# apps/planes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_planes, name='lista_planes'),
    path('nuevo/', views.crear_plan, name='crear_plan'),
    path('editar/<int:plan_id>/', views.editar_plan, name='editar_plan'),   # ← plan_id
    path('eliminar/<int:plan_id>/', views.eliminar_plan, name='eliminar_plan'),  # ← plan_id
]
