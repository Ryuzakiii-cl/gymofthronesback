from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST

from apps.canchas.models import Cancha, Reserva
from apps.socios.models import Socio
from apps.planes.models import SocioPlan


# ============================
#   HELPERS DE PERMISOS
# ============================

def es_admin_superadmin_profesor(user):
    """Solo Admin / Superadmin / Profesor."""
    return user.is_authenticated and getattr(user, 'rol', None) in ['admin', 'superadmin', 'profesor']


def es_admin_superadmin_profesor_socio(user):
    """Admin / Superadmin / Profesor / Socio."""
    return user.is_authenticated and getattr(user, 'rol', None) in ['admin', 'superadmin', 'profesor', 'socio']


# ============================
#   CRUD CANCHAS
# ============================

@login_required
@user_passes_test(es_admin_superadmin_profesor)
def canchas_list(request):
    canchas = Cancha.objects.all()
    return render(request, 'canchas/canchas_list.html', {'canchas': canchas})


@login_required
@user_passes_test(es_admin_superadmin_profesor)
def cancha_form(request, cancha_id=None):
    cancha = get_object_or_404(Cancha, id=cancha_id) if cancha_id else None

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        tipo = request.POST.get('tipo')
        activo = request.POST.get('activo') == 'on'

        existe = Cancha.objects.filter(nombre__iexact=nombre).exclude(
            id=cancha.id if cancha else None
        ).exists()

        if existe:
            messages.error(request, f"❌ Ya existe una cancha llamada '{nombre}'.")
            return redirect('canchas_list')

        if cancha:
            cancha.nombre = nombre
            cancha.tipo = tipo
            cancha.activo = activo
            cancha.save()
            return redirect('/canchas/?success=updated')
        else:
            Cancha.objects.create(nombre=nombre, tipo=tipo, activo=activo)
            return redirect('/canchas/?success=created')

    return render(request, 'canchas/cancha_form.html', {'cancha': cancha})


