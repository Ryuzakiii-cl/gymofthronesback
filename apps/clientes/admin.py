from django.contrib import admin
from .models import Socio

@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'apellido_paterno', 'correo', 'telefono', 'estado')
    search_fields = ('rut', 'nombre', 'apellido_paterno', 'correo')
    list_filter = ('estado',)
