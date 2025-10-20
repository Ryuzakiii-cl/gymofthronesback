from django.urls import path
from . import views

urlpatterns = [
    # Clases (CRUD clásico opcional)
    path('clases/', views.clases_list, name='clases_list'),
    path('clases/nueva/', views.clase_form, name='clase_crear'),
    path('clases/editar/<int:clase_id>/', views.clase_form, name='clase_editar'),
    path('clases/eliminar/<int:clase_id>/', views.clase_eliminar, name='clase_eliminar'),
    path('clases/inscribir/<int:clase_id>/', views.inscribir_socio_clase, name='inscribir_socio_clase'),
    path('clases/profesor/', views.clases_profesor, name='clases_profesor'),

    # Canchas y reservas (ya existentes)
    path('canchas/', views.canchas_list, name='canchas_list'),
    path('canchas/nueva/', views.cancha_form, name='cancha_crear'),
    path('canchas/editar/<int:cancha_id>/', views.cancha_form, name='cancha_editar'),

    path('', views.reservas_cancha_list, name='reservas_cancha_list'),
    path('reservas/nueva/', views.reserva_cancha_form, name='reserva_cancha_crear'),
    path('reservas/editar/<int:reserva_id>/', views.reserva_cancha_form, name='reserva_cancha_editar'),
    path('reservas/cancelar/<int:reserva_id>/', views.reserva_cancha_cancelar, name='reserva_cancha_cancelar'),

    # Calendarios
    path('calendario/canchas/', views.calendario, name='calendario_canchas'),
    path('calendario/clases/', views.calendario_clases, name='calendario_clases'),

    # APIs FullCalendar (canchas ya existía)
    path('calendario/eventos-clases/', views.eventos_clases_json, name='eventos_clases_json'),

    # APIs Clases (AJAX)
    path('api/clases/', views.api_clases, name='api_clases'),
    path('api/clases/crear/', views.api_crear_clase, name='api_crear_clase'),
    path('api/clases/<int:clase_id>/', views.api_detalle_clase, name='api_detalle_clase'),
    path('api/clases/<int:clase_id>/eliminar/', views.api_eliminar_clase, name='api_eliminar_clase'),
    path('api/clases/<int:clase_id>/inscribir/', views.api_inscribir_socio, name='api_inscribir_socio'),
    path('api/inscripciones/<int:insc_id>/asistencia/', views.api_cambiar_asistencia, name='api_cambiar_asistencia'),
    path('api/inscripciones/<int:insc_id>/eliminar/', views.api_eliminar_inscripcion, name='api_eliminar_inscripcion'),
]
