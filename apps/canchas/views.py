from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST

from apps.canchas.models import Cancha, Reserva
from apps.socios.models import Socio
from apps.planes.models import SocioPlan



def es_admin_o_superadmin(user):
    return user.is_authenticated and (getattr(user, 'rol', None) in ['admin', 'superadmin'])


@login_required
@user_passes_test(es_admin_o_superadmin)
def canchas_list(request):
    canchas = Cancha.objects.all()
    return render(request, 'canchas/canchas_list.html', {'canchas': canchas})


@login_required
@user_passes_test(es_admin_o_superadmin)
def cancha_form(request, cancha_id=None):
    cancha = get_object_or_404(Cancha, id=cancha_id) if cancha_id else None
    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip()
        tipo = request.POST.get('tipo')
        activo = request.POST.get('activo') == 'on'
        existe = Cancha.objects.filter(nombre__iexact=nombre).exclude(id=cancha.id if cancha else None).exists()
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
        return redirect('canchas_list')
    return render(request, 'canchas/cancha_form.html', {'cancha': cancha})


@login_required
@user_passes_test(es_admin_o_superadmin)
def eliminar_cancha(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    nombre = cancha.nombre
    cancha.delete()
    messages.success(request, f"🗑️ La cancha '{nombre}' fue eliminada correctamente.")
    return redirect('/canchas/?success=deleted')


# ---- Reservas ----
@login_required
@user_passes_test(es_admin_o_superadmin)
def reservas_cancha_list(request):
    reservas = Reserva.objects.select_related('cancha', 'socio').all()
    return render(request, 'canchas/reservas_cancha_list.html', {'reservas': reservas})


@login_required
@user_passes_test(es_admin_o_superadmin)
def reserva_cancha_form(request, reserva_id=None):
    """Formulario clásico de reserva (no modal)."""
    socios = Socio.objects.filter(estado=True)
    canchas = Cancha.objects.filter(activo=True)
    reserva = get_object_or_404(Reserva, id=reserva_id) if reserva_id else None

    if request.method == 'POST':
        socio = get_object_or_404(Socio, id=request.POST.get('socio'))
        cancha = get_object_or_404(Cancha, id=request.POST.get('cancha'))
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')

        socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
        if not socio_plan or not socio_plan.plan.puede_reservar_canchas:
            messages.error(request, '❌ El socio no tiene derecho a reservar canchas (plan).')
            return redirect('reservas_cancha_list')

        solapa = Reserva.objects.filter(
            cancha=cancha, fecha=fecha, estado__in=['pendiente', 'confirmada']
        ).exclude(id=reserva.id if reserva else None).filter(
            hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
        ).exists()
        if solapa:
            messages.error(request, '❌ Ya existe una reserva para esa cancha en ese horario.')
            return redirect('reservas_cancha_list')

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
                socio=socio, cancha=cancha, fecha=fecha,
                hora_inicio=hora_inicio, hora_fin=hora_fin,
                estado='confirmada'
            )
            messages.success(request, '✅ Reserva creada.')

        return redirect('reservas_cancha_list')

    return render(request, 'reservas/reserva_cancha_form.html', {
        'reserva': reserva, 'socios': socios, 'canchas': canchas
    })

@login_required
@user_passes_test(lambda u: u.is_authenticated and (getattr(u, 'rol', None) in ['admin', 'superadmin']))
def reserva_cancha_cancelar(request, reserva_id):
    """Cancela una reserva existente."""
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.estado = 'cancelada'
    reserva.save()
    messages.success(request, '✅ Reserva cancelada correctamente.')
    return redirect('reservas_cancha_list')

# ============================
#    API AJAX - RESERVAS
# ============================

@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def crear_reserva_ajax(request):
    socio = get_object_or_404(Socio, id=request.POST.get('socio'))
    cancha = get_object_or_404(Cancha, id=request.POST.get('cancha'))
    fecha = request.POST.get('fecha')
    hora_inicio = request.POST.get('hora_inicio')
    hora_fin = request.POST.get('hora_fin')

    socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
    if not socio_plan or not socio_plan.plan.puede_reservar_canchas:
        return JsonResponse({'status': 'error', 'message': 'El socio no puede reservar canchas con su plan.'}, status=400)

    solapa = Reserva.objects.filter(
        cancha=cancha, fecha=fecha, estado__in=['pendiente', 'confirmada']
    ).filter(
        hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
    ).exists()
    if solapa:
        return JsonResponse({'status': 'error', 'message': 'Ya existe una reserva en ese horario.'}, status=400)

    Reserva.objects.create(
        socio=socio, cancha=cancha, fecha=fecha,
        hora_inicio=hora_inicio, hora_fin=hora_fin, estado='confirmada'
    )
    return JsonResponse({'status': 'success', 'message': 'Reserva creada correctamente.'})




@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def editar_reserva_ajax(request, reserva_id):
    """Edita una reserva existente desde el modal (AJAX)."""
    reserva = get_object_or_404(Reserva, id=reserva_id)
    socio = get_object_or_404(Socio, id=request.POST.get('socio'))
    cancha = get_object_or_404(Cancha, id=request.POST.get('cancha'))
    fecha = request.POST.get('fecha')
    hora_inicio = request.POST.get('hora_inicio')
    hora_fin = request.POST.get('hora_fin')

    # Validar solapamiento
    solapa = Reserva.objects.filter(
        cancha=cancha, fecha=fecha, estado__in=['pendiente', 'confirmada']
    ).exclude(id=reserva.id).filter(
        hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
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
@user_passes_test(es_admin_o_superadmin)
@require_POST
def eliminar_reserva_ajax(request, reserva_id):
    """Elimina una reserva desde el modal (AJAX)."""
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.delete()
    return JsonResponse({'status': 'success', 'message': 'Reserva eliminada correctamente.'})
