from django.db import models
from apps.socios.models import Socio
from apps.planes.models import Plan, SocioPlan

class Pago(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
    ]

    FORMA_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]

    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='pagos')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    socio_plan = models.ForeignKey(SocioPlan, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_pago = models.DateField(auto_now_add=True)
    monto = models.IntegerField(("Monto"))
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_CHOICES)
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"{self.socio.nombre} - {self.plan.nombre if self.plan else 'Sin plan'} - ${self.monto} ({self.get_estado_display()})"
