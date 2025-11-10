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
from apps.core.decorators import es_admin, es_superadmin, es_profesor

# roles permitidos
es_admin_o_superadmin = lambda u: es_admin(u) or es_superadmin(u)


# ======================================================
#                CRUD DE TALLERES
# ======================================================

# CREAR / EDITAR
@login_required
@user_passes_test(es_admin_o_superadmin)
def taller_form(request, taller_id=None):
    """Formulario para crear o editar talleres"""
    profesores = Usuario.objects.filter(rol='profesor')
    taller = get_object_or_404(Taller, id_taller=taller_id) if taller_id else None

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion') or ''
        profesor_id = request.POST.get('profesor')
        cupos = int(request.POST.get('cupos'))
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        activo = True if request.POST.get('activo') == 'on' else False

        profesor = get_object_or_404(Usuario, id=profesor_id)

        # Crear o actualizar
        if taller:
            taller.nombre = nombre
            taller.descripcion = descripcion
            taller.profesor = profesor
            taller.cupos = cupos
            taller.fecha = fecha
            taller.hora_inicio = hora_inicio
            taller.hora_fin = hora_fin
            taller.activo = activo
            taller.save()
            messages.success(request, '✅ Taller actualizado.')
        else:
            Taller.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                profesor=profesor,
                cupos=cupos,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                activo=activo
            )
            messages.success(request, '✅ Taller creado.')
        return redirect('talleres_list')

    return render(request, 'talleres/taller_form.html', {'taller': taller, 'profesores': profesores})


# LEER (LISTAR)
@login_required
@user_passes_test(es_admin_o_superadmin)
def taller_list(request):
    """Listado general de talleres"""
    talleres = Taller.objects.all().order_by('fecha', 'hora_inicio')
    return render(request, 'talleres/talleres_list.html', {'talleres': talleres})


# ELIMINAR
@login_required
@user_passes_test(es_admin_o_superadmin)
def taller_eliminar(request, taller_id):
    """Eliminar un taller existente"""
    taller = get_object_or_404(Taller, id_taller=taller_id)
    taller.delete()
    messages.success(request, '🗑️ Taller eliminado.')
    return redirect('talleres_list')


# ======================================================
#           INSCRIPCIONES Y VISTA DEL PROFESOR
# ======================================================

#INSCRIBIR SOCIO A TALLER
@login_required
@user_passes_test(es_admin_o_superadmin)
def inscribir_socio_taller(request, taller_id):
    """Permite inscribir un socio a un taller si tiene plan activo"""
    taller = get_object_or_404(Taller, id_taller=taller_id)
    socios = Socio.objects.filter(estado=True)

    if request.method == 'POST':
        socio_id = request.POST.get('socio')
        socio = get_object_or_404(Socio, id=socio_id)

        if taller.inscritos_count() >= taller.cupos:
            messages.error(request, '❌ No hay cupos disponibles.')
            return redirect('talleres_list')

        socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
        if not socio_plan or not socio_plan.plan.puede_reservar_talleres:
            messages.error(request, '❌ El socio no tiene derecho a talleres.')
            return redirect('talleres_list')

        InscripcionTaller.objects.get_or_create(
            socio=socio, taller=taller, defaults={'estado': 'inscrito'}
        )
        messages.success(request, f'✅ {socio.nombre} inscrito en {taller.nombre}.')
        return redirect('talleres_list')

    return render(request, 'talleres/inscribir_taller.html', {'taller': taller, 'socios': socios})


#LISTADO DE TALLERES DEL PROFESOR
@login_required
@user_passes_test(es_profesor)
def talleres_profesor(request):
    """Vista exclusiva del profesor con sus talleres"""
    talleres = Taller.objects.filter(profesor=request.user).order_by('fecha', 'hora_inicio')
    return render(request, 'talleres/talleres_profesor.html', {'talleres': talleres})


# ======================================================
#                  API CRUD DE TALLERES (AJAX)
# ======================================================

@login_required
@user_passes_test(es_admin_o_superadmin)
def api_talleres(request):
    """Listado de talleres activos (para calendario o dashboard)"""
    talleres = Taller.objects.filter(activo=True).select_related('profesor').order_by('fecha', 'hora_inicio')
    data = [{
        'id': t.id_taller,
        'nombre': t.nombre,
        'profesor': f"{t.profesor.nombre} {getattr(t.profesor, 'apellido', '')}".strip(),
        'cupos': t.cupos,
        'fecha': t.fecha.strftime('%Y-%m-%d'),
        'hora_inicio': t.hora_inicio.strftime('%H:%M'),
        'hora_fin': t.hora_fin.strftime('%H:%M'),
        'inscritos': t.inscritos_count(),
    } for t in talleres]
    return JsonResponse({'ok': True, 'talleres': data})


