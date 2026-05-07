const STATUS_POLL_MS = 1500;

function $(id) {
  return document.getElementById(id);
}

function setText(id, value) {
  const el = $(id);
  if (el) el.textContent = value;
}

function setHtml(id, value) {
  const el = $(id);
  if (el) el.innerHTML = value;
}

function badgeForServiceLevel(level) {
  const normalized = (level || '').toLowerCase();
  if (normalized === 'heavy') return 'Service: Heavy';
  if (normalized === 'moderate') return 'Service: Moderate';
  return 'Service: Light';
}

async function refreshPitxStatus() {
  try {
    const response = await fetch('/api/pitx-status', { cache: 'no-store' });
    if (!response.ok) throw new Error('Bad response');
    const data = await response.json();

    setText('timestampLabel', data.live.timestamp_label || '--');
    setText('peopleBadge', `People Count: ${data.live.people_count ?? '--'}`);
    setText('serviceLevelBadge', badgeForServiceLevel(data.prediction?.service_level));

    const wait = data.prediction?.estimated_wait_minutes;
    setHtml('waitBadge', `
      <div class="text-[11px] uppercase tracking-[0.22em] text-gray-500">Predictive AI</div>
      <div class="mt-1 text-lg font-semibold">PITX Estimated Wait: ${wait ?? '--'} mins</div>
    `);

    const suggestion = data.route_suggestion || {};
    if (suggestion.is_optimal) {
      setText('routeSuggestion', suggestion.message || 'Current route is optimal.');
      setText('timeSavedBadge', '0 mins saved');
    } else {
      setText('routeSuggestion', suggestion.message || 'Alternative route suggestion unavailable.');
      const saved = suggestion.time_saved_minutes ?? '--';
      setText('timeSavedBadge', `${saved} mins saved`);
    }
  } catch (err) {
    // Keep UI stable during transient failures
    console.error('PITX status update failed:', err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  refreshPitxStatus();
  setInterval(refreshPitxStatus, STATUS_POLL_MS);

  // If the MJPEG stream stalls, forcing a reload of the <img> can recover it.
  const video = document.getElementById('pitxVideo');
  if (video) {
    video.addEventListener('error', () => {
      const base = '/video_feed';
      video.src = `${base}?t=${Date.now()}`;
    });
  }
});

