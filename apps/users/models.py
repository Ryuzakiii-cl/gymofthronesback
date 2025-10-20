from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    def create_user(self, rut, password=None, **extra_fields):
        if not rut:
            raise ValueError('El RUT es obligatorio')
        rut = rut.replace('.', '').replace('-', '')  # Normaliza el formato
        user = self.model(rut=rut, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'superadmin')
        return self.create_user(rut, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = [
        ('superadmin', 'Super Administrador'),
        ('admin', 'Administrador'),
        ('profesor', 'Profesor'),
        ('socio', 'Socio'),
    ]

    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=15, choices=ROLES, default='socio')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    objects = UsuarioManager()

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'correo']

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.get_rol_display()})"
