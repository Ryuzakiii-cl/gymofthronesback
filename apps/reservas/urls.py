from django.urls import path
from . import views

urlpatterns = [

    # ============================================================
    # 🧩 TALLERES (CRUD CLÁSICO)
    # ============================================================
    path('talleres/lista/', views.taller_list, name='taller_list'),
    path('talleres/nuevo/', views.taller_form, name='taller_crear'),
    path('talleres/editar/<int:taller_id>/', views.taller_form, name='taller_editar'),
    path('talleres/eliminar/<int:taller_id>/', views.taller_eliminar, name='taller_eliminar'),
    path('talleres/inscribir/<int:taller_id>/', views.inscribir_socio_taller, name='inscribir_socio_taller'),
    path('talleres/profesor/', views.talleres_profesor, name='talleres_profesor'),

    # ============================================================
    # ⚽ CANCHAS (CRUD CLÁSICO)
    # ============================================================
    path('canchas/', views.canchas_list, name='canchas_list'),
    path('canchas/nueva/', views.cancha_form, name='cancha_crear'),
    path('canchas/editar/<int:cancha_id>/', views.cancha_form, name='cancha_editar'),
    path('canchas/eliminar/<int:cancha_id>/', views.eliminar_cancha, name='eliminar_cancha'),

    # ============================================================
    # 📅 RESERVAS DE CANCHAS (LISTA + FORMULARIOS)
    # ============================================================
    path('reservas/', views.reservas_cancha_list, name='reservas_cancha_list'),
    path('reservas/nueva/', views.reserva_cancha_form, name='reserva_cancha_crear'),
    path('reservas/editar/<int:reserva_id>/', views.reserva_cancha_form, name='reserva_cancha_editar'),
    path('reservas/cancelar/<int:reserva_id>/', views.reserva_cancha_cancelar, name='reserva_cancha_cancelar'),

    # ============================================================
    # 🗓️ CALENDARIOS (VISTAS PRINCIPALES)
    # ============================================================
    path('calendario/canchas/', views.calendario_canchas, name='calendario_canchas'),
    path('calendario/talleres/', views.calendario_talleres, name='calendario_talleres'),

    # ============================================================
    # 📤 EVENTOS JSON (FullCalendar)
    # ============================================================
    path('calendario/eventos-canchas/', views.eventos_canchas_json, name='eventos_canchas_json'),
    path('calendario/eventos-talleres/', views.eventos_talleres_json, name='eventos_talleres_json'),

    # ============================================================
    # ⚙️ API AJAX - TALLERES
    # ============================================================
    path('api/talleres/', views.api_talleres, name='api_talleres'),
    path('api/talleres/crear/', views.api_crear_taller, name='api_crear_taller'),
    path('api/talleres/<int:taller_id>/', views.api_detalle_taller, name='api_detalle_taller'),
    path('api/talleres/<int:taller_id>/editar/', views.api_editar_taller, name='api_editar_taller'),
    path('api/talleres/<int:taller_id>/eliminar/', views.api_eliminar_taller, name='api_eliminar_taller'),
    path('api/talleres/<int:taller_id>/inscribir/', views.api_inscribir_socio, name='api_inscribir_taller'),

    # ============================================================
    # ⚙️ API AJAX - INSCRIPCIONES A TALLERES
    # ============================================================
    path('api/inscripciones/<int:insc_id>/asistencia/', views.api_cambiar_asistencia, name='api_cambiar_asistencia'),
    path('api/inscripciones/<int:insc_id>/eliminar/', views.api_eliminar_inscripcion, name='api_eliminar_inscripcion'),

    # ============================================================
    # ⚙️ API AJAX - RESERVAS DE CANCHAS
    # ============================================================
# ---------- API AJAX (canchas) ----------
    path('api/reservas/crear/', views.crear_reserva_ajax, name='crear_reserva_ajax'),
    path('editar/<int:reserva_id>/', views.editar_reserva_ajax, name='editar_reserva_ajax'),
    path('eliminar/<int:reserva_id>/', views.eliminar_reserva_ajax, name='eliminar_reserva_ajax'),

]


