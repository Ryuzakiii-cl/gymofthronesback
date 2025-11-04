from django.contrib import admin
from .models import Cancha, Reserva


# ============ CANCHAS ============

@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre',)
    ordering = ('nombre',)
    list_per_page = 20


# ============ RESERVAS ============

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('socio', 'cancha', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'cancha', 'fecha')
    search_fields = ('socio__nombre', 'cancha__nombre')
    ordering = ('-fecha', 'hora_inicio')
    list_per_page = 20
