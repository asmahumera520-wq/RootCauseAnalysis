/* history.js – fetches and lists all past incidents */

const API_BASE = 'http://localhost:5000';

function showToast(message, type = 'error') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
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

async function deleteIncident(id, cardEl) {
  if (!confirm('Delete this incident and its RCA? This cannot be undone.')) return;
  try {
    await fetch(`${API_BASE}/api/incidents/${id}`, { method: 'DELETE' });
    cardEl.style.animation = 'fadeIn 0.3s ease reverse';
    setTimeout(() => {
      cardEl.remove();
      if (!document.querySelector('.history-card')) renderEmpty();
    }, 280);
    showToast('Incident deleted.', 'success');
  } catch (err) {
    showToast('Failed to delete.', 'error');
  }
}

function renderEmpty() {
  document.getElementById('incidentList').innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">📂</div>
      <h3>No incidents yet</h3>
      <p>Submit your first incident to see it here.</p>
      <a href="/" class="btn-secondary" style="margin-top:1rem;">＋ New Incident</a>
    </div>`;
}

async function loadHistory() {
  try {
    const res  = await fetch(`${API_BASE}/api/incidents`);
    const data = await res.json();
    const list = document.getElementById('incidentList');

    if (!data.length) { renderEmpty(); return; }

    list.innerHTML = '';
    data.forEach(incident => {
      const card = document.createElement('div');
      card.className = 'history-card fade-in';

      card.innerHTML = `
        <div class="history-card-info">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <span class="badge ${severityClass(incident.severity)}">${incident.severity}</span>
            <div class="history-card-title">${incident.title}</div>
          </div>
          <div class="history-card-date">
            📅 ${formatDate(incident.incident_date || incident.created_at)}
            ${incident.affected_systems ? ` &nbsp;|&nbsp; 🖥️ ${incident.affected_systems}` : ''}
          </div>
        </div>
        <div class="history-card-actions">
          <a href="/report?id=${incident.id}" class="btn-secondary">View RCA →</a>
          <button class="btn-danger" onclick="deleteIncident(${incident.id}, this.closest('.history-card'))">🗑️ Delete</button>
        </div>
      `;

      list.appendChild(card);
    });

  } catch (err) {
    showToast(`Failed to load history: ${err.message}`, 'error');
    renderEmpty();
  }
}

loadHistory();
