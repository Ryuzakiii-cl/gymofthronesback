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

  // 👥 Barras - socios por plan
  new Chart(document.getElementById('grafico_socios_plan'), {
    type: 'bar',
    data: {
      labels: sociosPorPlan.map(p => p.plan),
      datasets: [{
        label: 'Socios',
        data: sociosPorPlan.map(p => p.cantidad),
        backgroundColor: colores,
      }]
    },
    options: { plugins: { legend: { display: false } } }
  });

  // 🥧 Donut - distribución socios
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
      plugins: {
        datalabels: {
          color: '#fff',
          formatter: v => v,
          font: { weight: 'bold' }
        }
      },
      cutout: '60%'
    }
  });

  // 📈 Línea - evolución mensual
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
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } }
    }
  });

  // 📊 Apilado - crecimiento por plan
  new Chart(document.getElementById('grafico_area'), {
    type: 'bar',
    data: {
      labels: mesesCrec,
      datasets: datasetsCrec
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
      scales: { x: { stacked: true }, y: { stacked: true } }
    }
  });
});
