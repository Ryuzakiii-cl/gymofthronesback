from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf.urls import handler404
from apps.users import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 Login, dashboard y usuarios
    path('users/', include('apps.users.urls')),  # todas las rutas del módulo users

    # 🌐 Redirección inicial
    path('', lambda request: redirect('login')),

    # 📦 Otros módulos
    path('canchas/', include('apps.canchas.urls')),
    path('calendario/', include('apps.calendario.urls')),
    path('planes/', include('apps.planes.urls')),
    path('pagos/', include('apps.pagos.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('socios/', include('apps.socios.urls')),
    path('talleres/', include('apps.talleres.urls')),
]

# 👉 Página de error 404 personalizada
handler404 = 'apps.users.views.error_404'
