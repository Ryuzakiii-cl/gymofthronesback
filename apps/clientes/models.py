from django.db import models
from datetime import date


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
    fec_registro = models.DateTimeField(auto_now_add=True)

    @property
    def plan_actual(self):
        """Devuelve el plan activo del socio o 'Sin plan activo'"""
        plan_activo = self.planes_asignados.filter(
            estado=True,
            fecFin__gte=date.today()
        ).order_by('-fecFin').first()

        if plan_activo:
            dias_restantes = (plan_activo.fecFin - date.today()).days
            color_estado = "🟢" if dias_restantes > 0 else "🔴"
            return f"{plan_activo.plan.nombre} ({color_estado} Vigente hasta {plan_activo.fecFin.strftime('%d/%m/%Y')})"
        else:
            return "Sin plan activo"



    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} ({'Activo' if self.estado else 'Inactivo'})"


