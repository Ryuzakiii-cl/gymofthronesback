from django.db import models
from django.utils import timezone

class Socio(models.Model):
    ESTADO_CHOICES = [
        (True, 'Activo'),
        (False, 'Inactivo'),
    ]

    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50, blank=True, null=True)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecNac = models.DateField(verbose_name='Fecha de Nacimiento', null=True, blank=True)
    estado = models.BooleanField(choices=ESTADO_CHOICES, default=True)
    fec_registro = models.DateTimeField(default=timezone.now)

    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Peso en kilogramos")
    altura = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Altura en metros")

    objetivos_choices = [
        ('bajar_peso', 'Bajar de peso'),
        ('subir_masa', 'Subir masa muscular'),
        ('bajar_grasa', 'Reducir grasa corporal'),
        ('mantener', 'Mantener condición física'),
        ('aumentar_fuerza', 'Aumentar fuerza'),
        ('tonificar', 'Tonificar / Definir'),
    ]
    objetivo = models.CharField(max_length=40, choices=objetivos_choices, default='mantener')

    profesor_asignado = models.ForeignKey(
        'users.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'profesor'},
        related_name='alumnos_asignados',
        help_text="Profesor asignado a este socio"
    )

    @property
    def imc(self):
        """Calcula el IMC si hay peso y altura disponibles."""
        if self.peso and self.altura and self.altura > 0:
            return round(self.peso / (self.altura ** 2), 2)
        return None

    @property
    def plan_nombre(self):
        """Devuelve el nombre del plan activo."""
        hoy = timezone.localdate()
        plan_activo = self.planes_asignados.filter(
            estado=True,
            fecFin__gte=hoy
        ).order_by('-fecFin').first()
        return plan_activo.plan.nombre if plan_activo else "Sin plan"

    @property
    def plan_vigencia(self):
        """Devuelve la vigencia del plan activo."""
        hoy = timezone.localdate()
        plan_activo = self.planes_asignados.filter(
            estado=True,
            fecFin__gte=hoy
        ).order_by('-fecFin').first()
        return plan_activo.fecFin.strftime('%d/%m/%Y') if plan_activo else "-"

    def __str__(self):
        estado = 'Activo' if self.estado else 'Inactivo'
        return f"{self.nombre} {self.apellido_paterno} ({estado})"
