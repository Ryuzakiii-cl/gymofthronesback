from django.shortcuts import render
from django.db.models import Count, Sum
from apps.clientes.models import Socio
from apps.planes.models import Plan, SocioPlan
from datetime import date

def dashboard_general(request):
    total_socios = Socio.objects.count()
    activos = Socio.objects.filter(estado=True).count()
    inactivos = Socio.objects.filter(estado=False).count()
    planes_activos = SocioPlan.objects.filter(estado=True).count()
    ingresos_mes = SocioPlan.objects.filter(
        fecInicio__month=date.today().month
    ).aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0

    plan_popular = SocioPlan.objects.values('plan__nombre').annotate(
        total=Count('plan')
    ).order_by('-total').first()

    contexto = {
        'total_socios': total_socios,
        'activos': activos,
        'inactivos': inactivos,
        'planes_activos': planes_activos,
        'ingresos_mes': ingresos_mes,
        'plan_popular': plan_popular['plan__nombre'] if plan_popular else 'Sin datos'
    }
    return render(request, 'core/dashboard.html', contexto)
