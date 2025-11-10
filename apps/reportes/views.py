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

# ==============================================================
#   DECORADOR DE ROL
# ==============================================================

def es_admin_o_superadmin(user):
    return user.is_authenticated and getattr(user, 'rol', None) in ['admin', 'superadmin']

# ==============================================================
#   UTILIDAD: FORMATO DE NÚMERO CHILENO
# ==============================================================

def formatear_numero(valor):
    """Convierte un número a formato chileno (1.234.567)"""
    try:
        return f"{valor:,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"

# ==============================================================
#   DASHBOARD DE REPORTES
# ==============================================================

@login_required
@user_passes_test(es_admin_o_superadmin)
def dashboard_reportes(request):
    """Vista principal del dashboard con métricas e indicadores clave."""
    hoy = timezone.localdate()
    inicio_str = request.GET.get('inicio')
    fin_str = request.GET.get('fin')
    tipo = request.GET.get('tipo', 'socios')

    # --- Rango de fechas ---
    try:
        inicio = timezone.datetime.strptime(inicio_str, "%Y-%m-%d").date() if inicio_str else hoy - timedelta(days=180)
        fin = timezone.datetime.strptime(fin_str, "%Y-%m-%d").date() if fin_str else hoy
    except ValueError:
        inicio, fin = hoy - timedelta(days=180), hoy

    # ==========================================================
    # 🔹 MÉTRICAS PRINCIPALES
    # ==========================================================
    socios_activos = Socio.objects.filter(estado=True).count()
    talleres_activos = Taller.objects.filter(activo=True).count()
    canchas_totales = Cancha.objects.count()

    # Ingresos totales
    ingresos_totales_val = (
        Pago.objects.filter(estado='completado', fecha_pago__range=(inicio, fin))
        .aggregate(Sum('monto'))['monto__sum'] or 0
    )

    # Reservas totales y ocupación
    reservas_totales = Reserva.objects.filter(fecha__range=(inicio, fin)).count()
    reservas_hoy = Reserva.objects.filter(fecha=hoy).count()
    ocupacion = round((reservas_hoy / canchas_totales) * 100, 1) if canchas_totales > 0 else 0.0

    # Ingreso promedio por socio
    ingreso_promedio = ingresos_totales_val / socios_activos if socios_activos > 0 else 0

    # Planes activos y vencidos
    planes_activos = SocioPlan.objects.filter(estado=True).count()
    planes_vencidos = SocioPlan.objects.filter(estado=False).count()

    # ==========================================================
    # 🔹 GRÁFICO 1: SOCIOS POR PLAN
    # ==========================================================
    socios_por_plan_qs = (
        SocioPlan.objects.filter(estado=True)
        .values('plan__nombre')
        .annotate(cantidad=Count('id'))
        .order_by('plan__nombre')
    )
    socios_por_plan = list(socios_por_plan_qs)

    # ==========================================================
    # 🔹 GRÁFICO 2: INGRESOS POR PLAN (OPTIMIZADO)
    # ==========================================================
    ingresos_por_plan_qs = (
        Pago.objects.filter(estado='completado', fecha_pago__range=(inicio, fin))
        .values('plan__nombre')
        .annotate(total=Sum('monto'))
        .order_by('plan__nombre')
    )
    ingresos_por_plan = [
        {'plan': p['plan__nombre'], 'monto': int(p['total'] or 0)}
        for p in ingresos_por_plan_qs
    ]

    # ==========================================================
    # 🔹 GRÁFICO 3: EVOLUCIÓN MENSUAL DE SOCIOS NUEVOS
    # ==========================================================
    evolucion = (
        Socio.objects.filter(fec_registro__range=(inicio, fin))
        .annotate(mes=TruncMonth('fec_registro'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    meses = [e['mes'].strftime('%b %Y') for e in evolucion]
    totales_mes = [e['total'] for e in evolucion]

    # ==========================================================
    # 🔹 GRÁFICO 4: CRECIMIENTO DE PLANES POR MES
    # ==========================================================
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

    # ==========================================================
    # CONTEXTO PARA TEMPLATE
    # ==========================================================
    context = {
        'inicio': inicio,
        'fin': fin,
        'tipo': tipo,

        # Números formateados
        'socios_activos': formatear_numero(socios_activos),
        'ingresos_totales': formatear_numero(ingresos_totales_val),
        'reservas_totales': formatear_numero(reservas_totales),
        'clases_activas': formatear_numero(talleres_activos),
        'ocupacion': f"{ocupacion:.1f}",
        'ingreso_promedio': formatear_numero(ingreso_promedio),
        'planes_activos': formatear_numero(planes_activos),
        'planes_vencidos': formatear_numero(planes_vencidos),

        # JSON para gráficos
        'socios_por_plan': json.dumps(socios_por_plan),
        'ingresos_por_plan': json.dumps(ingresos_por_plan),
        'meses': json.dumps(meses),
        'totales_mes': json.dumps(totales_mes),
        'meses_crecimiento': json.dumps(meses_crecimiento),
        'datasets_crecimiento': json.dumps(datasets_crecimiento),
    }

    return render(request, 'reportes/dashboard_reportes.html', context)

# ==============================================================
#   EXPORTACIÓN A EXCEL
# ==============================================================

@login_required
@user_passes_test(es_admin_o_superadmin)
def exportar_excel(request):
    """Exporta información en formato Excel según el tipo seleccionado."""
    tipo = request.GET.get('tipo', 'socios')
    hoy = timezone.localdate().strftime("%Y-%m-%d")

    if tipo == 'socios':
        data = Socio.objects.values('rut', 'nombre', 'apellido_paterno', 'correo', 'estado')
    elif tipo == 'finanzas':
        data = Pago.objects.values('socio__nombre', 'plan__nombre', 'monto', 'forma_pago', 'fecha_pago')
    else:
        data = Reserva.objects.values('socio__nombre', 'cancha__nombre', 'fecha', 'hora_inicio', 'hora_fin', 'estado')

    # Validar si hay registros
    if not data.exists():
        response = HttpResponse("No hay datos para exportar en este período.", content_type="text/plain")
        return response

    # Generar Excel con Pandas
    df = pd.DataFrame(list(data))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Reporte_{tipo}_{hoy}.xlsx"'
    df.to_excel(response, index=False)
    return response
