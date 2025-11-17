from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.users.models import Usuario
from apps.socios.models import Socio
from apps.planes.models import SocioPlan
from .models import Taller, InscripcionTaller


# ======================================================
#                HELPERS DE PERMISO
# ======================================================

def es_admin(user):
    return getattr(user, "rol", "") == "admin"

def es_superadmin(user):
    return getattr(user, "rol", "") == "superadmin"

def es_profesor(user):
    return getattr(user, "rol", "") == "profesor"

def es_socio(user):
    return getattr(user, "rol", "") == "socio"

def es_admin_o_superadmin(user):
    return es_admin(user) or es_superadmin(user)

def puede_gestionar_taller(user, taller):
    """Admin/Superadmin gestionan todos; profesor solo sus talleres."""
    if es_admin_o_superadmin(user):
        return True
    if es_profesor(user) and taller.profesor_id == user.id:
        return True
    return False


# ======================================================
#                CRUD DE TALLERES (Panel)
# ======================================================

@login_required
def taller_list(request):
    """
    Listado general solo visible para admin, superadmin y profesor.
    El socio debe usar el calendario.
    """
    if es_socio(request.user):
        return redirect('calendario_talleres')

    talleres = Taller.objects.all().order_by('fecha', 'hora_inicio')
    return render(request, 'talleres/talleres_list.html', {'talleres': talleres})


@login_required
@user_passes_test(lambda u: es_admin_o_superadmin(u) or es_profesor(u))
def taller_form(request, taller_id=None):
    """Crear o editar talleres desde el panel (no desde el calendario)."""
    profesores = Usuario.objects.filter(rol="profesor")
    taller = get_object_or_404(Taller, id_taller=taller_id) if taller_id else None

    if taller and not puede_gestionar_taller(request.user, taller):
        messages.error(request, "No puedes editar talleres que no son tuyos.")
        return redirect('taller_list')

    if request.method == "POST":

        nombre = request.POST.get("nombre")
        profesor_id = request.POST.get("profesor")
        cupos = int(request.POST.get("cupos"))
        fecha = request.POST.get("fecha")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")

        # Asigna profesor
        if es_profesor(request.user):
            profesor = request.user
        else:
            profesor = get_object_or_404(Usuario, id=profesor_id, rol="profesor")

        if taller:
            # EDITAR
            taller.nombre = nombre
            taller.profesor = profesor
            taller.cupos = cupos
            taller.fecha = fecha
            taller.hora_inicio = hora_inicio
            taller.hora_fin = hora_fin
            taller.save()
            messages.success(request, "Taller actualizado.")
        else:
            # CREAR
            Taller.objects.create(
                nombre=nombre,
                profesor=profesor,
                cupos=cupos,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                activo=True
            )
            messages.success(request, "Taller creado.")

        return redirect('taller_list')

    return render(request, 'talleres/taller_form.html', {
        'taller': taller,
        'profesores': profesores
    })


@login_required
def taller_eliminar(request, taller_id):
    """Elimina taller con permisos correctos."""
    taller = get_object_or_404(Taller, id_taller=taller_id)

    if not puede_gestionar_taller(request.user, taller):
        messages.error(request, "No puedes eliminar este taller.")
        return redirect('taller_list')

    taller.delete()
    messages.success(request, "Taller eliminado.")
    return redirect('taller_list')


# ======================================================
#                API CALENDARIO (AJAX)
# ======================================================

@login_required
@require_POST
def api_crear_taller(request):
    """Crear un taller desde el calendario."""
    user = request.user

    if es_socio(user):
        return JsonResponse({'ok': False, 'msg': 'Los socios no pueden crear talleres.'}, status=403)

    try:
        nombre = request.POST.get('nombre')
        cupos = int(request.POST.get('cupos'))
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        profesor_id = request.POST.get('profesor_id')

        if es_profesor(user):
            profesor = user
        else:
            profesor = get_object_or_404(Usuario, id=profesor_id, rol='profesor')

        nuevo = Taller.objects.create(
            nombre=nombre,
            profesor=profesor,
            cupos=cupos,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            activo=True
        )

        return JsonResponse({'ok': True, 'id': nuevo.id_taller})

    except Exception as e:
        return JsonResponse({'ok': False, 'msg': str(e)})


