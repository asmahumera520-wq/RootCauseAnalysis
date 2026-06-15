/* report.js – loads and renders an RCA report by incident ID */

const API_BASE = 'http://localhost:5000';

// Read ?id=N from the URL
const params     = new URLSearchParams(window.location.search);
const incidentId = params.get('id');

function showToast(message, type = 'error') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4500);
}

function severityClass(sev) {
  const map = { P1: 'badge-p1', P2: 'badge-p2', P3: 'badge-p3' };
  return map[sev] || 'badge-p2';
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return isNaN(d) ? dateStr : d.toLocaleString();
}

async function loadReport() {
  if (!incidentId) {
    document.getElementById('rcaContent').innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">❌</div>
        <h3>No Incident ID</h3>
        <p>Please go back and submit an incident first.</p>
        <a href="/" class="btn-secondary" style="margin-top:1rem;">← Back to Form</a>
      </div>`;
    return;
  }

  try {
    const res  = await fetch(`${API_BASE}/api/incidents/${incidentId}`);
    const data = await res.json();

    if (data.error) throw new Error(data.error);

    // ── Update page title ─────────────────────────────────────────────
    document.title = `${data.title} — RCA Drafter`;
    document.getElementById('reportTitle').textContent = data.title;

    const sev = data.severity || 'P2';
    const badge = document.getElementById('severityBadge');
    badge.textContent = sev;
    badge.className   = `badge ${severityClass(sev)}`;

    // ── Meta strip ────────────────────────────────────────────────────
    document.getElementById('metaSeverity').textContent  = sev;
    document.getElementById('metaDate').textContent      = formatDate(data.incident_date);
    document.getElementById('metaSystems').textContent   = data.affected_systems || '—';
    document.getElementById('metaGenerated').textContent = data.rca
      ? formatDate(data.rca.generated_at)
      : '—';
    document.getElementById('reportMeta').style.display  = 'flex';

    // ── Render RCA markdown ───────────────────────────────────────────
    if (data.rca && data.rca.full_report_text) {
      // Configure marked for security
      marked.setOptions({ breaks: true, gfm: true });
      document.getElementById('rcaContent').innerHTML = marked.parse(data.rca.full_report_text);
    } else {
      document.getElementById('rcaContent').innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">⚠️</div>
          <h3>No RCA Found</h3>
          <p>The RCA for this incident has not been generated yet.</p>
        </div>`;
    }

  } catch (err) {
    document.getElementById('rcaContent').innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">❌</div>
        <h3>Failed to Load Report</h3>
        <p>${err.message}</p>
        <a href="/" class="btn-secondary" style="margin-top:1rem;">← Back to Form</a>
      </div>`;
    showToast(`Error: ${err.message}`, 'error');
  }
}

function printReport() {
  window.print();
}

loadReport();
