from django.db import models
from django.utils import timezone
from django.conf import settings
import os
import json

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4


class Rutina(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
    ]

    profesor = models.ForeignKey(
        'users.Usuario',
        on_delete=models.PROTECT,
        limit_choices_to={'rol': 'profesor'},
        related_name='rutinas_asignadas'
    )

    socio = models.ForeignKey(
        'socios.Socio',
        on_delete=models.CASCADE,
        related_name='rutinas_recibidas'
    )

    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    contenido = models.TextField()
    imc_referencia = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    archivo_pdf = models.FileField(upload_to='rutinas/pdf/', blank=True, null=True)
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activa')

    class Meta:
        ordering = ['-fecha_asignacion']
        unique_together = ('profesor', 'socio', 'titulo')

    def __str__(self):
        return f"{self.titulo} → {self.socio.nombre} ({self.profesor.nombre})"


    # ---------------------------------------------------
    # ⭐⭐⭐ MÉTODO CORRECTO: generar_pdf dentro de la clase ⭐⭐⭐
    # ---------------------------------------------------
    def generar_pdf(self):
        """Genera un PDF profesional con semanas, días y ejercicios en tablas estilo Gym Of Thrones."""

        carpeta = os.path.join(settings.MEDIA_ROOT, 'rutinas/pdf')
        os.makedirs(carpeta, exist_ok=True)

        nombre_pdf = f"rutina_{self.socio.rut}_{self.fecha_asignacion.strftime('%Y%m%d_%H%M')}.pdf"
        ruta_pdf = os.path.join(carpeta, nombre_pdf)

        doc = SimpleDocTemplate(ruta_pdf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        story = []

        # ENCABEZADO
        story.append(Paragraph(f"<b>Rutina: {self.titulo}</b>", styles['Title']))
        story.append(Paragraph(f"Profesor: {self.profesor.nombre} {self.profesor.apellido}", styles['Normal']))
        story.append(Paragraph(f"Socio: {self.socio.nombre} {self.socio.apellido_paterno}", styles['Normal']))
        story.append(Paragraph(f"IMC referencia: {self.imc_referencia}", styles['Normal']))
        story.append(Spacer(1, 12))

        # JSON
        try:
            data = json.loads(self.contenido)
        except Exception as e:
            story.append(Paragraph("<b>ERROR:</b> Contenido JSON inválido", styles['Normal']))
            story.append(Paragraph(str(e), styles['Normal']))
            doc.build(story)
            self.archivo_pdf.name = f"rutinas/pdf/{nombre_pdf}"
            self.save()
            return

        negro = colors.black
        amarillo = colors.HexColor("#FFC300")

        # SEMANAS
        for semana_key in sorted(data.keys()):
            n_sem = semana_key.replace("semana", "")

            story.append(Spacer(1, 12))
            story.append(Paragraph(
                f"<para backColor='black' textColor='#FFC300' alignment='center'><b>SEMANA {n_sem}</b></para>",
                styles["Heading2"]
            ))
            story.append(Spacer(1, 12))

            semana = data[semana_key]

            # DÍAS
            for dia_key in sorted(semana.keys()):
                n_dia = dia_key.replace("dia", "")

                story.append(Paragraph(f"<b>DÍA {n_dia}</b>", styles["Heading3"]))
                story.append(Spacer(1, 6))

                ejercicios = semana[dia_key]
                tabla_data = [["Ejercicio", "Series", "Reps", "Descanso"]]

                for item in ejercicios:
                    tabla_data.append([
                        item.get("ejercicio", "-"),
                        item.get("series", "-"),
                        item.get("reps", "-"),
                        item.get("descanso", "-")
                    ])

                tabla = Table(tabla_data, colWidths=[8*cm, 2*cm, 2*cm, 2*cm])
                tabla.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), negro),
                    ("TEXTCOLOR", (0,0), (-1,0), amarillo),
                    ("GRID", (0,0), (-1,-1), 1, negro),
                    ("ALIGN", (1,1), (-1,-1), "CENTER"),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ]))

                story.append(tabla)
                story.append(Spacer(1, 16))

        # EXPORTAR PDF
        doc.build(story)

        self.archivo_pdf.name = f"rutinas/pdf/{nombre_pdf}"
        self.save()


# ---------------------------------------------------
#  Rutina Base (OK)
# ---------------------------------------------------
class RutinaBase(models.Model):
    objetivos_choices = [
        ('bajar_peso', 'Bajar de peso'),
        ('subir_masa', 'Subir masa muscular'),
        ('bajar_grasa', 'Reducir grasa corporal'),
        ('mantener', 'Mantener condición física'),
        ('aumentar_fuerza', 'Aumentar fuerza'),
        ('tonificar', 'Tonificar / Definir'),
    ]

    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    objetivo = models.CharField(max_length=40, choices=objetivos_choices)
    imc_min = models.DecimalField(max_digits=5, decimal_places=2)
    imc_max = models.DecimalField(max_digits=5, decimal_places=2)
    contenido = models.TextField()

    def __str__(self):
        return f"{self.titulo} ({self.objetivo} - IMC {self.imc_min}-{self.imc_max})"