@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_crear_taller(request):
    """Crear un nuevo taller desde el calendario (AJAX)"""
    try:
        nombre = request.POST.get('nombre')
        profesor_id = int(request.POST.get('profesor_id'))
        cupos = int(request.POST.get('cupos'))
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
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
        return JsonResponse({'ok': True, 'msg': 'Taller creado correctamente', 'id': nuevo.id_taller})
    except Exception as e:
        return JsonResponse({'ok': False, 'msg': str(e)}, status=400)


@login_required
@user_passes_test(es_admin_o_superadmin)
def api_detalle_taller(request, taller_id):
    """Devuelve los detalles del taller (modal de detalle AJAX)"""
    taller = get_object_or_404(Taller, id_taller=taller_id)
    inscritos = taller.inscripciones.select_related('socio').filter(estado='inscrito').values(
        'id', 'socio_id', 'socio__nombre', 'socio__apellido_paterno', 'asistencia'
    )

    data = {
        'id': taller.id_taller,
        'nombre': taller.nombre,
        'profesor_id': taller.profesor.id,
        'profesor': f"{taller.profesor.nombre} {getattr(taller.profesor, 'apellido', '')}".strip(),
        'cupos': taller.cupos,
        'inscritos': taller.inscritos_count(),
        'fecha': taller.fecha.strftime('%Y-%m-%d'),
        'hora_inicio': taller.hora_inicio.strftime('%H:%M'),
        'hora_fin': taller.hora_fin.strftime('%H:%M'),
        'alumnos': list(inscritos),
    }
    return JsonResponse({'ok': True, 'taller': data})


@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_editar_taller(request, taller_id):
    """Editar un taller existente (AJAX)"""
    try:
        taller = get_object_or_404(Taller, id_taller=taller_id)
        nombre = request.POST.get('nombre')
        profesor_id = request.POST.get('profesor_id')
        cupos = request.POST.get('cupos')
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')

        profesor = get_object_or_404(Usuario, id=profesor_id, rol='profesor')

        taller.nombre = nombre
        taller.profesor = profesor
        taller.cupos = int(cupos)
        taller.fecha = fecha
        taller.hora_inicio = hora_inicio
        taller.hora_fin = hora_fin
        taller.save()

        return JsonResponse({'ok': True, 'msg': 'Taller actualizado correctamente'})
    except Exception as e:
        return JsonResponse({'ok': False, 'msg': str(e)}, status=400)


@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_eliminar_taller(request, taller_id):
    """Eliminar un taller (AJAX)"""
    taller = get_object_or_404(Taller, id_taller=taller_id)
    taller.delete()
    return JsonResponse({'ok': True, 'msg': 'Taller eliminado correctamente'})


# ======================================================
#           API AJAX - INSCRIPCIÓN Y ASISTENCIA
# ======================================================

@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_inscribir_socio(request, taller_id):
    """Inscribe un socio en un taller, si hay cupos y su plan lo permite."""
    try:
        taller = get_object_or_404(Taller, id_taller=taller_id)
        socio_id = request.POST.get('socio_id')
        socio = get_object_or_404(Socio, id=socio_id, estado=True)

        if taller.inscritos_count() >= taller.cupos:
            return JsonResponse({'ok': False, 'msg': 'Cupos completos para este taller.'}, status=400)

        socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
        if not socio_plan or not socio_plan.plan.puede_reservar_talleres:
            return JsonResponse({'ok': False, 'msg': 'El socio no tiene derecho a inscribirse en talleres (plan).'}, status=400)

        inscripcion, creada = InscripcionTaller.objects.get_or_create(
            socio=socio,
            taller=taller,
            defaults={'estado': 'inscrito'}
        )
        if not creada and inscripcion.estado != 'inscrito':
            inscripcion.estado = 'inscrito'
            inscripcion.save()

        return JsonResponse({'ok': True, 'msg': 'Socio inscrito correctamente', 'id': inscripcion.id})
    except IntegrityError:
        return JsonResponse({'ok': False, 'msg': 'El socio ya está inscrito en este taller.'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'msg': str(e)}, status=400)


@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_cambiar_asistencia(request, insc_id):
    """Cambia el estado de asistencia de una inscripción (AJAX)."""
    insc = get_object_or_404(InscripcionTaller, id=insc_id)
    nueva_asistencia = request.POST.get('asistencia')

    if nueva_asistencia not in dict(InscripcionTaller.ASISTENCIA).keys():
        return JsonResponse({'ok': False, 'msg': 'Valor de asistencia inválido.'}, status=400)

    insc.asistencia = nueva_asistencia
    insc.save()
    return JsonResponse({'ok': True, 'msg': 'Asistencia actualizada correctamente.'})


@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_eliminar_inscripcion(request, insc_id):
    """Elimina una inscripción a un taller (AJAX)."""
    insc = get_object_or_404(InscripcionTaller, id=insc_id)
    insc.delete()
    return JsonResponse({'ok': True, 'msg': 'Inscripción eliminada correctamente'})