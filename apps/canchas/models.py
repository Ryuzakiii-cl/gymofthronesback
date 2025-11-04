from django.db import models
from django.utils import timezone

# =========================================
#   CANCHAS
# =========================================

class Cancha(models.Model):
    TIPO = (
        ('basket', 'Básquetbol'),
        ('volley', 'Vóleibol'),
        ('futbol', 'Fútbol'),
        ('tenis', 'Tenis'),
    )

    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO, default='futbol')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = "Cancha"
        verbose_name_plural = "Canchas"

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


# =========================================
#   RESERVAS
# =========================================

class Reserva(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    )

    socio = models.ForeignKey(
        'socios.Socio',
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    cancha = models.ForeignKey(
        Cancha,
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    fec_registro = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('cancha', 'fecha', 'hora_inicio')
        ordering = ['-fecha', 'hora_inicio']
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def __str__(self):
        return f"{self.cancha.nombre} - {self.fecha} ({self.hora_inicio}-{self.hora_fin})"

    @property
    def title(self):
        """Usado por FullCalendar (muestra el socio y la cancha)."""
        return f"{self.socio.nombre} ({self.cancha.nombre})"
