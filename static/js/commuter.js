let commuterMap;
let routeLayers = [];
let vehicleMarkers = [];

function getMarkerColor(percent) {
  if (percent >= 90) return '#ff4444';
  if (percent >= 50) return '#b8860b';
  return '#ffc107';
}

function createVehicleIcon(percent) {
  return L.divIcon({
    className: '',
    html: `<div style="background:${getMarkerColor(percent)};width:18px;height:18px;border-radius:50%;border:2px solid #000;box-shadow:0 0 10px ${getMarkerColor(percent)};"></div>`,
    iconSize: [18, 18]
  });
}

async function loadVehiclesAndMap() {
  const response = await fetch('/api/vehicles');
  const data = await response.json();
  const vehicles = data.vehicles || [];
  const reportVehicleSelect = document.getElementById('reportVehicleSelect');
  reportVehicleSelect.innerHTML = vehicles.map(vehicle => (
    `<option value="${vehicle.id}">${vehicle.id} · ${vehicle.prediction.route_name}</option>`
  )).join('');

  if (!commuterMap) {
    commuterMap = L.map('commuterMap').setView([14.645, 121.055], 11);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
    }).addTo(commuterMap);
  }

  routeLayers.forEach(layer => commuterMap.removeLayer(layer));
  vehicleMarkers.forEach(marker => commuterMap.removeLayer(marker));
  routeLayers = [];
  vehicleMarkers = [];

  vehicles.forEach(vehicle => {
    const path = vehicle.route_name;
    const popupHtml = `
      <strong>${vehicle.id}</strong><br>
      ${path}<br>
      ETA: ${vehicle.prediction.eta_minutes} min<br>
      Occupancy: ${vehicle.occupancy_percent}%<br>
      Fare: PHP ${vehicle.prediction.fare}<br>
      Status: ${vehicle.status}
    `;
    const marker = L.marker([vehicle.lat, vehicle.lng], { icon: createVehicleIcon(vehicle.occupancy_percent) })
      .addTo(commuterMap)
      .bindPopup(popupHtml);
    vehicleMarkers.push(marker);
  });

  vehicles.forEach(vehicle => {
    if (routeLayers.some(layer => layer.routeId === vehicle.route_id)) return;
    const latlngs = vehicle.route_path.map(point => [point[0], point[1]]);
    const layer = L.polyline(latlngs, {
      color: '#ffc107',
      weight: 6,
      opacity: 0.88
    }).addTo(commuterMap);
    layer.routeId = vehicle.route_id;
    layer.bindPopup(`<strong>${vehicle.route_name}</strong><br>${vehicle.type} corridor`);
    routeLayers.push(layer);
  });
}

function renderRecommendation(data) {
  const best = data.best_route;
  const bestRouteCard = document.getElementById('bestRouteCard');
  bestRouteCard.innerHTML = `
    <div class="mono-label mb-2">Magic Route Match</div>
    <div class="fw-bold fs-5 mb-2 text-gold">${best.route_name}</div>
    <div class="mb-2 text-secondary">${best.mode} · ${best.status}</div>
    <div class="mb-2">ETA: <strong>${best.eta_minutes} min</strong></div>
    <div class="mb-2">Fare: <strong>PHP ${best.fare}</strong></div>
    <div class="mb-2">Occupancy: <strong>${best.occupancy_percent}%</strong></div>
    <div class="text-secondary">${best.recommendation_reason}</div>
  `;
  bestRouteCard.className = `route-card fleet-card rounded-4 p-3 ${best.occupancy_percent > 90 ? 'full-route' : ''}`;

  document.getElementById('alternativeRoutes').innerHTML = data.alternatives.map(route => `
    <div class="route-card fleet-card rounded-4 p-3 ${route.occupancy_percent > 90 ? 'full-route' : ''}">
      <div class="fw-semibold text-gold">${route.route_name}</div>
      <div class="small text-secondary">${route.mode} · ETA ${route.eta_minutes} min · ${route.occupancy_percent}% full</div>
    </div>
  `).join('');
}

async function getRecommendation() {
  const priority = document.getElementById('prioritySelect').value;
  const response = await fetch(`/api/commuter/recommendation?priority=${priority}`);
  const data = await response.json();
  renderRecommendation(data);
}

async function submitReport() {
  const payload = {
    vehicle_id: document.getElementById('reportVehicleSelect').value,
    report_type: document.getElementById('reportTypeSelect').value,
    barangay: document.getElementById('barangayInput').value || 'Community Report',
    wait_minutes: 12
  };

  const response = await fetch('/api/commuter/report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  document.getElementById('reportResult').textContent = `${data.message}: ${data.report_type} for ${data.vehicle_id}`;
}

document.getElementById('getRecommendationBtn').addEventListener('click', getRecommendation);
document.getElementById('submitReportBtn').addEventListener('click', submitReport);
document.getElementById('refreshMapBtn').addEventListener('click', loadVehiclesAndMap);

Promise.all([loadVehiclesAndMap(), getRecommendation()]).catch(console.error);
