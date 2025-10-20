from django.contrib import admin
from .models import Pago

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('socio', 'plan', 'monto', 'forma_pago', 'estado', 'fecha_pago')
    list_filter = ('estado', 'forma_pago', 'fecha_pago')
    search_fields = ('socio__nombre', 'socio__rut', 'plan__nombre')
