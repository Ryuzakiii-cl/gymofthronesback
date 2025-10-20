from django.db import models


# Evitamos import directo al cargar modelos para no crear ciclos
# - Profesor: users.Usuario
# - Socio: clientes.Socio

class Clase(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    profesor = models.ForeignKey('users.Usuario', on_delete=models.PROTECT, limit_choices_to={'rol': 'profesor'})
    cupos = models.PositiveIntegerField(default=10)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return f"{self.nombre} - {self.fecha} {self.hora_inicio}-{self.hora_fin}"

    def inscritos_count(self):
        return self.inscripciones.filter(estado='inscrito').count()


class InscripcionClase(models.Model):
    ESTADO = (
        ('inscrito', 'Inscrito'),
        ('cancelado', 'Cancelado'),
    )
    socio = models.ForeignKey('clientes.Socio', on_delete=models.CASCADE, related_name='inscripciones_clase')
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, related_name='inscripciones')
    estado = models.CharField(max_length=10, choices=ESTADO, default='inscrito')
    fec_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('socio', 'clase')
        ordering = ['-fec_registro']

    def __str__(self):
        return f"{self.socio} -> {self.clase} ({self.estado})"


class Cancha(models.Model):
    TIPO = (
        ('basket', 'Básquetbol'),
        ('volley', 'Vóleibol'),
        ('futbol', 'Fútbol Sala'),
        ('tenis', 'Tenis'),
        ('otro', 'Otro'),
    )
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO, default='otro')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Reserva(models.Model):
    socio = models.ForeignKey('clientes.Socio', on_delete=models.CASCADE, related_name='reservas')
    cancha = models.ForeignKey('Cancha', on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=15,
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmada', 'Confirmada'),
            ('cancelada', 'Cancelada'),
        ],
        default='pendiente'
    )
    fec_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cancha', 'fecha', 'hora_inicio')
        ordering = ['-fecha', 'hora_inicio']

    def __str__(self):
        return f"{self.cancha.nombre} - {self.fecha} ({self.hora_inicio}-{self.hora_fin})"

    @property
    def title(self):
        return f"{self.socio.nombre} ({self.cancha.nombre})"


# =============== NUEVO: CLASE RECURRENTE (para generar "todos los días") ===============

class ClaseRecurrente(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Spinning, Yoga, Zumba")
    profesor = models.ForeignKey('users.Usuario', on_delete=models.PROTECT, limit_choices_to={'rol': 'profesor'})
    cupos = models.PositiveIntegerField(default=10)

    # Horarios (en punto). Valida en admin que sean :00
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    # Rango de fechas para generar
    fec_inicio = models.DateField()
    fec_fin = models.DateField()

    # Por ahora, todos los días
    repetir_diario = models.BooleanField(default=True)

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Clase Recurrente"
        verbose_name_plural = "Clases Recurrentes"
        ordering = ['-fec_inicio', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.fec_inicio} → {self.fec_fin})"



# Evitamos import directo para no crear ciclos
# - Profesor: users.Usuario
# - Socio: clientes.Socio

class Clase(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    profesor = models.ForeignKey('users.Usuario', on_delete=models.PROTECT, limit_choices_to={'rol': 'profesor'})
    cupos = models.PositiveIntegerField(default=10)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return f"{self.nombre} - {self.fecha} {self.hora_inicio}-{self.hora_fin}"

    def inscritos_count(self):
        return self.inscripciones.filter(estado='inscrito').count()


class InscripcionClase(models.Model):
    ESTADO = (
        ('inscrito', 'Inscrito'),
        ('cancelado', 'Cancelado'),
    )
    ASISTENCIA = (
        ('pendiente', 'Pendiente'),
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
    )
    socio = models.ForeignKey('clientes.Socio', on_delete=models.CASCADE, related_name='inscripciones_clase')
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, related_name='inscripciones')
    estado = models.CharField(max_length=10, choices=ESTADO, default='inscrito')
    asistencia = models.CharField(max_length=10, choices=ASISTENCIA, default='pendiente')
    fec_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('socio', 'clase')
        ordering = ['-fec_registro']

    def __str__(self):
        return f"{self.socio} -> {self.clase} ({self.estado})"


class Cancha(models.Model):
    TIPO = (
        ('basket', 'Básquetbol'),
        ('volley', 'Vóleibol'),
        ('futbol', 'Fútbol Sala'),
        ('tenis', 'Tenis'),
        ('otro', 'Otro'),
    )
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO, default='otro')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Reserva(models.Model):
    socio = models.ForeignKey('clientes.Socio', on_delete=models.CASCADE, related_name='reservas')
    cancha = models.ForeignKey('Cancha', on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=15,
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmada', 'Confirmada'),
            ('cancelada', 'Cancelada'),
        ],
        default='pendiente'
    )
    fec_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cancha', 'fecha', 'hora_inicio')
        ordering = ['-fecha', 'hora_inicio']

    def __str__(self):
        return f"{self.cancha.nombre} - {self.fecha} ({self.hora_inicio}-{self.hora_fin})"

    @property
    def title(self):
        return f"{self.socio.nombre} ({self.cancha.nombre})"
