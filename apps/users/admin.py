from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('rut', 'nombre', 'apellido', 'correo', 'rol', 'is_active', 'is_staff')
    list_filter = ('rol', 'is_active', 'is_staff')
    search_fields = ('rut', 'nombre', 'apellido', 'correo')
    ordering = ('rut',)

    fieldsets = (
        (None, {'fields': ('rut', 'password')}),
        ('Información personal', {'fields': ('nombre', 'apellido', 'correo')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'fecha_creacion')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('rut', 'nombre', 'apellido', 'correo', 'rol', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )
