from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from apps.users.models import Usuario
from apps.clientes.models import Socio
from apps.planes.models import Plan, SocioPlan
from .models import Clase, InscripcionClase, Cancha, Reserva

# ----------------------------
# Permisos
# ----------------------------
def es_admin_o_superadmin(user):
    return user.is_authenticated and (getattr(user, 'rol', None) in ['admin', 'superadmin'])

def es_profesor(user):
    return user.is_authenticated and getattr(user, 'rol', None) == 'profesor'


# ============================
#        CLASES (CRUD)
# ============================

@login_required
@user_passes_test(es_admin_o_superadmin)
def clases_list(request):
    clases = Clase.objects.all().order_by('fecha', 'hora_inicio')
    return render(request, 'reservas/clases_list.html', {'clases': clases})

@login_required
@user_passes_test(es_admin_o_superadmin)
def clase_form(request, clase_id=None):
    profesores = Usuario.objects.filter(rol='profesor')
    clase = get_object_or_404(Clase, id=clase_id) if clase_id else None

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

        # Validación: choque de horario del mismo profesor
        choque = Clase.objects.filter(
            profesor=profesor, fecha=fecha,
            hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
        ).exclude(id=clase.id if clase else None).exists()
        if choque:
            messages.error(request, '❌ El profesor ya tiene una clase en ese horario.')
            return redirect('clases_list')

        if clase:
            clase.nombre = nombre
            clase.descripcion = descripcion
            clase.profesor = profesor
            clase.cupos = cupos
            clase.fecha = fecha
            clase.hora_inicio = hora_inicio
            clase.hora_fin = hora_fin
            clase.activo = activo
            clase.save()
            messages.success(request, '✅ Clase actualizada.')
        else:
            Clase.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                profesor=profesor,
                cupos=cupos,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                activo=activo
            )
            messages.success(request, '✅ Clase creada.')
        return redirect('clases_list')

    return render(request, 'reservas/clase_form.html', {'clase': clase, 'profesores': profesores})

@login_required
@user_passes_test(es_admin_o_superadmin)
def clase_eliminar(request, clase_id):
    clase = get_object_or_404(Clase, id=clase_id)
    clase.delete()
    messages.success(request, '🗑️ Clase eliminada.')
    return redirect('clases_list')

@login_required
@user_passes_test(es_admin_o_superadmin)
def inscribir_socio_clase(request, clase_id):
    clase = get_object_or_404(Clase, id=clase_id)
    socios = Socio.objects.filter(estado=True)

    if request.method == 'POST':
        socio_id = request.POST.get('socio')
        socio = get_object_or_404(Socio, id=socio_id)

        # Validar cupos
        if clase.inscritos_count() >= clase.cupos:
            messages.error(request, '❌ No hay cupos disponibles.')
            return redirect('clases_list')

        # Validar plan (solo planes con puede_reservar_clases)
        socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
        if not socio_plan or not socio_plan.plan.puede_reservar_clases:
            messages.error(request, '❌ El socio no tiene derecho a inscribirse en clases (plan).')
            return redirect('clases_list')

        InscripcionClase.objects.get_or_create(socio=socio, clase=clase, defaults={'estado': 'inscrito'})
        messages.success(request, f'✅ {socio.nombre} inscrito en {clase.nombre}.')
        return redirect('clases_list')

    return render(request, 'reservas/inscribir_clase.html', {'clase': clase, 'socios': socios})

@login_required
@user_passes_test(es_profesor)
def clases_profesor(request):
    clases = Clase.objects.filter(profesor=request.user).order_by('fecha', 'hora_inicio')
    return render(request, 'reservas/clases_profesor.html', {'clases': clases})


# ============================
#      CANCHAS & RESERVAS
# ============================

@login_required
@user_passes_test(es_admin_o_superadmin)
def canchas_list(request):
    canchas = Cancha.objects.all()
    return render(request, 'reservas/canchas_list.html', {'canchas': canchas})

@login_required
@user_passes_test(es_admin_o_superadmin)
def cancha_form(request, cancha_id=None):
    cancha = get_object_or_404(Cancha, id=cancha_id) if cancha_id else None

    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip()
        tipo = request.POST.get('tipo')
        activo = True if request.POST.get('activo') == 'on' else False

        existe = Cancha.objects.filter(nombre__iexact=nombre).exclude(id=cancha.id if cancha else None).exists()
        if existe:
            messages.error(request, f"❌ Ya existe una cancha llamada '{nombre}'.")
            return redirect('canchas_list')

        if cancha:
            cancha.nombre = nombre
            cancha.tipo = tipo
            cancha.activo = activo
            cancha.save()
            messages.success(request, '✅ Cancha actualizada correctamente.')
        else:
            Cancha.objects.create(nombre=nombre, tipo=tipo, activo=activo)
            messages.success(request, '✅ Cancha creada correctamente.')

        return redirect('canchas_list')

    return render(request, 'reservas/cancha_form.html', {'cancha': cancha})

