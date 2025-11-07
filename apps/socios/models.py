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

    # 🔹 Propiedad para obtener el nombre del plan activo
    @property
    def plan_nombre(self):
        """Devuelve solo el nombre del plan activo"""
        hoy = timezone.localdate()
        plan_activo = self.planes_asignados.filter(
            estado=True,
            fecFin__gte=hoy
        ).order_by('-fecFin').first()
        if plan_activo:
            return plan_activo.plan.nombre
        return "Sin plan"

    # 🔹 Propiedad para obtener la vigencia del plan activo
    @property
    def plan_vigencia(self):
        """Devuelve la vigencia del plan activo"""
        hoy = timezone.localdate()
        plan_activo = self.planes_asignados.filter(
            estado=True,
            fecFin__gte=hoy
        ).order_by('-fecFin').first()
        if plan_activo:
            return plan_activo.fecFin.strftime('%d/%m/%Y')
        return "-"
    
    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} ({'Activo' if self.estado else 'Inactivo'})"
