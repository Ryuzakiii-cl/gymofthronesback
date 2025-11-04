import json
from datetime import timedelta
from decimal import Decimal
import pandas as pd

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from apps.canchas.models import Cancha, Reserva
from apps.pagos.models import Pago
from apps.planes.models import Plan, SocioPlan
from apps.socios.models import Socio
from apps.talleres.models import Taller


def es_admin_o_superadmin(user):
    return user.is_authenticated and user.rol in ['admin', 'superadmin']


def formatear_numero(valor):
    """Convierte número a formato chileno: 1.234.567,89"""
    try:
        return f"{valor:,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


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
    ingresos_totales_val = (
        Pago.objects.filter(estado='completado', fecha_pago__range=(inicio, fin))
        .aggregate(Sum('monto'))['monto__sum'] or 0
    )
    reservas_totales = Reserva.objects.filter(fecha__range=(inicio, fin)).count()
    talleres_activos = Taller.objects.filter(activo=True).count()
    canchas_totales = Cancha.objects.count()

    # Ocupación actual (% con decimal)
    reservas_hoy = Reserva.objects.filter(fecha=hoy).count()
    ocupacion = round((reservas_hoy / canchas_totales) * 100, 1) if canchas_totales > 0 else 0.0

    # --- Gráfico 1: socios por plan ---
    planes = Plan.objects.all()
    socios_por_plan = [
        {'plan': plan.nombre, 'cantidad': SocioPlan.objects.filter(plan=plan, estado=True).count()}
        for plan in planes
    ]

    # --- Gráfico 2: ingresos por plan ---
    ingresos_por_plan = []
    for plan in planes:
        total = (
            Pago.objects.filter(plan=plan, estado='completado', fecha_pago__range=(inicio, fin))
            .aggregate(Sum('monto'))['monto__sum'] or 0
        )
        ingresos_por_plan.append({'plan': plan.nombre, 'monto': int(total)})

    # --- Gráfico 3: evolución mensual ---
    evolucion = (
        Socio.objects.filter(fec_registro__range=(inicio, fin))
        .annotate(mes=TruncMonth('fec_registro'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    meses = [e['mes'].strftime('%b %Y') for e in evolucion]
    totales_mes = [e['total'] for e in evolucion]

    # --- Gráfico 4: crecimiento por plan ---
    crecimiento = (
        SocioPlan.objects.filter(fecInicio__range=(inicio, fin))
        .annotate(mes=TruncMonth('fecInicio'))
        .values('mes', 'plan__nombre')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    series = {}
    for c in crecimiento:
        plan = c['plan__nombre']
        mes = c['mes'].strftime('%b %Y')
        series.setdefault(plan, {})[mes] = c['total']

    meses_crecimiento = sorted(set(m for c in series.values() for m in c))
    colores = ['#ffc107', '#28a745', '#007bff', '#ff5722', '#7952b3']

    datasets_crecimiento = [
        {
            'label': plan,
            'data': [data.get(m, 0) for m in meses_crecimiento],
            'backgroundColor': colores[i % len(colores)],
            'fill': True
        }
        for i, (plan, data) in enumerate(series.items())
    ]

    # --- Contexto ---
    context = {
        'inicio': inicio,
        'fin': fin,
        'tipo': tipo,

        # ✅ Números formateados
        'socios_activos': formatear_numero(socios_activos),
        'ingresos_totales': formatear_numero(ingresos_totales_val),
        'reservas_totales': formatear_numero(reservas_totales),
        'clases_activas': formatear_numero(talleres_activos),
        'ocupacion': f"{ocupacion:.1f}",

        # ✅ JSON para gráficos
        'socios_por_plan': json.dumps(socios_por_plan),
        'ingresos_por_plan': json.dumps(ingresos_por_plan),
        'meses': json.dumps(meses),
        'totales_mes': json.dumps(totales_mes),
        'meses_crecimiento': json.dumps(meses_crecimiento),
        'datasets_crecimiento': json.dumps(datasets_crecimiento),
    }

    return render(request, 'reportes/dashboard_reportes.html', context)



@login_required
@user_passes_test(es_admin_o_superadmin)
def exportar_excel(request):
    tipo = request.GET.get('tipo', 'socios')
    hoy = timezone.localdate().strftime("%Y-%m-%d")

    if tipo == 'socios':
        data = Socio.objects.values('rut', 'nombre', 'apellido_paterno', 'correo', 'estado')
    elif tipo == 'finanzas':
        data = Pago.objects.values('socio__nombre', 'plan__nombre', 'monto', 'forma_pago', 'fecha_pago')
    else:
        data = Reserva.objects.values('socio__nombre', 'cancha__nombre', 'fecha', 'hora_inicio', 'hora_fin', 'estado')

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Reporte_{tipo}_{hoy}.xlsx"'
    df.to_excel(response, index=False)
    return response
