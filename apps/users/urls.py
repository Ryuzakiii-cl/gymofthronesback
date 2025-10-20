from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/superadmin/', views.dashboard_superadmin, name='dashboard_superadmin'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/profesor/', views.dashboard_profesor, name='dashboard_profesor'),
    path('dashboard/socio/', views.dashboard_socio, name='dashboard_socio'),
]
