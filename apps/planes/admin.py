from django.contrib import admin
from .models import Plan, PlanBeneficio, SocioPlan

# 🔹 Beneficios en línea dentro del plan
class PlanBeneficioInline(admin.TabularInline):
    model = PlanBeneficio
    extra = 1


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion', 'puede_reservar_clases', 'puede_reservar_canchas')
    list_filter = ('puede_reservar_clases', 'puede_reservar_canchas')
    search_fields = ('nombre',)
    ordering = ('nombre',)
    inlines = [PlanBeneficioInline]  #aquí lo integramos correctamente


@admin.register(PlanBeneficio)
class PlanBeneficioAdmin(admin.ModelAdmin):
    list_display = ('plan', 'descripcion')
    search_fields = ('plan__nombre', 'descripcion')
    ordering = ('plan',)


@admin.register(SocioPlan)
class SocioPlanAdmin(admin.ModelAdmin):
    list_display = ('socio', 'plan', 'fecInicio', 'fecFin', 'estado')
    list_filter = ('estado', 'plan')
    search_fields = ('socio__nombre', 'plan__nombre')
    ordering = ('-fecInicio',)

