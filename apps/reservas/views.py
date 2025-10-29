from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect 
from django.views.decorators.http import require_POST
from django.db import IntegrityError

from apps.users.models import Usuario
from apps.clientes.models import Socio
from apps.planes.models import SocioPlan
# Modelos importados correctamente
from .models import Taller, InscripcionTaller, Cancha, Reserva 


# ----------------------------
# Permisos
# ----------------------------
def es_admin_o_superadmin(user):
    return user.is_authenticated and (getattr(user, 'rol', None) in ['admin', 'superadmin'])

def es_profesor(user):
    return user.is_authenticated and getattr(user, 'rol', None) == 'profesor'

def es_socio(user):
    return user.is_authenticated and getattr(user, 'rol', None) == 'socio'


# ============================
#       TALLERES (CRUD)
# ============================

@login_required
@user_passes_test(es_admin_o_superadmin)
def taller_list(request):
    """Lista todos los talleres."""
    talleres = Taller.objects.all().order_by('fecha', 'hora_inicio')
    # Contexto actualizado a 'talleres'
    return render(request, 'reservas/talleres_list.html', {'talleres': talleres})

@login_required
@user_passes_test(es_admin_o_superadmin)
def taller_form(request, taller_id=None):
    """Formulario para crear o editar un Taller."""
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

        # Validación: choque de horario del mismo profesor
        choque = Taller.objects.filter(
            profesor=profesor, fecha=fecha,
            hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
        ).exclude(id_taller=taller.id_taller if taller else None).exists()
        
        if choque:
            messages.error(request, '❌ El profesor ya tiene un taller en ese horario.')
            return redirect('talleres_list') 

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
        return redirect('talleres_list') # OJO: URL 'clases_list'

    # Contexto actualizado a 'taller'
    return render(request, 'reservas/taller_form.html', {'taller': taller, 'profesores': profesores})

@login_required
@user_passes_test(es_admin_o_superadmin)
def taller_eliminar(request, taller_id):
    """Elimina un taller."""
    taller = get_object_or_404(Taller, id_taller=taller_id) # Usar id_taller
    taller.delete()
    messages.success(request, '🗑️ Taller eliminado.')
    return redirect('clases_list') # OJO: URL 'clases_list'

@login_required
@user_passes_test(es_admin_o_superadmin)
def inscribir_socio_taller(request, taller_id):
    """Inscribe manualmente un socio a un taller (vista de admin)."""
    taller = get_object_or_404(Taller, id_taller=taller_id) # Usar Taller y id_taller
    socios = Socio.objects.filter(estado=True)

    if request.method == 'POST':
        socio_id = request.POST.get('socio')
        socio = get_object_or_404(Socio, id=socio_id)

        # Validar cupos
        if taller.inscritos_count() >= taller.cupos:
            messages.error(request, '❌ No hay cupos disponibles.')
            return redirect('clases_list') # OJO: URL 'clases_list'

        # Validar plan (solo planes con puede_reservar_clases)
        socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
        if not socio_plan or not socio_plan.plan.puede_reservar_talleres:
            messages.error(request, '❌ El socio no tiene derecho a inscribirse en talleres (plan).')
            return redirect('clases_list') # OJO: URL 'clases_list'

        # Usar InscripcionTaller y el campo 'taller'
        InscripcionTaller.objects.get_or_create(socio=socio, taller=taller, defaults={'estado': 'inscrito'})
        messages.success(request, f'✅ {socio.nombre} inscrito en {taller.nombre}.')
        return redirect('clases_list') # OJO: URL 'clases_list'

    # Contexto actualizado a 'taller'
    return render(request, 'reservas/inscribir_clase.html', {'taller': taller, 'socios': socios})

@login_required
@user_passes_test(es_profesor)
def talleres_profesor(request):
    """Vista para que el profesor vea sus talleres asignados."""
    talleres = Taller.objects.filter(profesor=request.user).order_by('fecha', 'hora_inicio')
    # Contexto actualizado a 'talleres'
    return render(request, 'reservas/clases_profesor.html', {'talleres': talleres})


