document.addEventListener('DOMContentLoaded', function() {
  Chart.register(ChartDataLabels);

  const {
    sociosPorPlan,
    ingresosPorPlan,
    meses,
    totalesMes,
    mesesCrec,
    datasetsCrec
  } = window.datosReportes;

  const colores = ['#007bff', '#ffc107', '#28a745', '#ff5722', '#7952b3'];

  const baseOptions = {
    responsive: true,
    plugins: { legend: { display: false } },
    animation: { duration: 800, easing: 'easeOutQuart' }
  };

  // 👥 Barras - socios por plan
  if (sociosPorPlan?.length) {
    new Chart(document.getElementById('grafico_socios_plan'), {
      type: 'bar',
      data: {
        labels: sociosPorPlan.map(p => p.plan),
        datasets: [{
          label: 'Socios',
          data: sociosPorPlan.map(p => p.cantidad),
          backgroundColor: colores,
          borderRadius: 6,
          borderWidth: 1,
          borderColor: '#fff'
        }]
      },
      options: baseOptions
    });
  }

  // 🥧 Donut - distribución socios
  if (sociosPorPlan?.length) {
    new Chart(document.getElementById('grafico_donut'), {
      type: 'doughnut',
      data: {
        labels: sociosPorPlan.map(p => p.plan),
        datasets: [{
          data: sociosPorPlan.map(p => p.cantidad),
          backgroundColor: colores
        }]
      },
      options: {
        ...baseOptions,
        plugins: {
          datalabels: {
            color: '#fff',
            formatter: (v, ctx) => {
              const total = ctx.chart._metasets[0].total || ctx.chart.getDatasetMeta(0).total;
              const pct = total ? ((v / total) * 100).toFixed(1) + '%' : '0%';
              return `${v} (${pct})`;
            },
            font: { weight: 'bold' }
          }
        },
        cutout: '60%'
      }
    });
  }

  // 📈 Línea - evolución mensual
  if (meses?.length && totalesMes?.length) {
    new Chart(document.getElementById('grafico_linea'), {
      type: 'line',
      data: {
        labels: meses,
        datasets: [{
          label: 'Socios activos',
          data: totalesMes,
          borderColor: '#007bff',
          backgroundColor: 'rgba(0,123,255,0.2)',
          tension: 0.3,
          fill: true,
          borderWidth: 2,
          pointRadius: 3
        }]
      },
      options: { ...baseOptions }
    });
  }

  // 📊 Apilado - crecimiento por plan
  if (mesesCrec?.length && datasetsCrec?.length) {
    new Chart(document.getElementById('grafico_area'), {
      type: 'bar',
      data: {
        labels: mesesCrec,
        datasets: datasetsCrec
      },
      options: {
        ...baseOptions,
        plugins: { legend: { position: 'bottom' } },
        scales: { x: { stacked: true }, y: { stacked: true } }
      }
    });
  }

  // 🧹 Botón "Limpiar filtros"
  const btnLimpiar = document.getElementById('btn-limpiar');
  if (btnLimpiar) {
    btnLimpiar.addEventListener('click', function() {
      // Redirige a la misma ruta sin parámetros GET
      window.location.href = window.location.pathname;
    });
  }

});
