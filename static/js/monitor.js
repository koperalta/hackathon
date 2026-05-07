const vehicleSelect = document.getElementById('vehicleSelect');
const statusSelect = document.getElementById('statusSelect');
const monitorFeed = document.getElementById('monitorFeed');
const videoPanel = document.getElementById('videoPanel');
let pollingHandle;
let currentSimulationMode = false;

function badgeClassForOccupancy(percent) {
  if (percent >= 90) return 'status-danger';
  if (percent >= 50) return 'status-bronze';
  if (percent >= 0) return 'status-gold';
  return 'status-neutral';
}

async function loadVehicles() {
  const response = await fetch('/api/vehicles');
  const data = await response.json();
  vehicleSelect.innerHTML = data.vehicles.map(vehicle => (
    `<option value="${vehicle.id}">${vehicle.id} · ${vehicle.route_name}</option>`
  )).join('');

  if (data.vehicles.length) {
    const currentVehicle = data.vehicles[0];
    statusSelect.value = currentVehicle.status;
    setFeedSource(currentVehicle.id, false);
    await refreshMonitor(false);
    startPolling();
  }
}

function setFeedSource(vehicleId, simulate) {
  currentSimulationMode = simulate;
  monitorFeed.src = `/api/monitor/frame?vehicle_id=${vehicleId}&simulate=${simulate}`;
}

function renderMonitor(data) {
  document.getElementById('passengerCount').textContent = data.occupancy.count;
  document.getElementById('visibleNowCount').textContent = data.occupancy.tracking.visible_now;
  document.getElementById('enteredCount').textContent = data.occupancy.tracking.entered;
  document.getElementById('passedByCount').textContent = data.occupancy.tracking.passed_by;
  document.getElementById('vehicleCapacity').textContent = data.vehicle.capacity;
  document.getElementById('occupancyPercent').textContent = `${data.occupancy.occupancy_percent}%`;
  document.getElementById('etaValue').textContent = `${data.prediction.eta_minutes} min`;
  document.getElementById('confidenceMetric').textContent = `${data.occupancy.confidence}%`;
  document.getElementById('trackingModeLabel').textContent =
    `${data.occupancy.tracking.tracking_mode} · line Y ${data.occupancy.tracking.line_position}`;

  const occupancyBadge = document.getElementById('occupancyBadge');
  occupancyBadge.textContent = data.occupancy.occupancy_level;
  occupancyBadge.className = `badge pill-badge ${badgeClassForOccupancy(data.occupancy.occupancy_percent)}`;

  const statusBadge = document.getElementById('statusBadge');
  statusBadge.textContent = data.vehicle.status;
  statusBadge.className = `badge pill-badge ${data.vehicle.status === 'Full' ? 'status-danger' : 'status-neutral'}`;

  const confidenceBadge = document.getElementById('confidenceBadge');
  confidenceBadge.textContent = `Confidence ${data.occupancy.confidence}%`;
  confidenceBadge.className = 'badge pill-badge status-neutral';

  const sourceBadge = document.getElementById('sourceBadge');
  sourceBadge.textContent = data.occupancy.source;
  sourceBadge.className = `badge pill-badge ${data.occupancy.tracking.camera_active ? 'status-gold' : 'status-neutral'}`;

  const cameraStateBadge = document.getElementById('cameraStateBadge');
  cameraStateBadge.textContent = data.occupancy.tracking.camera_active ? 'Camera Active' : 'Simulation Mode';
  cameraStateBadge.className = `badge pill-badge ${data.occupancy.tracking.camera_active ? 'status-gold' : 'status-neutral'}`;

  videoPanel.classList.toggle('active-tracking', data.occupancy.tracking.camera_active);

  document.getElementById('vehicleMeta').textContent =
    `${data.vehicle.type} on ${data.prediction.route_name} · ${data.prediction.recommendation} · exits ${data.occupancy.tracking.exited} · active tracks ${data.occupancy.tracking.active_tracks}`;
}

async function refreshMonitor(simulate) {
  const vehicleId = vehicleSelect.value;
  const response = await fetch('/api/monitor/status', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vehicle_id: vehicleId, simulate })
  });
  const data = await response.json();
  setFeedSource(vehicleId, simulate);
  renderMonitor(data);
}

async function updateVehicleStatus() {
  const vehicleId = vehicleSelect.value;
  const response = await fetch(`/api/vehicle/${vehicleId}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: statusSelect.value })
  });
  const data = await response.json();
  document.getElementById('statusBadge').textContent = data.vehicle.status;
  document.getElementById('statusBadge').className = `badge pill-badge ${data.vehicle.status === 'Full' ? 'status-danger' : 'status-neutral'}`;
  document.getElementById('vehicleMeta').textContent =
    `${data.vehicle.type} on ${data.prediction.route_name} · ${data.prediction.recommendation}`;
}

async function resetTracking() {
  const vehicleId = vehicleSelect.value;
  const response = await fetch('/api/monitor/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vehicle_id: vehicleId })
  });
  const data = await response.json();
  renderMonitor(data);
}

function startPolling() {
  if (pollingHandle) clearInterval(pollingHandle);
  pollingHandle = setInterval(async () => {
    try {
      const vehicleId = vehicleSelect.value;
      if (!vehicleId) return;
      const response = await fetch(`/api/monitor/status?vehicle_id=${vehicleId}&simulate=${currentSimulationMode}`);
      const data = await response.json();
      renderMonitor(data);
    } catch (error) {
      console.error(error);
    }
  }, 3000);
}

vehicleSelect.addEventListener('change', async (event) => {
  setFeedSource(event.target.value, false);
  await refreshMonitor(false);
});

document.getElementById('refreshOccupancyBtn').addEventListener('click', () => refreshMonitor(false));
document.getElementById('simulateOccupancyBtn').addEventListener('click', () => refreshMonitor(true));
document.getElementById('updateStatusBtn').addEventListener('click', updateVehicleStatus);
document.getElementById('resetTrackingBtn').addEventListener('click', resetTracking);

loadVehicles().catch(console.error);