@login_required
def api_detalle_taller(request, taller_id):
    """Datos del taller para el modal de detalle."""
    taller = get_object_or_404(Taller, id_taller=taller_id)
    user = request.user

    inscritos = taller.inscripciones.filter(
        estado='inscrito'
    ).select_related('socio').values(
        'id', 'socio_id', 'socio__nombre', 'socio__apellido_paterno', 'asistencia'
    )

    cupos_disp = taller.cupos - taller.inscritos_count()

    # socio: ¿está inscrito?
    mi_inscripcion = None
    if es_socio(user):
        mi = taller.inscripciones.filter(socio__rut=user.rut).first()
        if mi:
            mi_inscripcion = mi.id

    puede_gestionar = puede_gestionar_taller(user, taller)

    data = {
        'id': taller.id_taller,
        'nombre': taller.nombre,
        'profesor_id': taller.profesor.id,
        'profesor': f"{taller.profesor.nombre} {getattr(taller.profesor, 'apellido', '')}",
        'cupos': taller.cupos,
        'inscritos': taller.inscritos_count(),
        'cupos_disponibles': cupos_disp,
        'fecha': taller.fecha.strftime('%Y-%m-%d'),
        'hora_inicio': taller.hora_inicio.strftime('%H:%M'),
        'hora_fin': taller.hora_fin.strftime('%H:%M'),
        'alumnos': list(inscritos),
        'mi_inscripcion_id': mi_inscripcion,
        'puede_gestionar': puede_gestionar,
    }

    return JsonResponse({'ok': True, 'taller': data})


@login_required
@require_POST
def api_editar_taller(request, taller_id):
    """Editar taller desde calendario."""
    taller = get_object_or_404(Taller, id_taller=taller_id)

    if not puede_gestionar_taller(request.user, taller):
        return JsonResponse({'ok': False, 'msg': 'No puedes editar este taller'}, status=403)

    try:
        taller.nombre = request.POST.get('nombre')
        taller.cupos = int(request.POST.get('cupos'))
        taller.fecha = request.POST.get('fecha')
        taller.hora_inicio = request.POST.get('hora_inicio')
        taller.hora_fin = request.POST.get('hora_fin')

        profesor_id = request.POST.get('profesor_id')

        if es_profesor(request.user):
            taller.profesor = request.user
        else:
            taller.profesor = get_object_or_404(Usuario, id=profesor_id, rol='profesor')

        taller.save()
        return JsonResponse({'ok': True})

    except Exception as e:
        return JsonResponse({'ok': False, 'msg': str(e)})


@login_required
@require_POST
def api_eliminar_taller(request, taller_id):
    """Eliminar taller desde calendario."""
    taller = get_object_or_404(Taller, id_taller=taller_id)

    if not puede_gestionar_taller(request.user, taller):
        return JsonResponse({'ok': False, 'msg': 'No tienes permiso'}, status=403)

    taller.delete()
    return JsonResponse({'ok': True})


# ======================================================
#      INSCRIPCIÓN (ADMIN / PROFESOR / SOCIO)
# ======================================================

@login_required
@require_POST
def api_inscribir_socio(request, taller_id):

    taller = get_object_or_404(Taller, id_taller=taller_id)
    user = request.user

    # SOCIO → solo él mismo
    if es_socio(user):
        socio = get_object_or_404(Socio, rut=user.rut)

    else:
        # PROFESOR O ADMIN
        if not puede_gestionar_taller(user, taller):
            return JsonResponse({'ok': False, 'msg': 'No tienes permisos para inscribir aquí'}, status=403)

        # obtiene socio desde el select correctamente
        socio_id = request.POST.get("socio_id")
        socio = get_object_or_404(Socio, id=socio_id)

    # Validar cupos
    if taller.inscritos_count() >= taller.cupos:
        return JsonResponse({'ok': False, 'msg': 'No hay cupos disponibles'}, status=400)

    # Validar que el socio tenga plan válido
    socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).first()
    if not socio_plan or not socio_plan.plan.puede_reservar_talleres:
        return JsonResponse({'ok': False, 'msg': 'El socio no tiene derecho a talleres'}, status=400)

    # Crear inscripción
    insc, creada = InscripcionTaller.objects.get_or_create(
        socio=socio,
        taller=taller,
        defaults={'estado': 'inscrito'}
    )

    if not creada:
        insc.estado = 'inscrito'
        insc.save()

    
    return api_detalle_taller(request, taller.id_taller)


# ======================================================
#      ASISTENCIA + ELIMINAR INSCRIPCIÓN
# ======================================================

@login_required
@require_POST
def api_cambiar_asistencia(request, insc_id):
    insc = get_object_or_404(InscripcionTaller, id=insc_id)
    taller = insc.taller

    if not puede_gestionar_taller(request.user, taller):
        return JsonResponse({'ok': False, 'msg': 'No tienes permiso'}, status=403)

    nueva = request.POST.get('asistencia')
    if nueva not in dict(InscripcionTaller.ASISTENCIA).keys():
        return JsonResponse({'ok': False, 'msg': 'Valor inválido'})

    insc.asistencia = nueva
    insc.save()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def api_eliminar_inscripcion(request, insc_id):
    insc = get_object_or_404(InscripcionTaller, id=insc_id)
    taller = insc.taller
    user = request.user

    # Socio elimina SOLO su inscripción
    if es_socio(user):
        if insc.socio.rut != user.rut:
            return JsonResponse({'ok': False, 'msg': 'No puedes eliminar otros'}, status=403)

    # admin / profesor / superadmin
    else:
        if not puede_gestionar_taller(user, taller):
            return JsonResponse({'ok': False, 'msg': 'No tienes permiso'}, status=403)

    insc.delete()
    return api_detalle_taller(request, insc.taller.id_taller)

