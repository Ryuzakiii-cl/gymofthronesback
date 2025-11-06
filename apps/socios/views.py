from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta

from apps.socios.models import Socio
from apps.planes.models import Plan, SocioPlan
from apps.pagos.models import Pago
from apps.users.views import es_admin, es_superadmin




def formatear_rut(rut):
    """Formatea un RUT chileno sin puntos ni guion -> con puntos y guion."""
    try:
        rut = str(rut)
        cuerpo, dv = rut[:-1], rut[-1]
        cuerpo_con_puntos = f"{int(cuerpo):,}".replace(",", ".")
        return f"{cuerpo_con_puntos}-{dv.upper()}"
    except Exception:
        return rut  # si viene vacío o mal formado, se deja igual



# --- Listar socios ---
@login_required
@user_passes_test(lambda u: es_admin(u) or es_superadmin(u))
def lista_socios(request):
    socios = Socio.objects.select_related().order_by('nombre')
    for s in socios:
        s.rut_formateado = formatear_rut(s.rut)
    return render(request, 'socios/lista_socios.html', {'socios': socios})



# --- Crear socio ---
@login_required
@user_passes_test(lambda u: es_admin(u) or es_superadmin(u))
def crear_socio(request):
    planes = Plan.objects.all()

    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        nombre = request.POST.get('nombre')
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        fecNac = request.POST.get('fecNac') or None
        plan_id = request.POST.get('plan')
        forma_pago = request.POST.get('forma_pago')

        if Socio.objects.filter(rut=rut).exists():
            return redirect('/socios/?error=exists')

        # ✅ Crear socio
        socio = Socio.objects.create(
            rut=rut,
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            correo=correo,
            telefono=telefono,
            fecNac=fecNac,
            estado=True
        )

        # 🔐 Crear usuario asociado al socio
        from apps.users.models import Usuario
        from django.contrib.auth.hashers import make_password

        if not Usuario.objects.filter(rut=rut).exists():
            Usuario.objects.create(
                rut=rut,
                nombre=nombre,
                apellido=apellido_paterno,
                correo=correo,
                rol='socio',
                password=make_password(rut),
                is_active=True
            )

        # 🧾 Asignar plan y pago
        plan = Plan.objects.get(id=plan_id)
        fec_inicio = timezone.localdate()
        fec_fin = fec_inicio + timedelta(days=plan.duracion)

        socio_plan = SocioPlan.objects.create(
            socio=socio,
            plan=plan,
            fecInicio=fec_inicio,
            fecFin=fec_fin,
            estado=True
        )

        Pago.objects.create(
            socio=socio,
            plan=plan,
            socio_plan=socio_plan,
            monto=plan.precio,
            forma_pago=forma_pago,
            observaciones="Pago inicial del plan",
            estado='completado'
        )

        return redirect('/socios/?success=created')

    return render(request, 'socios/crear_socio.html', {'planes': planes})



# --- Editar socio ---
@login_required
@user_passes_test(lambda u: es_admin(u) or es_superadmin(u))
def editar_socio(request, socio_id):
    socio = get_object_or_404(Socio, id=socio_id)
    planes = Plan.objects.all()
    hoy = timezone.localdate()

    # Plan actual
    plan_actual = SocioPlan.objects.filter(
        socio=socio,
        estado=True,
        fecFin__gte=hoy
    ).order_by('-fecFin').first()
    socio.plan_actual_obj = plan_actual.plan if plan_actual else None

    if request.method == 'POST':
        nuevo_rut = request.POST.get('rut', '').strip()
        socio.nombre = request.POST.get('nombre')
        socio.apellido_paterno = request.POST.get('apellido_paterno')
        socio.apellido_materno = request.POST.get('apellido_materno')
        socio.correo = request.POST.get('correo')
        socio.telefono = request.POST.get('telefono')
        socio.fecNac = request.POST.get('fecNac') or None

        # ✅ Guardar el checkbox "estado"
        socio.estado = True if request.POST.get('estado') == 'on' else False

        # ⚠️ Validar cambio de RUT
        if nuevo_rut != socio.rut:
            if Socio.objects.filter(rut=nuevo_rut).exclude(id=socio.id).exists():
                return redirect(f'/socios/editar/{socio.id}/?error=exists')
            socio.rut = nuevo_rut

        # 🔁 Actualización del plan
        nuevo_plan_id = request.POST.get('plan')
        if nuevo_plan_id:
            nuevo_plan = Plan.objects.get(id=nuevo_plan_id)
            if not plan_actual or nuevo_plan.id != plan_actual.plan.id:
                if plan_actual:
                    plan_actual.estado = False
                    plan_actual.save()

                fec_inicio = hoy
                fec_fin = fec_inicio + timedelta(days=nuevo_plan.duracion)

                SocioPlan.objects.create(
                    socio=socio,
                    plan=nuevo_plan,
                    fecInicio=fec_inicio,
                    fecFin=fec_fin,
                    estado=True
                )

        socio.save()

        # 🔁 Sincronizar usuario asociado al socio
        from apps.users.models import Usuario
        from django.contrib.auth.hashers import make_password

        try:
            usuario = Usuario.objects.get(rut=socio.rut)
            usuario.nombre = socio.nombre
            usuario.apellido = socio.apellido_paterno
            usuario.correo = socio.correo
            usuario.is_active = socio.estado
            usuario.save()
        except Usuario.DoesNotExist:
            Usuario.objects.create(
                rut=socio.rut,
                nombre=socio.nombre,
                apellido=socio.apellido_paterno,
                correo=socio.correo,
                rol='socio',
                password=make_password(socio.rut),
                is_active=socio.estado
            )

        return redirect('/socios/?success=updated')

    return render(request, 'socios/editar_socio.html', {
        'socio': socio,
        'planes': planes
    })


# --- Eliminar socio ---
@login_required
@user_passes_test(lambda u: es_admin(u) or es_superadmin(u))
def eliminar_socio(request, id):
    socio = get_object_or_404(Socio, id=id)

    # 🗑️ Eliminar usuario asociado si existe
    from apps.users.models import Usuario
    Usuario.objects.filter(rut=socio.rut).delete()

    socio.delete()
    return redirect('/socios/?success=deleted')
