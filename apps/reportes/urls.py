from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard_reportes'),
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),
]