@login_required
@user_passes_test(es_admin_superadmin_profesor)
def eliminar_cancha(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    nombre = cancha.nombre
    cancha.delete()
    messages.success(request, f"🗑️ La cancha '{nombre}' fue eliminada correctamente.")
    return redirect('/canchas/?success=deleted')


# ============================
#   RESERVAS CANCHAS (WEB)
# ============================

@login_required
@user_passes_test(es_admin_superadmin_profesor_socio)
def reservas_cancha_list(request):
    rol = getattr(request.user, 'rol', None)

    if rol in ['admin', 'superadmin', 'profesor']:
        reservas = Reserva.objects.select_related('cancha', 'socio').all()
    else:  # socio
        reservas = Reserva.objects.filter(
            socio__rut=request.user.rut
        ).select_related('cancha', 'socio')

    return render(request, 'canchas/reservas_cancha_list.html', {'reservas': reservas})


@login_required
@user_passes_test(es_admin_superadmin_profesor_socio)
def reserva_cancha_form(request, reserva_id=None):

    rol = getattr(request.user, 'rol', None)
    reserva = get_object_or_404(Reserva, id=reserva_id) if reserva_id else None

    # 🔒 Socio no puede abrir/editar reservas que no son suyas
    if reserva and rol == 'socio' and reserva.socio.rut != request.user.rut:
        return HttpResponseForbidden("No puedes editar reservas de otro socio.")

    # ================================
    # SOCIOS LISTADOS SEGÚN EL ROL
    # ================================
    if rol == 'socio':
        socios = Socio.objects.filter(rut=request.user.rut)
    else:
        socios = Socio.objects.filter(estado=True)

    canchas = Cancha.objects.filter(activo=True)

    if request.method == 'POST':
        # SOCIO NO ELIGE, FORZAR SU PROPIO ID
        if rol == 'socio':
            socio = get_object_or_404(Socio, rut=request.user.rut)
        else:
            socio = get_object_or_404(Socio, id=request.POST.get('socio'))

        cancha = get_object_or_404(Cancha, id=request.POST.get('cancha'))
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')

        # VALIDACIONES DE PLAN
        socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
        if not socio_plan or not socio_plan.plan.puede_reservar_canchas:
            messages.error(request, '❌ El socio no puede reservar canchas con su plan.')
            return redirect('reservas_cancha_list')

        # VALIDAR SOLAPAMIENTO
        solapa = Reserva.objects.filter(
            cancha=cancha,
            fecha=fecha,
            estado__in=['pendiente', 'confirmada']
        ).exclude(id=reserva.id if reserva else None).filter(
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio
        ).exists()
        if solapa:
            messages.error(request, '❌ Ya existe una reserva para esa cancha en ese horario.')
            return redirect('reservas_cancha_list')

        # GUARDADO
        if reserva:
            reserva.socio = socio
            reserva.cancha = cancha
            reserva.fecha = fecha
            reserva.hora_inicio = hora_inicio
            reserva.hora_fin = hora_fin
            reserva.estado = 'confirmada'
            reserva.save()
            messages.success(request, '✅ Reserva actualizada.')
        else:
            Reserva.objects.create(
                socio=socio,
                cancha=cancha,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                estado='confirmada'
            )
            messages.success(request, '✅ Reserva creada.')

        return redirect('reservas_cancha_list')

    return render(request, 'reservas/reserva_cancha_form.html', {
        'reserva': reserva,
        'socios': socios,
        'canchas': canchas,
        'rol': rol,   # 👈 IMPORTANTE: enviar el rol al template
    })


@login_required
@user_passes_test(es_admin_superadmin_profesor_socio)
def reserva_cancha_cancelar(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    rol = getattr(request.user, 'rol', None)

    # 🔒 Socio solo puede cancelar sus propias reservas
    if rol == 'socio':
        socio_usuario = get_object_or_404(Socio, rut=request.user.rut)
        if reserva.socio_id != socio_usuario.id:
            return HttpResponseForbidden("No puedes cancelar reservas de otro socio.")

    reserva.estado = 'cancelada'
    reserva.save()
    messages.success(request, '✅ Reserva cancelada correctamente.')
    return redirect('reservas_cancha_list')


# ============================
#   API AJAX - RESERVAS
# ============================

@login_required
@user_passes_test(es_admin_superadmin_profesor_socio)
@require_POST
def crear_reserva_ajax(request):
    rol = getattr(request.user, 'rol', None)

    if rol == 'socio':
        socio = get_object_or_404(Socio, rut=request.user.rut)
    else:
        socio = get_object_or_404(Socio, id=request.POST.get('socio'))

    cancha = get_object_or_404(Cancha, id=request.POST.get('cancha'))
    fecha = request.POST.get('fecha')
    hora_inicio = request.POST.get('hora_inicio')
    hora_fin = request.POST.get('hora_fin')

    socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
    if not socio_plan or not socio_plan.plan.puede_reservar_canchas:
        return JsonResponse({'status': 'error', 'message': 'El socio no puede reservar canchas con su plan.'}, status=400)

    solapa = Reserva.objects.filter(
        cancha=cancha,
        fecha=fecha,
        estado__in=['pendiente', 'confirmada']
    ).filter(
        hora_inicio__lt=hora_fin,
        hora_fin__gt=hora_inicio
    ).exists()

    if solapa:
        return JsonResponse({'status': 'error', 'message': 'Ya existe una reserva en ese horario.'}, status=400)

    Reserva.objects.create(
        socio=socio,
        cancha=cancha,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        estado='confirmada'
    )
    return JsonResponse({'status': 'success', 'message': 'Reserva creada correctamente.'})


@login_required
@user_passes_test(es_admin_superadmin_profesor_socio)
@require_POST
def editar_reserva_ajax(request, reserva_id):
    """Edita una reserva existente desde el modal (AJAX)."""
    reserva = get_object_or_404(Reserva, id=reserva_id)
    rol = getattr(request.user, 'rol', None)

    # 🔒 Socio solo puede editar sus propias reservas
    if rol == 'socio':
        socio_usuario = get_object_or_404(Socio, rut=request.user.rut)
        if reserva.socio_id != socio_usuario.id:
            return JsonResponse({'status': 'error', 'message': 'No puedes editar reservas de otro socio.'}, status=403)

    if rol == 'socio':
        socio = get_object_or_404(Socio, rut=request.user.rut)
    else:
        socio = get_object_or_404(Socio, id=request.POST.get('socio'))

    cancha = get_object_or_404(Cancha, id=request.POST.get('cancha'))
    fecha = request.POST.get('fecha')
    hora_inicio = request.POST.get('hora_inicio')
    hora_fin = request.POST.get('hora_fin')

    solapa = Reserva.objects.filter(
        cancha=cancha,
        fecha=fecha,
        estado__in=['pendiente', 'confirmada']
    ).exclude(id=reserva.id).filter(
        hora_inicio__lt=hora_fin,
        hora_fin__gt=hora_inicio
    ).exists()

    if solapa:
        return JsonResponse({'status': 'error', 'message': 'Ya existe una reserva para esa cancha en ese horario.'}, status=400)

    reserva.socio = socio
    reserva.cancha = cancha
    reserva.fecha = fecha
    reserva.hora_inicio = hora_inicio
    reserva.hora_fin = hora_fin
    reserva.save()

    return JsonResponse({'status': 'success', 'message': 'Reserva actualizada correctamente.'})


@login_required
@user_passes_test(es_admin_superadmin_profesor_socio)
@require_POST
def eliminar_reserva_ajax(request, reserva_id):
    """Elimina una reserva desde el modal (AJAX)."""
    reserva = get_object_or_404(Reserva, id=reserva_id)
    rol = getattr(request.user, 'rol', None)

    # 🔒 Socio solo puede eliminar sus propias reservas
    if rol == 'socio':
        socio_usuario = get_object_or_404(Socio, rut=request.user.rut)
        if reserva.socio_id != socio_usuario.id:
            return JsonResponse({'status': 'error', 'message': 'No puedes eliminar reservas de otro socio.'}, status=403)

    reserva.delete()
    return JsonResponse({'status': 'success', 'message': 'Reserva eliminada correctamente.'})
