import json
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.serializers.json import DjangoJSONEncoder

from apps.users.models import Usuario
from apps.socios.models import Socio
from apps.canchas.models import Cancha, Reserva
from apps.talleres.models import Taller


# ============================
#   HELPERS DE PERMISOS
# ============================

def es_admin_superadmin_profesor(user):
    """Admin / Superadmin / Profesor."""
    return user.is_authenticated and getattr(user, 'rol', None) in ['admin', 'superadmin', 'profesor']


def es_admin_superadmin_profesor_socio(user):
    """Admin / Superadmin / Profesor / Socio."""
    return user.is_authenticated and getattr(user, 'rol', None) in ['admin', 'superadmin', 'profesor', 'socio']


# ============================
#   CALENDARIO CANCHAS
# ============================

@login_required
@user_passes_test(es_admin_superadmin_profesor_socio)
def calendario_canchas(request):
    socios = Socio.objects.filter(estado=True).order_by('nombre', 'apellido_paterno')
    canchas = Cancha.objects.filter(activo=True).order_by('nombre')

    context = {'socios': socios, 'canchas': canchas}
    return render(request, 'calendario/calendario_canchas.html', context)


# ============================
#   CALENDARIO TALLERES
# ============================

# ============================
#   CALENDARIO TALLERES
# ============================

@login_required
@user_passes_test(es_admin_superadmin_profesor_socio)  # 👈 ahora también puede entrar el socio
def calendario_talleres(request):
    profesores = list(
        Usuario.objects.filter(rol='profesor').values('id', 'nombre', 'apellido')
    )
    socios = list(
        Socio.objects.filter(estado=True).values('id', 'nombre', 'apellido_paterno')
    )

    return render(request, 'calendario/calendario_talleres.html', {
        'profesores': json.dumps(profesores, cls=DjangoJSONEncoder),
        'socios': json.dumps(socios, cls=DjangoJSONEncoder),
    })



# ============================
#   EVENTOS CANCHAS (JSON)
# ============================

@login_required
def eventos_canchas_json(request):
    eventos = []
    rol = getattr(request.user, 'rol', None)

    # 🔹 SOCIO AHORA VE TODAS LAS RESERVAS, NO SOLO LAS SUYAS
    if rol == 'socio':
        reservas = Reserva.objects.filter(
            estado='confirmada'
        ).select_related('cancha', 'socio')   # 👈 AQUÍ SE QUITÓ EL FILTRO DEL RUT
    else:
        # Admin / Superadmin / Profesor → todas las reservas
        reservas = Reserva.objects.filter(
            estado='confirmada'
        ).select_related('cancha', 'socio')

    for r in reservas:
        eventos.append({
            "id": r.id,
            "title": f"{r.cancha.nombre} - {r.socio.nombre}",
            "start": f"{r.fecha}T{r.hora_inicio}",
            "end": f"{r.fecha}T{r.hora_fin}",
            "color": "#ffc107",
            "extendedProps": {
                "id": r.id,
                "socio_id": r.socio.id,
                "cancha_id": r.cancha.id,
                "hora_inicio": str(r.hora_inicio),
                "hora_fin": str(r.hora_fin),
            },
        })

    return JsonResponse(eventos, safe=False)



# ============================
#   EVENTOS TALLERES (JSON)
# ============================

@login_required
def eventos_talleres_json(request):
    eventos = []
    for taller in Taller.objects.filter(activo=True):
        eventos.append({
            "id": taller.id_taller,
            "title": taller.nombre,
            "start": f"{taller.fecha}T{taller.hora_inicio}",
            "end": f"{taller.fecha}T{taller.hora_fin}",
            "color": "#007bff",
            "extendedProps": {
                "profesor": f"{taller.profesor.nombre} {getattr(taller.profesor, 'apellido', '')}".strip(),
                "cupos": taller.cupos,
                "inscritos": taller.inscritos_count(),
            },
        })
    return JsonResponse(eventos, safe=False)
