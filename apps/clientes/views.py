from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone  # ✅ reemplaza datetime.date
from datetime import timedelta

from apps.clientes.models import Socio
from apps.planes.models import Plan, SocioPlan
from apps.pagos.models import Pago


# --- Permiso de acceso ---
def es_admin_o_superadmin(user):
    return user.is_authenticated and (user.rol == 'admin' or user.rol == 'superadmin')


# --- Listar socios ---
@login_required
@user_passes_test(es_admin_o_superadmin)
def lista_socios(request):
    socios = Socio.objects.all().order_by('-fec_registro')
    return render(request, 'clientes/lista_socios.html', {'socios': socios})


# --- Crear socio ---
@login_required
@user_passes_test(es_admin_o_superadmin)
def crear_socio(request):
    planes = Plan.objects.all()

    if request.method == 'POST':
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        fecNac = request.POST.get('fecNac') or None
        plan_id = request.POST.get('plan')
        forma_pago = request.POST.get('forma_pago')

        # Verificar si ya existe el socio
        if Socio.objects.filter(rut=rut).exists():
            messages.error(request, '❌ Ya existe un socio con ese RUT.')
            return redirect('crear_socio')

        # Crear socio
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

        # Asignar plan y registrar pago
        plan = Plan.objects.get(id=plan_id)
        fec_inicio = timezone.localdate()  # ✅ reemplaza date.today()
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

        messages.success(request, f'✅ Socio {socio.nombre} registrado con el plan {plan.nombre}.')
        return redirect('lista_socios')

    return render(request, 'clientes/crear_socio.html', {'planes': planes})


# --- Editar socio ---
@login_required
@user_passes_test(es_admin_o_superadmin)
def editar_socio(request, socio_id):
    socio = get_object_or_404(Socio, id=socio_id)
    planes = Plan.objects.all()

    hoy = timezone.localdate()
    plan_actual = SocioPlan.objects.filter(
        socio=socio,
        estado=True,
        fecFin__gte=hoy
    ).order_by('-fecFin').first()

    socio.plan_actual_obj = plan_actual.plan if plan_actual else None

    if request.method == 'POST':
        socio.nombre = request.POST.get('nombre')
        socio.apellido_paterno = request.POST.get('apellido_paterno')
        socio.apellido_materno = request.POST.get('apellido_materno')
        socio.correo = request.POST.get('correo')
        socio.telefono = request.POST.get('telefono')
        socio.fecNac = request.POST.get('fecNac') or None
        socio.estado = 'estado' in request.POST

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
        messages.success(request, '✅ Socio actualizado correctamente.')
        return redirect('lista_socios')

    return render(request, 'clientes/editar_socio.html', {'socio': socio, 'planes': planes})


# --- Eliminar socio ---
@login_required
@user_passes_test(es_admin_o_superadmin)
def eliminar_socio(request, id):
    socio = get_object_or_404(Socio, id=id)
    socio.delete()
    messages.success(request, '🗑️ Socio eliminado correctamente.')
    return redirect('lista_socios')