@login_required
@user_passes_test(es_admin_o_superadmin)
def reservas_cancha_list(request):
    reservas = Reserva.objects.select_related('cancha', 'socio').all()
    return render(request, 'reservas/reservas_cancha_list.html', {'reservas': reservas})

# *** Vista requerida por tus URLs: la dejamos implementada aunque uses modales ***
@login_required
@user_passes_test(es_admin_o_superadmin)
def reserva_cancha_form(request, reserva_id=None):
    """Formulario clásico de reserva (no modal). Lo mantenemos para no romper rutas existentes."""
    socios = Socio.objects.filter(estado=True)
    canchas = Cancha.objects.filter(activo=True)
    reserva = get_object_or_404(Reserva, id=reserva_id) if reserva_id else None

    if request.method == 'POST':
        socio = get_object_or_404(Socio, id=request.POST.get('socio'))
        cancha = get_object_or_404(Cancha, id=request.POST.get('cancha'))
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')

        # Validar plan (solo planes con puede_reservar_canchas)
        socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
        if not socio_plan or not socio_plan.plan.puede_reservar_canchas:
            messages.error(request, '❌ El socio no tiene derecho a reservar canchas (plan).')
            return redirect('reservas_cancha_list')

        # Validar choque
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
@user_passes_test(es_admin_o_superadmin)
def reserva_cancha_cancelar(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.estado = 'cancelada'
    reserva.save()
    messages.success(request, '✅ Reserva cancelada.')
    return redirect('reservas_cancha_list')


# ============================
#          CALENDARIOS
# ============================

@login_required
@user_passes_test(es_admin_o_superadmin)
def calendario_canchas(request):
    socios = Socio.objects.filter(estado=True).order_by('nombre', 'apellido_paterno')
    canchas = Cancha.objects.filter(activo=True).order_by('nombre')
    return render(request, 'reservas/calendario_canchas.html', {'socios': socios, 'canchas': canchas})

@login_required
@user_passes_test(es_admin_o_superadmin)
def calendario_clases(request):
    profesores = list(Usuario.objects.filter(rol='profesor').values('id', 'nombre', 'apellido'))
    socios = list(Socio.objects.filter(estado=True).values('id', 'nombre', 'apellido_paterno'))
    return render(request, 'reservas/calendario_clases.html', {
        'profesores': profesores,
        'socios': socios,
    })


# ---------- JSON para FullCalendar ----------

@login_required
def eventos_canchas_json(request):
    """Eventos del calendario de canchas."""
    eventos = []
    reservas = Reserva.objects.filter(estado='confirmada').select_related('cancha', 'socio')
    for r in reservas:
        eventos.append({
            "title": f"{r.cancha.nombre} - {r.socio.nombre}",
            "start": f"{r.fecha}T{r.hora_inicio}",
            "end": f"{r.fecha}T{r.hora_fin}",
            "color": "#ffc107"
        })
    return JsonResponse(eventos, safe=False)

@login_required
def eventos_clases_json(request):
    """Eventos del calendario de clases."""
    eventos = []
    clases = Clase.objects.filter(activo=True).select_related('profesor')
    for c in clases:
        eventos.append({
            "id": c.id,
            "title": f"{c.nombre} ({c.profesor.nombre})",
            "start": f"{c.fecha}T{c.hora_inicio}",
            "end": f"{c.fecha}T{c.hora_fin}",
            "color": "#5A8DEE"
        })
    return JsonResponse(eventos, safe=False)


# ============================
#        APIs (AJAX)
# ============================

# ---- Clases
@login_required
@user_passes_test(es_admin_o_superadmin)
def api_clases(request):
    clases = Clase.objects.filter(activo=True).select_related('profesor').order_by('fecha', 'hora_inicio')
    data = [{
        'id': c.id,
        'nombre': c.nombre,
        'profesor': f"{c.profesor.nombre} {getattr(c.profesor, 'apellido', '')}".strip(),
        'profesor_id': c.profesor_id,
        'cupos': c.cupos,
        'fecha': c.fecha.strftime('%Y-%m-%d'),
        'hora_inicio': c.hora_inicio.strftime('%H:%M'),
        'hora_fin': c.hora_fin.strftime('%H:%M'),
        'inscritos': c.inscritos_count(),
    } for c in clases]
    return JsonResponse({'clases': data})

@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_crear_clase(request):
    try:
        nombre = request.POST.get('nombre')
        profesor_id = int(request.POST.get('profesor_id'))
        cupos = int(request.POST.get('cupos'))
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')

        profesor = get_object_or_404(Usuario, id=profesor_id, rol='profesor')

        choque = Clase.objects.filter(
            profesor=profesor, fecha=fecha,
            hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
        ).exists()
        if choque:
            return JsonResponse({'ok': False, 'msg': 'El profesor ya tiene una clase en ese horario.'}, status=400)

        clase = Clase.objects.create(
            nombre=nombre,
            profesor=profesor,
            cupos=cupos,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            activo=True
        )
        return JsonResponse({'ok': True, 'id': clase.id})
    except Exception as e:
        return JsonResponse({'ok': False, 'msg': str(e)}, status=400)

@login_required
@user_passes_test(es_admin_o_superadmin)
def api_detalle_clase(request, clase_id):
    c = get_object_or_404(Clase, id=clase_id)
    inscritos = c.inscripciones.select_related('socio').filter(estado='inscrito').values(
        'id', 'socio_id', 'socio__nombre', 'socio__apellido_paterno', 'asistencia'
    )
    data = {
        'id': c.id,
        'nombre': c.nombre,
        'profesor_id': c.profesor_id,
        'profesor': f"{c.profesor.nombre} {getattr(c.profesor, 'apellido', '')}".strip(),
        'cupos': c.cupos,
        'inscritos': c.inscritos_count(),
        'fecha': c.fecha.strftime('%Y-%m-%d'),
        'hora_inicio': c.hora_inicio.strftime('%H:%M'),
        'hora_fin': c.hora_fin.strftime('%H:%M'),
        'alumnos': list(inscritos),
    }
    return JsonResponse({'ok': True, 'clase': data})

@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_eliminar_clase(request, clase_id):
    c = get_object_or_404(Clase, id=clase_id)
    c.delete()
    return JsonResponse({'ok': True})

@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_inscribir_socio(request, clase_id):
    c = get_object_or_404(Clase, id=clase_id)
    socio_id = request.POST.get('socio_id')
    socio = get_object_or_404(Socio, id=socio_id, estado=True)

    # Cupos
    if c.inscritos_count() >= c.cupos:
        return JsonResponse({'ok': False, 'msg': 'Cupos completos para esta clase.'}, status=400)

    # Validar plan
    socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
    if not socio_plan or not socio_plan.plan.puede_reservar_clases:
        return JsonResponse({'ok': False, 'msg': 'El socio no tiene derecho a inscribirse en clases (plan).'}, status=400)

    insc, created = InscripcionClase.objects.get_or_create(
        socio=socio, clase=c, defaults={'estado': 'inscrito'}
    )
    if not created and insc.estado != 'inscrito':
        insc.estado = 'inscrito'
        insc.save()

    return JsonResponse({'ok': True})

@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_cambiar_asistencia(request, insc_id):
    insc = get_object_or_404(InscripcionClase, id=insc_id)
    nueva = request.POST.get('asistencia')
    if nueva not in dict(InscripcionClase.ASISTENCIA).keys():
        return JsonResponse({'ok': False, 'msg': 'Valor de asistencia inválido.'}, status=400)
    insc.asistencia = nueva
    insc.save()
    return JsonResponse({'ok': True})

@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_eliminar_inscripcion(request, insc_id):
    insc = get_object_or_404(InscripcionClase, id=insc_id)
    insc.delete()
    return JsonResponse({'ok': True})


# ---- Canchas (AJAX creación desde modal)
@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def crear_reserva_ajax(request):
    socio = get_object_or_404(Socio, id=request.POST.get('socio'))
    cancha = get_object_or_404(Cancha, id=request.POST.get('cancha'))
    fecha = request.POST.get('fecha')
    hora_inicio = request.POST.get('hora_inicio')
    hora_fin = request.POST.get('hora_fin')

    # Validar plan (solo planes con puede_reservar_canchas)
    socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
    if not socio_plan or not socio_plan.plan.puede_reservar_canchas:
        return JsonResponse({'status': 'error', 'message': 'El socio no puede reservar canchas con su plan.'}, status=400)

    # Validar choque horario
    solapa = Reserva.objects.filter(
        cancha=cancha, fecha=fecha, estado__in=['pendiente', 'confirmada']
    ).filter(
        hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
    ).exists()
    if solapa:
        return JsonResponse({'status': 'error', 'message': 'Ya existe una reserva para esa cancha en ese horario.'}, status=400)

    Reserva.objects.create(
        socio=socio, cancha=cancha, fecha=fecha,
        hora_inicio=hora_inicio, hora_fin=hora_fin, estado='confirmada'
    )
    return JsonResponse({'status': 'success', 'message': 'Reserva creada correctamente.'})
