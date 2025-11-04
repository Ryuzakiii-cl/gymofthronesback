from django.urls import path
from . import views

urlpatterns = [
    # ============================================================
    # ⚽ CANCHAS (CRUD CLÁSICO)
    # ============================================================
    path('', views.canchas_list, name='canchas_list'),
    path('nueva/', views.cancha_form, name='cancha_crear'),
    path('editar/<int:cancha_id>/', views.cancha_form, name='cancha_editar'),
    path('eliminar/<int:cancha_id>/', views.eliminar_cancha, name='eliminar_cancha'),

    # ============================================================
    # 📅 RESERVAS DE CANCHAS
    # ============================================================
    path('reservas/', views.reservas_cancha_list, name='reservas_cancha_list'),
    path('reservas/nueva/', views.reserva_cancha_form, name='reserva_cancha_crear'),
    path('reservas/editar/<int:reserva_id>/', views.reserva_cancha_form, name='reserva_cancha_editar'), 
    path('reservas/cancelar/<int:reserva_id>/', views.reserva_cancha_cancelar, name='reserva_cancha_cancelar'),

    # ============================================================
    # ⚙️ API AJAX - RESERVAS (CRUD desde modal)
    # ============================================================

    path('api/reservas/crear/', views.crear_reserva_ajax, name='crear_reserva_ajax'),
    path('api/reservas/editar/<int:reserva_id>/', views.editar_reserva_ajax, name='editar_reserva_ajax'),
    path('api/reservas/eliminar/<int:reserva_id>/', views.eliminar_reserva_ajax, name='eliminar_reserva_ajax'),

]
