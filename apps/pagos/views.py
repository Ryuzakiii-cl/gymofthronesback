from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Pago
from apps.clientes.models import Socio
from apps.planes.models import Plan, SocioPlan
from datetime import date

# --- Permisos ---
def es_admin_o_superadmin(user):
    return user.is_authenticated and user.rol in ['admin', 'superadmin']

# --- LISTAR PAGOS ---
@login_required
@user_passes_test(es_admin_o_superadmin)
def lista_pagos(request):
    pagos = Pago.objects.select_related('socio', 'plan').order_by('-fecha_pago')
    return render(request, 'pagos/lista_pagos.html', {'pagos': pagos})

# --- CREAR PAGO ---
@login_required
@user_passes_test(es_admin_o_superadmin)
def crear_pago(request):
    socios = Socio.objects.filter(estado=True)
    planes = Plan.objects.all()

    if request.method == 'POST':
        socio_id = request.POST.get('socio')
        plan_id = request.POST.get('plan')
        monto = request.POST.get('monto')
        forma_pago = request.POST.get('forma_pago')
        observaciones = request.POST.get('observaciones')

        socio = get_object_or_404(Socio, id=socio_id)
        plan = get_object_or_404(Plan, id=plan_id)
        socio_plan = SocioPlan.objects.filter(socio=socio, plan=plan, estado=True).first()

        Pago.objects.create(
            socio=socio,
            plan=plan,
            socio_plan=socio_plan,
            monto=monto,
            forma_pago=forma_pago,
            observaciones=observaciones,
            estado='completado',
            fecha_pago=date.today()
        )

        messages.success(request, f"✅ Pago registrado correctamente para {socio.nombre}.")
        return redirect('lista_pagos')

    return render(request, 'pagos/crear_pago.html', {'socios': socios, 'planes': planes})

# --- EDITAR PAGO ---
@login_required
@user_passes_test(es_admin_o_superadmin)
def editar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    socios = Socio.objects.filter(estado=True)
    planes = Plan.objects.all()

    if request.method == 'POST':
        pago.socio_id = request.POST.get('socio')
        pago.plan_id = request.POST.get('plan')
        pago.monto = request.POST.get('monto')
        pago.forma_pago = request.POST.get('forma_pago')
        pago.observaciones = request.POST.get('observaciones')
        pago.save()

        messages.success(request, "✅ Pago actualizado correctamente.")
        return redirect('lista_pagos')

    return render(request, 'pagos/editar_pago.html', {'pago': pago, 'socios': socios, 'planes': planes})

# --- ELIMINAR PAGO ---
@login_required
@user_passes_test(es_admin_o_superadmin)
def eliminar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    pago.delete()
    messages.success(request, "🗑️ Pago eliminado correctamente.")
    return redirect('lista_pagos')
