// static/js/commuter.js

const MONITOR_INTERVAL_MS = 3000; // Poll the edge cameras every 3 seconds
let activeReroute = false;

/**
 * Continuously polls the edge IoT simulation to monitor the queue vs. capacity.
 */
async function fetchLiveGateStatus() {
    try {
        // Fetching the simulated edge data from the Flask backend
        const response = await fetch('/api/monitor/status?vehicle_id=JEEP-001');
        const data = await response.json();

        updateLiveDeparturesBoard(data);

        // Core Logic: Trigger auto-reroute if occupancy hits "Siksikan" threshold
        if (data.occupancy.occupancy_percent >= 90 && !activeReroute) {
            await triggerAutoReroute();
        } else if (data.occupancy.occupancy_percent < 90 && activeReroute) {
            // Queue has cleared, reset the UI
            resetGateUI();
        }
    } catch (error) {
        console.error("Error fetching live gate status:", error);
    }
}

/**
 * Updates the standard data labels on the Gate Card.
 */
function updateLiveDeparturesBoard(data) {
    const queueLabel = document.getElementById('live-queue-count');
    const statusLabel = document.getElementById('live-gate-status');
    
    if (queueLabel) queueLabel.innerText = `${data.occupancy.count} pax`;
    if (statusLabel) statusLabel.innerText = data.occupancy.occupancy_level;
}

/**
 * Executes the visual transition and fetches the intelligent fallback route.
 */
async function triggerAutoReroute() {
    activeReroute = true;
    
    // 1. Instantly update the primary Gate Card border to Alert Red
    const gateCard = document.getElementById('primary-gate-card');
    if (gateCard) {
        gateCard.classList.remove('status-comfortable');
        gateCard.classList.add('status-siksikan');
    }

    // 2. Fetch Alternative Route via the Python AI Backend
    try {
        const response = await fetch('/api/commuter/recommendation?priority=least_crowded');
        const recommendation = await response.json();
        
        // 3. Inject the floating recommendation banner
        showRerouteBanner(recommendation.best_route);
    } catch (error) {
        console.error("Error calculating alternative route:", error);
    }
}

/**
 * Dynamically constructs and animates a floating banner to suggest the new route.
 */
function showRerouteBanner(bestRoute) {
    const boardContainer = document.getElementById('live-departures-board');
    if (!boardContainer) return;
    
    // Ensure we do not stack multiple banners
    if (document.getElementById('auto-reroute-banner')) return;

    const banner = document.createElement('div');
    banner.id = 'auto-reroute-banner';
    banner.className = 'reroute-banner slide-down-animation';
    
    // Constructing the HTML natively without reloading the page
    banner.innerHTML = `
        <div class="banner-content">
            <div class="banner-text">
                <h4 style="color: #FFC107; margin: 0; font-size: 16px;">✨ Magic Auto-Reroute Triggered</h4>
                <p style="margin: 4px 0 0; font-size: 14px; color: #E0E0E0;">
                    Gate queue is currently <strong>Siksikan</strong>. 
                    Switch to <strong>${bestRoute.route_name}</strong> at Gate 6. 
                    <br>Status: ${bestRoute.occupancy_level} (${bestRoute.occupancy_percent}%) | ETA: ${bestRoute.eta_minutes} min.
                </p>
            </div>
            <button class="accept-reroute-btn" onclick="acceptNewRoute()">Accept Seat</button>
        </div>
    `;
    
    // Insert the banner above the main board to adhere to the "Never hide the board" UX rule
    boardContainer.parentNode.insertBefore(banner, boardContainer);
}

function acceptNewRoute() {
    // Logic to confirm the new route and update the primary tracking view
    alert("Route updated successfully. Proceed to the new gate.");
    resetGateUI();
}

function resetGateUI() {
    activeReroute = false;
    const gateCard = document.getElementById('primary-gate-card');
    if (gateCard) {
        gateCard.classList.remove('status-siksikan');
        gateCard.classList.add('status-comfortable');
    }
    
    const banner = document.getElementById('auto-reroute-banner');
    if (banner) {
        banner.remove();
    }
}

// Boot up the monitoring loop when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    setInterval(fetchLiveGateStatus, MONITOR_INTERVAL_MS);
});