from django.urls import path
from . import views

urlpatterns = [
    # ============================================================
    # 🧩 TALLERES (CRUD CLÁSICO)
    # ============================================================
    path('lista/', views.taller_list, name='taller_list'),
    path('nuevo/', views.taller_form, name='taller_crear'),
    path('editar/<int:taller_id>/', views.taller_form, name='taller_editar'),
    path('eliminar/<int:taller_id>/', views.taller_eliminar, name='taller_eliminar'),


    # ============================================================
    # ⚙️ API AJAX - TALLERES
    # ============================================================
    path('api/crear/', views.api_crear_taller, name='api_crear_taller'),
    path('api/<int:taller_id>/', views.api_detalle_taller, name='api_detalle_taller'),
    path('api/<int:taller_id>/editar/', views.api_editar_taller, name='api_editar_taller'),
    path('api/<int:taller_id>/eliminar/', views.api_eliminar_taller, name='api_eliminar_taller'),

    # ============================================================
    # ⚙️ API AJAX - INSCRIPCIONES
    # ============================================================
    path('api/<int:taller_id>/inscribir/', views.api_inscribir_socio, name='api_inscribir_taller'),
    path('api/inscripciones/<int:insc_id>/asistencia/', views.api_cambiar_asistencia, name='api_cambiar_asistencia'),
    path('api/inscripciones/<int:insc_id>/eliminar/', views.api_eliminar_inscripcion, name='api_eliminar_inscripcion'),
    
]
