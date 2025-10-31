from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.utils import timezone 
from datetime import timedelta
from django.db.models.functions import TruncMonth
from apps.clientes.models import Socio
from apps.pagos.models import Pago
from apps.reservas.models import Reserva, Taller, Cancha
from apps.planes.models import Plan, SocioPlan
import pandas as pd
from django.http import HttpResponse
import json
from decimal import Decimal




def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def es_admin_o_superadmin(user):
    return user.is_authenticated and user.rol in ['admin', 'superadmin']


@login_required
@user_passes_test(es_admin_o_superadmin)
def dashboard_reportes(request):
    hoy = timezone.localdate()
    inicio_str = request.GET.get('inicio')
    fin_str = request.GET.get('fin')
    tipo = request.GET.get('tipo', 'socios')

    try:

        inicio = timezone.datetime.strptime(inicio_str, "%Y-%m-%d").date() if inicio_str else hoy - timedelta(days=180)
        fin = timezone.datetime.strptime(fin_str, "%Y-%m-%d").date() if fin_str else hoy
    except ValueError:
        inicio, fin = hoy - timedelta(days=180), hoy

    # --- Datos base ---
    socios_activos = Socio.objects.filter(estado=True).count()
    ingresos_totales = Pago.objects.filter(
        estado='completado', fecha_pago__range=(inicio, fin)
    ).aggregate(Sum('monto'))['monto__sum'] or 0

    reservas_totales = Reserva.objects.filter(fecha__range=(inicio, fin)).count()
    talleres_activos = Taller.objects.filter(activo=True).count()
    canchas_totales = Cancha.objects.count()

    # Ocupación actual
    reservas_hoy = Reserva.objects.filter(fecha=hoy).count()
    ocupacion = round((reservas_hoy / canchas_totales) * 100, 1) if canchas_totales > 0 else 0

    # --- Gráfico 1: socios por plan ---
    planes = Plan.objects.all()
    socios_por_plan = []
    for plan in planes:
        cantidad = SocioPlan.objects.filter(plan=plan, estado=True).count()
        socios_por_plan.append({'plan': plan.nombre, 'cantidad': cantidad})

    # --- Gráfico 2: ingresos por plan ---
    ingresos_por_plan = []
    for plan in planes:
        total = Pago.objects.filter(
            plan=plan, estado='completado', fecha_pago__range=(inicio, fin)
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        ingresos_por_plan.append({'plan': plan.nombre, 'monto': total})

    # --- Gráfico 3: evolución mensual de socios ---
    evolucion = (
        Socio.objects.filter(fec_registro__range=(inicio, fin))
        .annotate(mes=TruncMonth('fec_registro'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    meses = [e['mes'].strftime('%b %Y') for e in evolucion]
    totales_mes = [e['total'] for e in evolucion]

    # --- Gráfico 4: crecimiento apilado por plan ---
    crecimiento = (
        SocioPlan.objects.filter(fecInicio__range=(inicio, fin))
        .annotate(mes=TruncMonth('fecInicio'))
        .values('mes', 'plan__nombre')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    # Organizar datos para Chart.js
    series = {}
    for c in crecimiento:
        plan = c['plan__nombre']
        mes = c['mes'].strftime('%b %Y')
        if plan not in series:
            series[plan] = {}
        series[plan][mes] = c['total']

    meses_crecimiento = sorted(set(m for c in series.values() for m in c))
    datasets_crecimiento = []
    colores = ['#ffc107', '#28a745', '#007bff', '#ff5722', '#7952b3']
    for i, (plan, data) in enumerate(series.items()):
        valores = [data.get(m, 0) for m in meses_crecimiento]
        datasets_crecimiento.append({
            'label': plan,
            'data': valores,
            'backgroundColor': colores[i % len(colores)],
            'fill': True
        })

    context = {
        'inicio': inicio,
        'fin': fin,
        'tipo': tipo,
        'socios_activos': socios_activos,
        'ingresos_totales': ingresos_totales,
        'reservas_totales': reservas_totales,
        'talleres_activos': talleres_activos,
        'ocupacion': ocupacion,

        'socios_por_plan': json.dumps(socios_por_plan, default=decimal_default),
        'ingresos_por_plan': json.dumps(ingresos_por_plan, default=decimal_default),
        'meses': json.dumps(meses, default=decimal_default),
        'totales_mes': json.dumps(totales_mes, default=decimal_default),
        'meses_crecimiento': json.dumps(meses_crecimiento, default=decimal_default),
        'datasets_crecimiento': json.dumps(datasets_crecimiento, default=decimal_default),
    }


    return render(request, 'reportes/dashboard_reportes.html', context)


@login_required
@user_passes_test(es_admin_o_superadmin)
def exportar_excel(request):
    tipo = request.GET.get('tipo', 'socios')
    hoy = timezone.localdate().strftime("%Y-%m-%d")  # ✅ usa timezone

    if tipo == 'socios':
        data = Socio.objects.values('rut', 'nombre', 'apellido_paterno', 'correo', 'estado')
        df = pd.DataFrame(data)
    elif tipo == 'finanzas':
        data = Pago.objects.values('socio__nombre', 'plan__nombre', 'monto', 'forma_pago', 'fecha_pago')
        df = pd.DataFrame(data)
    else:
        data = Reserva.objects.values('socio__nombre', 'cancha__nombre', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
        df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Reporte_{tipo}_{hoy}.xlsx"'
    df.to_excel(response, index=False)
    return response
