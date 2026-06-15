/* form.js – handles incident form submission */

const API_BASE = 'http://localhost:5000';

// ── File upload: show filename when selected ─────────────────────────────
document.getElementById('log_file').addEventListener('change', function () {
  const name = this.files[0]?.name || '';
  document.getElementById('logFileName').textContent = name ? `✓ ${name}` : '';
});

document.getElementById('diff_file').addEventListener('change', function () {
  const name = this.files[0]?.name || '';
  document.getElementById('diffFileName').textContent = name ? `✓ ${name}` : '';
});

// ── Drag-and-drop highlight ──────────────────────────────────────────────
['logUploadBox', 'diffUploadBox'].forEach(id => {
  const box = document.getElementById(id);
  box.addEventListener('dragover',  e => { e.preventDefault(); box.classList.add('dragover'); });
  box.addEventListener('dragleave', ()  => box.classList.remove('dragover'));
  box.addEventListener('drop',      e => { e.preventDefault(); box.classList.remove('dragover'); });
});

// ── Loading overlay steps animation ─────────────────────────────────────
function animateLoadingSteps() {
  const steps = ['step1','step2','step3','step4','step5'];
  let i = 0;
  const interval = setInterval(() => {
    if (i > 0) document.getElementById(steps[i-1])?.classList.remove('active');
    if (i < steps.length) {
      document.getElementById(steps[i])?.classList.add('active');
      i++;
    } else {
      clearInterval(interval);
    }
  }, 1800);
}

// ── Toast helper ─────────────────────────────────────────────────────────
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// ── Form submission ──────────────────────────────────────────────────────
document.getElementById('incidentForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  // Basic validation
  const title    = document.getElementById('title').value.trim();
  const timeline = document.getElementById('timeline').value.trim();

  if (!title) {
    showToast('Please enter an Incident Title.', 'error');
    document.getElementById('title').focus();
    return;
  }
  if (!timeline) {
    showToast('Please enter the Incident Timeline.', 'error');
    document.getElementById('timeline').focus();
    return;
  }

  // Show loading overlay
  const overlay = document.getElementById('loadingOverlay');
  overlay.classList.add('active');
  document.getElementById('generateBtn').disabled = true;
  animateLoadingSteps();

  // Build form data (supports file uploads)
  const formData = new FormData();
  formData.append('title',            title);
  formData.append('severity',         document.getElementById('severity').value);
  formData.append('incident_date',    document.getElementById('incident_date').value);
  formData.append('affected_systems', document.getElementById('affected_systems').value.trim());
  formData.append('timeline',         timeline);

  const logFile  = document.getElementById('log_file').files[0];
  const diffFile = document.getElementById('diff_file').files[0];
  if (logFile)  formData.append('log_file',  logFile);
  if (diffFile) formData.append('diff_file', diffFile);

  try {
    const response = await fetch(`${API_BASE}/api/generate-rca`, {
      method: 'POST',
      body:   formData,
    });

    const data = await response.json();

    if (data.success) {
      showToast('RCA generated successfully! Redirecting…', 'success');
      setTimeout(() => {
        window.location.href = `/report?id=${data.incident_id}`;
      }, 800);
    } else {
      throw new Error(data.error || 'Unknown error from server.');
    }

  } catch (err) {
    overlay.classList.remove('active');
    document.getElementById('generateBtn').disabled = false;
    showToast(`Error: ${err.message}`, 'error');
    console.error(err);
  }
});
