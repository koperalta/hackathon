let crowdingChart;
let opportunityChart;

function average(values) {
  if (!values.length) return 0;
  return Math.round(values.reduce((sum, value) => sum + value, 0) / values.length);
}

function renderList(elementId, items, formatter) {
  document.getElementById(elementId).innerHTML = items.map(formatter).join('');
}

async function loadDashboard() {
  const response = await fetch('/api/dashboard/summary');
  const data = await response.json();

  const occupancies = data.route_metrics.map(item => item.average_occupancy);
  const waits = data.route_metrics.map(item => item.average_wait);
  const topRoute = [...data.route_metrics].sort((a, b) => b.average_occupancy - a.average_occupancy)[0];

  document.getElementById('avgWaitCard').textContent = `${average(waits)} min`;
  document.getElementById('peakCrowdingCard').textContent = `${occupancies.length ? Math.max(...occupancies) : 0}%`;
  document.getElementById('topRouteCard').textContent = topRoute ? topRoute.route_name : 'N/A';
  document.getElementById('underservedCard').textContent = data.underserved_areas.length;

  const crowdingContext = document.getElementById('crowdingChart');
  if (crowdingChart) crowdingChart.destroy();
  crowdingChart = new Chart(crowdingContext, {
    type: 'bar',
    data: {
      labels: data.route_metrics.map(item => item.route_name),
      datasets: [
        {
          label: 'Average Occupancy %',
          data: data.route_metrics.map(item => item.average_occupancy),
          backgroundColor: ['#ffc107', '#d4a017', '#b8860b', '#ff4444']
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: '#ffffff' } }
      },
      scales: {
        x: { ticks: { color: '#e0e0e0' }, grid: { color: '#333333' } },
        y: { beginAtZero: true, max: 100, ticks: { color: '#e0e0e0' }, grid: { color: '#333333' } }
      }
    }
  });

  const opportunityContext = document.getElementById('opportunityChart');
  if (opportunityChart) opportunityChart.destroy();
  opportunityChart = new Chart(opportunityContext, {
    type: 'line',
    data: {
      labels: data.opportunity_scores.slice(0, 8).map(item => item.barangay),
      datasets: [
        {
          label: 'Opportunity Mobility Score',
          data: data.opportunity_scores.slice(0, 8).map(item => item.score),
          borderColor: '#ffc107',
          backgroundColor: 'rgba(255,193,7,.15)',
          fill: true,
          tension: 0.35
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: '#ffffff' } }
      },
      scales: {
        x: { ticks: { color: '#e0e0e0' }, grid: { color: '#333333' } },
        y: { beginAtZero: true, max: 100, ticks: { color: '#e0e0e0' }, grid: { color: '#333333' } }
      }
    }
  });

  renderList('insightsList', data.insights, insight => `<li>${insight}</li>`);
  renderList(
    'dispatchList',
    data.dispatch_recommendations,
    item => `<li><strong>${item.route_name}:</strong> ${item.action}</li>`
  );

  document.getElementById('underservedTableBody').innerHTML = data.underserved_areas.map(item => `
    <tr>
      <td>${item.barangay}</td>
      <td>${item.route_name}</td>
      <td>${item.score}</td>
      <td>${item.label}</td>
      <td>${item.average_wait} min</td>
      <td>${item.average_crowding}%</td>
    </tr>
  `).join('');
}

document.getElementById('refreshDashboardBtn').addEventListener('click', loadDashboard);
loadDashboard().catch(console.error);
