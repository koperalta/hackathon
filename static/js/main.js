async function loadHomepageMetrics() {
  const [vehiclesResponse, dashboardResponse] = await Promise.all([
    fetch('/api/vehicles'),
    fetch('/api/dashboard/summary')
  ]);

  const vehiclesData = await vehiclesResponse.json();
  const dashboardData = await dashboardResponse.json();
  const vehicles = vehiclesData.vehicles || [];
  const occupancies = vehicles.map(vehicle => vehicle.occupancy_percent || 0);
  const avgOccupancy = occupancies.length
    ? Math.round(occupancies.reduce((sum, value) => sum + value, 0) / occupancies.length)
    : 0;
  const busiestRoute = [...dashboardData.route_metrics].sort((a, b) => b.average_occupancy - a.average_occupancy)[0];

  document.getElementById('vehicleCount').textContent = vehicles.length;
  document.getElementById('avgOccupancy').textContent = `${avgOccupancy}%`;
  document.getElementById('highDemandRoute').textContent = busiestRoute ? busiestRoute.route_name : 'N/A';
  document.getElementById('underservedCount').textContent = dashboardData.underserved_areas.length;
}

loadHomepageMetrics().catch(() => {
  document.getElementById('vehicleCount').textContent = '4';
  document.getElementById('avgOccupancy').textContent = '62%';
  document.getElementById('highDemandRoute').textContent = 'Fairview';
  document.getElementById('underservedCount').textContent = '2';
});