# ============================
#       CANCHAS 
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
def eliminar_cancha(request, cancha_id):
    """Elimina una cancha existente."""
    cancha = get_object_or_404(Cancha, id=cancha_id)
    nombre = cancha.nombre

    try:
        cancha.delete()
        messages.success(request, f"🗑️ La cancha '{nombre}' fue eliminada correctamente.")
    except Exception as e:
        messages.error(request, f"❌ No se pudo eliminar la cancha: {e}")

    return redirect('canchas_list')


@login_required
@user_passes_test(es_admin_o_superadmin)
def reservas_cancha_list(request):
    reservas = Reserva.objects.select_related('cancha', 'socio').all()
    return render(request, 'reservas/reservas_cancha_list.html', {'reservas': reservas})

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
@user_passes_test(es_admin_o_superadmin)
def reserva_cancha_cancelar(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.estado = 'cancelada'
    reserva.save()
    messages.success(request, '✅ Reserva cancelada.')
    return redirect('reservas_cancha_list')


# ============================
#         CALENDARIOS
# ============================

@login_required
@user_passes_test(es_admin_o_superadmin)
def calendario_canchas(request):
    socios = Socio.objects.filter(estado=True).order_by('nombre', 'apellido_paterno')
    canchas = Cancha.objects.filter(activo=True).order_by('nombre')
    return render(request, 'reservas/calendario_canchas.html', {'socios': socios, 'canchas': canchas})

@login_required
@user_passes_test(es_admin_o_superadmin)
def calendario_talleres(request): 
    profesores = list(Usuario.objects.filter(rol='profesor').values('id', 'nombre', 'apellido'))
    socios = list(Socio.objects.filter(estado=True).values('id', 'nombre', 'apellido_paterno'))
    return render(request, 'reservas/calendario_talleres.html', { #Nombre de template
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
def eventos_talleres_json(request): # Renombrada
    """Devuelve talleres e inscripciones para el calendario de talleres."""
    eventos = []

    # --- Talleres base ---
    for taller in Taller.objects.filter(activo=True): # Usar Taller
        eventos.append({
            "id": taller.id_taller, # Usar id_taller
            "title": taller.nombre,
            "start": f"{taller.fecha}T{taller.hora_inicio}",
            "end": f"{taller.fecha}T{taller.hora_fin}",
            "color": "#007bff",  # azul = taller disponible
            "extendedProps": {
                "tipo": "taller", # 'taller'
                "id_taller": taller.id_taller, # id_taller
                "profesor": f"{taller.profesor.nombre} {getattr(taller.profesor, 'apellido', '')}".strip(),
                "cupos": taller.cupos,
                "inscritos": taller.inscritos_count(),
            }
        })

    # --- Inscripciones de socios ---
    # Usar InscripcionTaller y select_related('taller', 'socio')
    inscripciones = InscripcionTaller.objects.select_related('taller', 'socio').filter(estado='inscrito') 
    for insc in inscripciones:
        eventos.append({
            "id": f"insc-{insc.id}",
            "title": f"{insc.socio.nombre} ({insc.taller.nombre})", # usar insc.taller
            "start": f"{insc.taller.fecha}T{insc.taller.hora_inicio}", # usar insc.taller
            "end": f"{insc.taller.fecha}T{insc.taller.hora_fin}", # usar insc.taller
            "color": "#28a745",  # verde = reserva
            "extendedProps": {
                "tipo": "reserva",
                "id_inscripcion": insc.id,
                "socio": insc.socio.nombre,
                "taller": insc.taller.nombre, # 'taller'
            }
        })

    return JsonResponse(eventos, safe=False)


# ============================
#        APIs (AJAX)
# ============================

# ---- Talleres
@login_required
@user_passes_test(es_admin_o_superadmin)
def api_talleres(request): # Renombrada
    """API que lista todos los talleres."""
    talleres = Taller.objects.filter(activo=True).select_related('profesor').order_by('fecha', 'hora_inicio')
    data = [{
        'id': c.id_taller,
        'nombre': c.nombre,
        'profesor': f"{c.profesor.nombre} {getattr(c.profesor, 'apellido', '')}".strip(),
        'cupos': c.cupos,
        'fecha': c.fecha.strftime('%Y-%m-%d'),
        'hora_inicio': c.hora_inicio.strftime('%H:%M'),
        'hora_fin': c.hora_fin.strftime('%H:%M'),
        'inscritos': c.inscritos_count(),
    } for c in talleres] # variable 'talleres'
    return JsonResponse({'ok': True, 'talleres': data}) # 'talleres'

@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_crear_taller(request):
    """Crear un nuevo taller desde el calendario."""
    try:
        nombre = request.POST.get('nombre')
        profesor_id = int(request.POST.get('profesor_id'))
        cupos = int(request.POST.get('cupos'))
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        profesor = get_object_or_404(Usuario, id=profesor_id, rol='profesor')

        choque = Taller.objects.filter(
            profesor=profesor, fecha=fecha,
            hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
        ).exists()
        if choque:
            return JsonResponse({'ok': False, 'msg': 'El profesor ya tiene un taller en ese horario.'}, status=400)

        nueva = Taller.objects.create( 
            nombre=nombre,
            profesor=profesor,
            cupos=cupos,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            activo=True
        )

        return JsonResponse({'ok': True, 'msg': 'Taller creado correctamente', 'id': nueva.id_taller})
    except Exception as e:
        return JsonResponse({'ok': False, 'msg': str(e)}, status=400)


@login_required
@user_passes_test(es_admin_o_superadmin)
def api_detalle_taller(request, taller_id): 
    """Devuelve detalle de un taller con los socios inscritos."""
    taller = get_object_or_404(Taller, id_taller=taller_id) 
    
    inscritos = taller.inscripciones.select_related('socio').filter(estado='inscrito').values(
        'id', 'socio_id', 'socio__nombre', 'socio__apellido_paterno', 'asistencia'
    )
    data = {
        'id': taller.id_taller,
        'nombre': taller.nombre,
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
def api_eliminar_taller(request, taller_id): 
    """Elimina un taller."""
    taller = get_object_or_404(Taller, id_taller=taller_id) 
    taller.delete()
    return JsonResponse({'ok': True, 'msg': 'Taller eliminado correctamente'})


@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_inscribir_socio(request, taller_id):
    """Inscribe un socio en un taller, si hay cupos y su plan lo permite."""
    try:
        taller = get_object_or_404(Taller, id_taller=taller_id) 
        socio_id = request.POST.get('socio_id')
        socio = get_object_or_404(Socio, id=socio_id, estado=True)

        # Validar cupos
        if taller.inscritos_count() >= taller.cupos:
            return JsonResponse({'ok': False, 'msg': 'Cupos completos para este taller.'}, status=400)

        # Validar plan
        socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
        if not socio_plan or not socio_plan.plan.puede_reservar_talleres:
            return JsonResponse({'ok': False, 'msg': 'El socio no tiene derecho a inscribirse en talleres (plan).'}, status=400)

        
        insc, created = InscripcionTaller.objects.get_or_create(
            socio=socio, taller=taller, defaults={'estado': 'inscrito'}
        )
        if not created and insc.estado != 'inscrito':
            insc.estado = 'inscrito'
            insc.save()

        return JsonResponse({'ok': True, 'msg': 'Socio inscrito correctamente', 'id': insc.id})
    except IntegrityError:
        return JsonResponse({'ok': False, 'msg': 'El socio ya está inscrito en este taller.'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'msg': str(e)}, status=400)

@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_cambiar_asistencia(request, insc_id):
    """Cambia el estado de asistencia de una inscripcion."""
    insc = get_object_or_404(InscripcionTaller, id=insc_id) 
    nueva = request.POST.get('asistencia')
    
    if nueva not in dict(InscripcionTaller.ASISTENCIA).keys():
        return JsonResponse({'ok': False, 'msg': 'Valor de asistencia inválido.'}, status=400)
    
    insc.asistencia = nueva
    insc.save()
    return JsonResponse({'ok': True})

@login_required
@user_passes_test(es_admin_o_superadmin)
@require_POST
def api_eliminar_inscripcion(request, insc_id):
    """Elimina una inscripción a taller."""
    insc = get_object_or_404(InscripcionTaller, id=insc_id) 
    insc.delete()
    return JsonResponse({'ok': True, 'msg': 'Inscripción eliminada correctamente'})


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

    socio_plan = SocioPlan.objects.filter(socio=socio, estado=True).order_by('-fecFin').first()
    if not socio_plan or not socio_plan.plan.puede_reservar_canchas:
        return JsonResponse({'status': 'error', 'message': 'El socio no puede reservar canchas con su plan.'}, status=400)

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