from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Rutina, RutinaBase

@admin.register(Rutina)
class RutinaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'socio', 'profesor', 'fecha_asignacion', 'estado')
    list_filter = ('estado', 'fecha_asignacion', 'profesor')
    search_fields = ('titulo', 'socio__nombre', 'profesor__nombre')
    date_hierarchy = 'fecha_asignacion'
    ordering = ('-fecha_asignacion',)
    readonly_fields = ('archivo_pdf',)


@admin.register(RutinaBase)
class RutinaBaseAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'objetivo', 'imc_min', 'imc_max')
    search_fields = ('titulo', 'objetivo')
    list_filter = ('objetivo',)
