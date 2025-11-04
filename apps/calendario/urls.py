from django.urls import path
from . import views

urlpatterns = [
    # ============================================================
    # 🗓️ CALENDARIOS (VISTAS PRINCIPALES)
    # ============================================================
    path('canchas/', views.calendario_canchas, name='calendario_canchas'),
    path('talleres/', views.calendario_talleres, name='calendario_talleres'),

    # ============================================================
    # 📤 EVENTOS JSON (FullCalendar)
    # ============================================================
    path('eventos/canchas/', views.eventos_canchas_json, name='eventos_canchas_json'),
    path('eventos/talleres/', views.eventos_talleres_json, name='eventos_talleres_json'),
]
