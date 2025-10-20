from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Plan, SocioPlan
from apps.clientes.models import Socio
from datetime import datetime, timedelta



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

        Plan.objects.create(nombre=nombre, descripcion=descripcion, precio=precio, duracion=duracion)
        return redirect('lista_planes')
    return render(request, 'planes/form_plan.html')


@login_required
@user_passes_test(es_admin_o_superadmin)
def editar_plan(request, id):
    plan = get_object_or_404(Plan, id=id)
    if request.method == 'POST':
        plan.nombre = request.POST['nombre']
        plan.descripcion = request.POST.get('descripcion', '')
        plan.precio = request.POST['precio']
        plan.duracion = request.POST['duracion']
        plan.save()
        return redirect('lista_planes')
    return render(request, 'planes/form_plan.html', {'plan': plan})


@login_required
@user_passes_test(es_admin_o_superadmin)
def eliminar_plan(request, id):
    plan = get_object_or_404(Plan, id=id)
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
        fecInicio = datetime.now().date()

        plan = Plan.objects.get(id=plan_id)
        fecFin = fecInicio + timedelta(days=plan.duracion)

        # Desactivar plan anterior si existe
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
