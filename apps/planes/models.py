from django.db import models


class Plan(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.PositiveIntegerField(help_text="Duración en días")

    # 🔹 Nuevos campos: control de acceso
    puede_reservar_clases = models.BooleanField(default=False)
    puede_reservar_canchas = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre



class PlanBeneficio(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='beneficios')
    descripcion = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.plan.nombre}: {self.descripcion}"

class SocioPlan(models.Model):
    ESTADO_CHOICES = [
        (True, 'Activo'),
        (False, 'Inactivo'),
    ]

    socio = models.ForeignKey('clientes.Socio', on_delete=models.CASCADE, related_name='planes_asignados')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    fecInicio = models.DateField()
    fecFin = models.DateField()
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(choices=ESTADO_CHOICES, default=True)

    def __str__(self):
        return f"{self.socio.nombre} - {self.plan.nombre} ({'Activo' if self.estado else 'Inactivo'})"