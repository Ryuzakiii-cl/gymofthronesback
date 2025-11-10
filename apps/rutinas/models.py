from django.db import models
from django.utils import timezone
from django.conf import settings
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


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

    titulo = models.CharField(max_length=100, help_text="Ejemplo: Rutina fuerza y resistencia - Semana 1")
    descripcion = models.TextField(help_text="Descripción general de los objetivos de esta rutina.", blank=True, null=True)
    contenido = models.TextField(help_text="Detalle completo de la rutina: ejercicios, repeticiones, descansos, observaciones.")
    imc_referencia = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
                                         help_text="IMC del socio al momento de crear la rutina (para referencia o automatización futura).")
    archivo_pdf = models.FileField(upload_to='rutinas/pdf/', blank=True, null=True, help_text="Archivo PDF generado automáticamente.")
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activa')

    class Meta:
        ordering = ['-fecha_asignacion']
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"
        unique_together = ('profesor', 'socio', 'titulo')

    def __str__(self):
        return f"{self.titulo} → {self.socio.nombre} ({self.profesor.nombre})"

    def generar_pdf(self):
        """Genera un PDF con la rutina del socio."""

        carpeta = os.path.join(settings.MEDIA_ROOT, 'rutinas/pdf')
        os.makedirs(carpeta, exist_ok=True)
        nombre_pdf = f"rutina_{self.socio.rut}_{self.fecha_asignacion.strftime('%Y%m%d_%H%M')}.pdf"
        ruta_pdf = os.path.join(carpeta, nombre_pdf)

        c = canvas.Canvas(ruta_pdf, pagesize=A4)
        c.setTitle(self.titulo)
        c.drawString(50, 800, f"Rutina: {self.titulo}")
        c.drawString(50, 780, f"Profesor: {self.profesor.nombre} {self.profesor.apellido}")
        c.drawString(50, 760, f"Socio: {self.socio.nombre} {self.socio.apellido_paterno}")
        c.drawString(50, 740, f"IMC referencia: {self.imc_referencia}")
        c.drawString(50, 720, "--------------------------------------------")

        text_object = c.beginText(50, 700)
        for line in self.contenido.split('\n'):
            text_object.textLine(line)
        c.drawText(text_object)
        c.save()

        self.archivo_pdf.name = f"rutinas/pdf/{nombre_pdf}"
        self.save()


class RutinaBase(models.Model):
    objetivos_choices = [
        ('bajar_peso', 'Bajar de peso'),
        ('subir_masa', 'Subir masa muscular'),
        ('bajar_grasa', 'Reducir grasa corporal'),
        ('mantener', 'Mantener condición física'),
        ('aumentar_fuerza', 'Aumentar fuerza'),
        ('mejorar_resistencia', 'Mejorar resistencia / Cardio'),
        ('mejorar_flexibilidad', 'Mejorar flexibilidad / Movilidad'),
        ('rendimiento_deportivo', 'Mejorar rendimiento deportivo'),
        ('salud_bienestar', 'Salud y bienestar / Reducir estrés'),
        ('rehabilitacion', 'Rehabilitación / Recuperación de lesión'),
        ('tonificar', 'Tonificar / Definir'),
    ]

    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    objetivo = models.CharField(max_length=40, choices=objetivos_choices)
    imc_min = models.DecimalField(max_digits=5, decimal_places=2)
    imc_max = models.DecimalField(max_digits=5, decimal_places=2)
    contenido = models.TextField(help_text="Detalle de la rutina predefinida")

    def __str__(self):
        return f"{self.titulo} ({self.objetivo} - IMC {self.imc_min}-{self.imc_max})"
