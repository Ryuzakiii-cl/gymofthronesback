"""
URL configuration for gymofthronesback project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls import handler404
from apps.users import views
urlpatterns = [
    path('admin/', admin.site.urls),

    # Apps principales
    path('', include('apps.users.urls')),
    path('', lambda request: redirect('login')),
    path('users/', include('apps.users.urls')), #login/logout del dashboard
    path('logout/', views.logout_view, name='logout'),
    path('canchas/', include('apps.canchas.urls')),
    path('calendario/', include('apps.calendario.urls')),
    path('planes/', include('apps.planes.urls')),
    path('pagos/', include('apps.pagos.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('socios/', include('apps.socios.urls')),
    path('talleres/', include('apps.talleres.urls')),
]

# 👉 Si el usuario ingresa una ruta que no existe lo manda al 404
handler404 = 'apps.users.views.error_404'