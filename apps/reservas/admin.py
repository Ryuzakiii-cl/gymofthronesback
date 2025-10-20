from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from datetime import timedelta, time

from .models import Clase, InscripcionClase, Cancha, Reserva, ClaseRecurrente

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'profesor', 'fecha', 'hora_inicio', 'hora_fin', 'cupos', 'activo')
    list_filter = ('activo', 'profesor', 'fecha')
    search_fields = ('nombre', 'profesor__nombre')
    ordering = ('-fecha', 'hora_inicio')


@admin.register(InscripcionClase)
class InscripcionClaseAdmin(admin.ModelAdmin):
    list_display = ('socio', 'clase', 'estado', 'fec_registro')
    list_filter = ('estado',)
    search_fields = ('socio__nombre', 'clase__nombre')
    ordering = ('-fec_registro',)


@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('cancha', 'socio', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'cancha', 'fecha')
    search_fields = ('cancha__nombre', 'socio__nombre')
    ordering = ('-fecha', 'hora_inicio')


@admin.register(ClaseRecurrente)
class ClaseRecurrenteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'profesor', 'hora_inicio', 'hora_fin', 'fec_inicio', 'fec_fin', 'repetir_diario', 'activo')
    list_filter = ('repetir_diario', 'activo', 'profesor')
    search_fields = ('nombre', 'profesor__nombre')
    ordering = ('-fec_inicio', 'nombre')

    def save_model(self, request, obj, form, change):
        """
        Al guardar una ClaseRecurrente, generar instancias Clase para cada día del rango.
        Valida que las horas sean en punto (:00) y evita duplicados.
        """
        super().save_model(request, obj, form, change)

        # Validar horas en punto
        if obj.hora_inicio.minute != 0 or obj.hora_fin.minute != 0:
            messages.error(request, _("Las horas deben ser en punto (minutos 00). No se generaron clases."))
            return

        if obj.fec_fin < obj.fec_inicio:
            messages.error(request, _("La fecha fin no puede ser anterior a la fecha inicio."))
            return

        if not obj.repetir_diario:
            messages.warning(request, _("Por ahora solo generamos 'todos los días'. Active 'repetir_diario'."))
            return

        # Generar clases diarias
        desde = obj.fec_inicio
        hasta = obj.fec_fin
        creadas = 0
        actuales = 0

        from .models import Clase  # import local

        while desde <= hasta:
            # Evitar duplicados exactos para ese día/hora/profesor/nombre
            clase, created = Clase.objects.get_or_create(
                nombre=obj.nombre,
                profesor=obj.profesor,
                fecha=desde,
                hora_inicio=obj.hora_inicio,
                defaults={
                    'hora_fin': obj.hora_fin,
                    'cupos': obj.cupos,
                    'descripcion': 'Generada automáticamente desde Clase Recurrente',
                    'activo': obj.activo
                }
            )
            if created:
                creadas += 1
            else:
                actuales += 1
            desde += timedelta(days=1)

        messages.success(request, _(f"Clases generadas: {creadas}. Ya existentes: {actuales}."))
