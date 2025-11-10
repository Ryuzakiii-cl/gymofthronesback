from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone 
from .models import Pago
from apps.socios.models import Socio
from apps.planes.models import Plan, SocioPlan
from apps.core.utils import formatear_numero
from apps.core.decorators import es_socio


# --- Permisos ---
def es_admin_o_superadmin(user):
    return user.is_authenticated and user.rol in ['admin', 'superadmin']



# ===============================
# CRUD DE PAGOS
# ===============================

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
            fecha_pago=timezone.localdate()  
        )

        return redirect('/pagos/?success=created')

    return render(request, 'pagos/crear_pago.html', {'socios': socios, 'planes': planes})

# --- LISTAR PAGOS ---
@login_required
@user_passes_test(es_admin_o_superadmin)
def lista_pagos(request):
    pagos = Pago.objects.select_related('socio', 'plan').order_by('-fecha_pago')

    # Formatea el monto con separador de miles
    for p in pagos:
        p.monto_formateado = formatear_numero(p.monto)

    return render(request, 'pagos/lista_pagos.html', {'pagos': pagos})


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

        return redirect('/pagos/?success=updated')

    return render(request, 'pagos/editar_pago.html', {'pago': pago, 'socios': socios, 'planes': planes})


# --- ELIMINAR PAGO ---
@login_required
@user_passes_test(es_admin_o_superadmin)
def eliminar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    pago.delete()
    return redirect('/pagos/?success=deleted')




@login_required
@user_passes_test(es_socio)
def pagos_socio(request):
    """Muestra solo los pagos del socio autenticado."""
    pagos = Pago.objects.filter(socio__rut=request.user.rut).order_by('-fecha_pago')

    # Opcional: cálculo total de lo pagado
    total_pagado = 0
    for p in pagos:
        p.monto_formateado = formatear_numero(p.monto)
        total_pagado += p.monto

    context = {
        'pagos': pagos,
        'total_pagado': formatear_numero(total_pagado),
    }
    return render(request, 'pagos/pagos_socio.html', context)