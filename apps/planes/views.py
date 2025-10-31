from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone  
from datetime import timedelta
from .models import Plan, SocioPlan
from apps.clientes.models import Socio


def es_admin_o_superadmin(user):
    return user.is_authenticated and (user.rol == 'admin' or user.rol == 'superadmin')


@login_required
@user_passes_test(es_admin_o_superadmin)
def lista_planes(request):
    planes = Plan.objects.all().order_by('precio')
    return render(request, 'planes/lista_planes.html', {'planes': planes})


@login_required
@user_passes_test(es_admin_o_superadmin)
def crear_plan(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST['precio']
        duracion = request.POST['duracion']
        puede_reservar_talleres = request.POST.get('puede_reservar_talleres') is not None
        puede_reservar_canchas = request.POST.get('puede_reservar_canchas') is not None

        Plan.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            duracion=duracion,
            puede_reservar_talleres=puede_reservar_talleres,
            puede_reservar_canchas=puede_reservar_canchas,
        )
        return redirect('lista_planes')
    return render(request, 'planes/form_plan.html')


@login_required
@user_passes_test(es_admin_o_superadmin)
def editar_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        plan.nombre = request.POST['nombre']
        plan.descripcion = request.POST.get('descripcion', '')
        plan.precio = request.POST['precio']
        plan.duracion = request.POST['duracion']
        plan.puede_reservar_talleres = request.POST.get('puede_reservar_talleres') is not None
        plan.puede_reservar_canchas = request.POST.get('puede_reservar_canchas') is not None
        plan.save()
        return redirect('lista_planes')
    return render(request, 'planes/form_plan.html', {'plan': plan})


@login_required
@user_passes_test(es_admin_o_superadmin)
def eliminar_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    plan.delete()
    return redirect('lista_planes')


@login_required
@user_passes_test(es_admin_o_superadmin)
def asignar_plan(request, socio_id):
    socio = Socio.objects.get(id=socio_id)
    planes = Plan.objects.all()

    if request.method == 'POST':
        plan_id = request.POST['plan']
        monto_pagado = request.POST['monto_pagado']
        fecInicio = timezone.localdate()
        plan = Plan.objects.get(id=plan_id)
        fecFin = fecInicio + timedelta(days=plan.duracion)

        SocioPlan.objects.filter(socio=socio, estado=True).update(estado=False)

        SocioPlan.objects.create(
            socio=socio,
            plan=plan,
            fecInicio=fecInicio,
            fecFin=fecFin,
            monto_pagado=monto_pagado,
            estado=True
        )
        return redirect('lista_socios')

    return render(request, 'planes/asignar_plan.html', {'socio': socio, 'planes': planes})
