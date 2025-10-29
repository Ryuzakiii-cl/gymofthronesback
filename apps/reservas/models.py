from django.db import models
from django.utils import timezone


# =========================================
#   TALLERES
# =========================================

# Representa un taller o clase dirigida por un profesor.
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

# Representa la inscripción de un socio a una clase.
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
        'clientes.Socio',
        on_delete=models.CASCADE,
        related_name='inscripciones_taller'
    )
    taller = models.ForeignKey(
        Taller,
        on_delete=models.CASCADE,
        related_name='inscripciones'
    )
    # ---------------------------------
    estado = models.CharField(max_length=10, choices=ESTADO, default='inscrito')
    asistencia = models.CharField(max_length=10, choices=ASISTENCIA, default='pendiente')
    fec_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('socio', 'taller')
        # ---------------------------------
        ordering = ['-fec_registro']
        verbose_name = "Inscripción a Taller"
        verbose_name_plural = "Inscripciones a Talleres"

    def __str__(self):

        return f"{self.socio} → {self.taller} ({self.estado})"
        # ---------------------------------


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
    tipo = models.CharField(max_length=20, choices=TIPO, default='otro')
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
        'clientes.Socio',
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
    

