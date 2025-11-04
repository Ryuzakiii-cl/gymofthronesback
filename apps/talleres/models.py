from django.db import models

# =========================================
#   TALLERES
# =========================================

class Taller(models.Model):
    id_taller = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    profesor = models.ForeignKey(
        'users.Usuario',
        on_delete=models.PROTECT,
        limit_choices_to={'rol': 'profesor'},
        related_name='talleres_asignados'
    )
    cupos = models.PositiveIntegerField(default=10)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['fecha', 'hora_inicio']
        verbose_name = "Taller"
        verbose_name_plural = "Talleres"

    def __str__(self):
        return f"{self.nombre} - {self.fecha} {self.hora_inicio}-{self.hora_fin}"

    def inscritos_count(self):
        """Devuelve la cantidad de socios inscritos con estado activo."""
        return self.inscripciones.filter(estado='inscrito').count()


class InscripcionTaller(models.Model):
    ESTADO = (
        ('inscrito', 'Inscrito'),
        ('cancelado', 'Cancelado')
    )

    ASISTENCIA = (
        ('pendiente', 'Pendiente'),
        ('presente', 'Presente'),
        ('ausente', 'Ausente')
    )

    socio = models.ForeignKey(
        'socios.Socio',
        on_delete=models.CASCADE,
        related_name='inscripciones_taller'
    )
    taller = models.ForeignKey(
        Taller,
        on_delete=models.CASCADE,
        related_name='inscripciones'
    )
    estado = models.CharField(max_length=10, choices=ESTADO, default='inscrito')
    asistencia = models.CharField(max_length=10, choices=ASISTENCIA, default='pendiente')
    fec_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('socio', 'taller')
        ordering = ['-fec_registro']
        verbose_name = "Inscripción a Taller"
        verbose_name_plural = "Inscripciones a Talleres"

    def __str__(self):
        return f"{self.socio} → {self.taller} ({self.estado})"
