from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf.urls import handler404
from apps.users import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),  
    path('', lambda request: redirect('login')),
    path('canchas/', include('apps.canchas.urls')),
    path('calendario/', include('apps.calendario.urls')),
    path('planes/', include('apps.planes.urls')),
    path('pagos/', include('apps.pagos.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('socios/', include('apps.socios.urls')),
    path('talleres/', include('apps.talleres.urls')),
    path('rutinas/', include('apps.rutinas.urls')), 
]

handler404 = 'apps.users.views.error_404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)