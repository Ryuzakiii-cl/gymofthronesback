from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pagos, name='lista_pagos'),
    path('nuevo/', views.crear_pago, name='crear_pago'),
    path('editar/<int:pago_id>/', views.editar_pago, name='editar_pago'),
    path('eliminar/<int:pago_id>/', views.eliminar_pago, name='eliminar_pago'),
    path('mis-pagos/', views.pagos_socio, name='pagos_socio'),

]
