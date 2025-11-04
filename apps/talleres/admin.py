from django.contrib import admin
from .models import Taller, InscripcionTaller


# ============ Talleres ============

@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'profesor', 'fecha', 'hora_inicio', 'hora_fin', 'cupos', 'activo')
    list_filter = ('activo', 'profesor', 'fecha')
    search_fields = ('nombre', 'profesor__nombre')
    ordering = ('fecha', 'hora_inicio')
    list_per_page = 20


# ============ Inscripciones ============

@admin.register(InscripcionTaller)
class InscripcionTallerAdmin(admin.ModelAdmin):
    list_display = ('socio', 'taller', 'estado', 'asistencia', 'fec_registro')
    list_filter = ('estado', 'asistencia')
    search_fields = ('socio__nombre', 'taller__nombre')
    date_hierarchy = 'fec_registro'
    list_per_page = 20
