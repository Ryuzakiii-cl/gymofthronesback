from django.urls import path
from . import views

urlpatterns = [
    # 👨‍🏫 PROFESOR - ALUMNOS
    path('profesor/alumnos/', views.mis_alumnos, name='mis_alumnos'),
    path('profesor/generar/<int:socio_id>/', views.generar_rutina_automatica, name='generar_rutina_automatica'),

    # 📋 LISTA DE RUTINAS (vista temporal)
    path('profesor/rutinas/', views.lista_rutinas, name='lista_rutinas'),
    path('plantillas/<int:id>/editar/', views.editar_rutina, name='editar_rutina'),
    path('plantillas/<int:rutina_id>/eliminar/', views.eliminar_rutina, name='eliminar_rutina'),


    # ➕ placeholders para evitar errores
    path('profesor/rutinas/crear/', views.crear_rutina, name='crear_rutina'),
    path('profesor/rutinas/<int:rutina_id>/', views.ver_rutina, name='ver_rutina'),
    path('socio/mis-rutinas/', views.mis_rutinas_socio, name='mis_rutinas_socio'),
]
