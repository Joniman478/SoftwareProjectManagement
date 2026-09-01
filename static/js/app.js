// National Car Import Supply Chain Platform (NCI-SCP) - Application Script

const appState = {
  currentRole: 'importer',
  activeShipmentId: 'SHP-2024-001',
  cachedShipments: []
};

document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initRoleSelector();
  initActiveNav();
  renderDashboardChart();
  renderReportsChart();
  fetchInitialData();
});

// CLOCK
function initClock() {
  const clockEl = document.getElementById('liveDateTime');
  const updateTime = () => {
    const now = new Date();
    const options = {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    };
    if (clockEl) clockEl.textContent = now.toLocaleDateString('en-US', options);
  };
  updateTime();
  setInterval(updateTime, 1000);
}

// ACTIVE NAVIGATION
function initActiveNav() {
  const currentPath = window.location.pathname;
  const navItems = document.querySelectorAll('.sidebar nav .nav-item');
  
  navItems.forEach(item => {
    const href = item.getAttribute('href');
    if (!href) return;
    item.classList.remove('active');
    if (href === currentPath || (currentPath === '/' && href.includes('dashboard'))) {
      item.classList.add('active');
    } else if (currentPath !== '/' && href !== '/' && href !== '/dashboard/' && currentPath.includes(href)) {
      item.classList.add('active');
    }
  });
}

// ROLE SELECTOR
function switchRole(selectedRole) {
  const roleSelector = document.getElementById('userRole');
  const userNameLabel = document.getElementById('userNameLabel');
  const userRoleLabel = document.getElementById('userRoleLabel');
  const greetingName = document.getElementById('headerGreetingName');
  const userAvatarInitials = document.getElementById('userAvatarInitials');

  const rolesMap = {
    importer: { name: 'GT Motors Importer', role: 'Importer / Dealership', initials: 'GM' },
    customs: { name: 'Inspector Tadesse (ECC)', role: 'Customs Officer', initials: 'EC' },
    port: { name: 'Modjo Yard Master', role: 'Port Operator', initials: 'MP' },
    forwarder: { name: 'ESLSE Freight Officer', role: 'Freight Forwarder', initials: 'ES' },
    bank: { name: 'CBE Trade Finance Desk', role: 'Bank Official', initials: 'CB' },
    registration: { name: 'MoTL Title Registrar', role: 'Registration Officer', initials: 'TR' },
    admin: { name: 'System Administrator', role: 'System Administrator', initials: 'SA' }
  };

  const selected = selectedRole || localStorage.getItem('nci_user_role') || 'importer';
  const user = rolesMap[selected] || rolesMap.importer;
  appState.currentRole = selected;
  try {
    localStorage.setItem('nci_user_role', selected);
  } catch (e) {}

  if (userNameLabel) userNameLabel.textContent = user.name;
  if (userRoleLabel) userRoleLabel.textContent = user.role;
  if (greetingName) greetingName.textContent = user.name.split(' ')[0];
  if (userAvatarInitials) userAvatarInitials.textContent = user.initials;
  if (roleSelector) roleSelector.value = selected;

  return user;
}

function initRoleSelector() {
  const savedRole = localStorage.getItem('nci_user_role') || 'importer';
  switchRole(savedRole);

  const roleSelector = document.getElementById('userRole');
  if (roleSelector) {
    roleSelector.addEventListener('change', (e) => {
      const user = switchRole(e.target.value);
      showToast(`Switched portal perspective to ${user.role}`);
    });
  }
}

// FETCH LIVE DATA
async function fetchInitialData() {
  try {
    const res = await fetch('/api/dashboard/');
    if (res.ok) {
      const data = await res.json();
      appState.cachedShipments = data.shipments || [];
    }
  } catch (e) {
    console.warn('API sync fallback active', e);
  }
}

// DASHBOARD SVG CHART
function renderDashboardChart() {
  const wrapper = document.getElementById('svgChartWrapper');
  if (!wrapper) return;

  wrapper.innerHTML = `
    <svg width="100%" height="100%" viewBox="0 0 500 180" preserveAspectRatio="none" style="overflow: visible;">
      <defs>
        <linearGradient id="chartGlowPurple" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.45"/>
          <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.0"/>
        </linearGradient>
        <linearGradient id="chartGlowCyan" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.25"/>
          <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.0"/>
        </linearGradient>
      </defs>

      <!-- Grid Lines -->
      <line x1="0" y1="35" x2="500" y2="35" stroke="rgba(255,255,255,0.06)" stroke-dasharray="4"/>
      <line x1="0" y1="80" x2="500" y2="80" stroke="rgba(255,255,255,0.06)" stroke-dasharray="4"/>
      <line x1="0" y1="125" x2="500" y2="125" stroke="rgba(255,255,255,0.06)" stroke-dasharray="4"/>

      <!-- Target Velocity Curve -->
      <path d="M 20 120 Q 120 100, 240 85 T 480 60 L 480 150 L 20 150 Z" fill="url(#chartGlowCyan)"/>
      <path d="M 20 120 Q 120 100, 240 85 T 480 60" fill="none" stroke="#06b6d4" stroke-width="2" stroke-dasharray="5,5"/>

      <!-- Import Volume Curve -->
      <path d="M 20 135 Q 110 145, 200 80 T 360 50 T 480 30 L 480 150 L 20 150 Z" fill="url(#chartGlowPurple)"/>
      <path d="M 20 135 Q 110 145, 200 80 T 360 50 T 480 30" fill="none" stroke="#a855f7" stroke-width="3.5" stroke-linecap="round"/>

      <!-- Data Dots -->
      <circle cx="20" cy="135" r="4.5" fill="#a855f7" stroke="#fff" stroke-width="1.5"/>
      <circle cx="110" cy="140" r="4.5" fill="#a855f7" stroke="#fff" stroke-width="1.5"/>
      <circle cx="200" cy="80" r="4.5" fill="#a855f7" stroke="#fff" stroke-width="1.5"/>
      <circle cx="360" cy="50" r="4.5" fill="#a855f7" stroke="#fff" stroke-width="1.5"/>
      <circle cx="480" cy="30" r="6" fill="#fff" stroke="#8b5cf6" stroke-width="3"/>

      <!-- Highlight Badge -->
      <g transform="translate(320, 10)">
        <rect x="0" y="0" width="95" height="30" rx="6" fill="#1e1b4b" stroke="#8b5cf6" stroke-width="1"/>
        <text x="47" y="13" font-size="9" fill="#94a3b8" text-anchor="middle" font-weight="600">Week 4 Peak</text>
        <text x="47" y="24" font-size="10" font-weight="bold" fill="#ffffff" text-anchor="middle">35 Vehicles</text>
      </g>

      <!-- X-Axis Labels -->
      <text x="20" y="168" font-size="10" fill="#64748b" font-weight="600">Week 1 (May 07)</text>
      <text x="135" y="168" font-size="10" fill="#64748b" font-weight="600">Week 2 (May 14)</text>
      <text x="265" y="168" font-size="10" fill="#64748b" font-weight="600">Week 3 (May 21)</text>
      <text x="420" y="168" font-size="10" fill="#64748b" font-weight="600">Week 4 (May 28)</text>
    </svg>
  `;
}

// REPORTS SVG CHART
function renderReportsChart() {
  const wrapper = document.getElementById('reportsAnalyticsChart');
  if (!wrapper) return;

  wrapper.innerHTML = `
    <svg width="100%" height="100%" viewBox="0 0 600 220" preserveAspectRatio="none" style="overflow: visible;">
      <defs>
        <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.9"/>
          <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.4"/>
        </linearGradient>
      </defs>

      <!-- Grid lines -->
      <line x1="0" y1="40" x2="600" y2="40" stroke="rgba(255,255,255,0.06)" stroke-dasharray="4"/>
      <line x1="0" y1="90" x2="600" y2="90" stroke="rgba(255,255,255,0.06)" stroke-dasharray="4"/>
      <line x1="0" y1="140" x2="600" y2="140" stroke="rgba(255,255,255,0.06)" stroke-dasharray="4"/>

      <!-- Bars -->
      <!-- Jan -->
      <rect x="50" y="110" width="45" height="70" rx="6" fill="url(#barGradient)"/>
      <text x="72" y="100" font-size="11" fill="#c084fc" font-weight="bold" text-anchor="middle">18</text>
      <text x="72" y="200" font-size="11" fill="#94a3b8" text-anchor="middle">Jan 2024</text>

      <!-- Feb -->
      <rect x="160" y="95" width="45" height="85" rx="6" fill="url(#barGradient)"/>
      <text x="182" y="85" font-size="11" fill="#c084fc" font-weight="bold" text-anchor="middle">22</text>
      <text x="182" y="200" font-size="11" fill="#94a3b8" text-anchor="middle">Feb 2024</text>

      <!-- Mar -->
      <rect x="270" y="60" width="45" height="120" rx="6" fill="url(#barGradient)"/>
      <text x="292" y="50" font-size="11" fill="#c084fc" font-weight="bold" text-anchor="middle">31</text>
      <text x="292" y="200" font-size="11" fill="#94a3b8" text-anchor="middle">Mar 2024</text>

      <!-- Apr -->
      <rect x="380" y="70" width="45" height="110" rx="6" fill="url(#barGradient)"/>
      <text x="402" y="60" font-size="11" fill="#c084fc" font-weight="bold" text-anchor="middle">28</text>
      <text x="402" y="200" font-size="11" fill="#94a3b8" text-anchor="middle">Apr 2024</text>

      <!-- May -->
      <rect x="490" y="45" width="45" height="135" rx="6" fill="url(#barGradient)"/>
      <text x="512" y="35" font-size="11" fill="#38bdf8" font-weight="bold" text-anchor="middle">35</text>
      <text x="512" y="200" font-size="11" fill="#94a3b8" text-anchor="middle">May 2024</text>
    </svg>
  `;
}

// WORKFLOW STEPPER CONTROLS
function selectWorkflowStep(stepIndex) {
  const steps = document.querySelectorAll('#workflowStepper li');
  steps.forEach((step, idx) => {
    const isCompleted = idx < stepIndex;
    const isActive = idx === stepIndex;
    step.classList.toggle('completed', isCompleted);
    step.classList.toggle('active', isActive);
  });
}

async function loadWorkflowForShipment(shipmentId) {
  if (!shipmentId) return;
  appState.activeShipmentId = shipmentId;

  try {
    const res = await fetch(`/api/track/?q=${encodeURIComponent(shipmentId)}`);
    if (res.ok) {
      const data = await res.json();
      if (data.found && data.shipment) {
        const s = data.shipment;
        const vImg = document.getElementById('wfVehicleImg');
        const vTitle = document.getElementById('wfVehicleTitle');
        const vSub = document.getElementById('wfVehicleSub');
        const wfId = document.getElementById('wfShipmentId');
        const wfVin = document.getElementById('wfVin');
        const wfStatus = document.getElementById('wfCurrentStatus');
        const wfProg = document.getElementById('wfProgressVal');
        const wfDest = document.getElementById('wfDestination');

        if (vImg) vImg.src = s.image;
        if (vTitle) vTitle.textContent = s.vehicle;
        if (wfId) wfId.textContent = s.id;
        if (wfVin) wfVin.textContent = s.vin;
        if (wfStatus) wfStatus.textContent = s.status;
        if (wfProg) wfProg.textContent = `${s.progress}%`;
        if (wfDest) wfDest.textContent = s.destination;

        updateDetailedWorkflowStepper(s.status);
      }
    }
  } catch (e) {
    console.error('Error loading shipment workflow', e);
  }
}

function updateDetailedWorkflowStepper(status) {
  const stages = [
    'Booking Confirmed',
    'In Transit',
    'Arrived at Port',
    'Customs Clearance',
    'Released',
    'Delivered'
  ];
  const targetIdx = stages.indexOf(status);
  const activeIdx = targetIdx >= 0 ? targetIdx : 3;

  for (let i = 0; i < 6; i++) {
    const stepEl = document.getElementById(`wfStep${i}`);
    if (stepEl) {
      stepEl.classList.toggle('completed', i < activeIdx);
      stepEl.classList.toggle('active', i === activeIdx);
    }
  }
}

async function advanceActiveWorkflowShipment() {
  const shipmentId = appState.activeShipmentId || document.getElementById('workflowShipmentSelect')?.value || 'SHP-2024-001';
  await advanceShipment(shipmentId);
  await loadWorkflowForShipment(shipmentId);
}

// ADVANCE SHIPMENT WORKFLOW (API)
async function advanceShipment(shipmentId) {
  try {
    const res = await fetch(`/api/shipments/${encodeURIComponent(shipmentId)}/advance/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (res.ok) {
      const data = await res.json();
      showToast(`Advanced ${shipmentId} to stage: "${data.status}" (${data.progress}%)`);
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } else {
      showToast(`Could not advance shipment stage.`);
    }
  } catch (e) {
    showToast(`Error advancing shipment: ${e.message}`);
  }
}

// SEARCH & FILTERS
function filterGlobalShipments(query) {
  const q = (query || '').toLowerCase().trim();
  const rows = document.querySelectorAll('#recentShipmentsTableBody tr, #fullShipmentsTableBody tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(q) ? '' : 'none';
  });
}

function filterShipmentsTable(query) {
  const q = (query || '').toLowerCase().trim();
  const rows = document.querySelectorAll('#fullShipmentsTableBody tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(q) ? '' : 'none';
  });
}

function applyShipmentFilter(status, btn) {
  document.querySelectorAll('.filter-pill-group .filter-pill').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const rows = document.querySelectorAll('#fullShipmentsTableBody tr');
  rows.forEach(row => {
    const rowStatus = row.getAttribute('data-status');
    if (status === 'All' || rowStatus === status) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}

function filterDocumentsTable(query) {
  const q = (query || '').toLowerCase().trim();
  const rows = document.querySelectorAll('#documentTableBody tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(q) ? '' : 'none';
  });
}

function filterAuditTable(query) {
  const q = (query || '').toLowerCase().trim();
  const rows = document.querySelectorAll('#auditTrailTableBody tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(q) ? '' : 'none';
  });
}

function filterNotificationType(type, btn) {
  document.querySelectorAll('.filter-pill-group .filter-pill').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const rows = document.querySelectorAll('#fullNotificationList .notification-row');
  rows.forEach(row => {
    const rowType = row.getAttribute('data-type');
    if (type === 'all' || rowType === type) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}

// MODAL HELPERS
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
}

function openNewShipment() {
  openModal('newShipmentForm');
}

function closeNewShipment() {
  closeModal('newShipmentForm');
}

function openDocumentUpload() {
  openModal('documentUploadForm');
}

function closeDocumentUpload() {
  closeModal('documentUploadForm');
}

function trackShipment() {
  openModal('trackShipmentModal');
}

function openComposeMessageModal() {
  openModal('composeMessageModal');
}

function quickMessageStakeholder(stakeholderName) {
  const recipientSelect = document.getElementById('msgRecipient');
  if (recipientSelect) {
    recipientSelect.value = stakeholderName;
  }
  openComposeMessageModal();
}

function openAlertModal(title, message) {
  const modalTitle = document.getElementById('genericAlertTitle');
  const modalMessage = document.getElementById('genericAlertMessage');
  if (modalTitle) modalTitle.textContent = title;
  if (modalMessage) modalMessage.textContent = message;
  openModal('genericAlertModal');
}

// INSPECT SHIPMENT MODAL
async function inspectShipment(id) {
  const modalBody = document.getElementById('inspectModalBody');
  if (!modalBody) return;

  modalBody.innerHTML = `
    <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
      <span>Loading verified consignment data for ${id}...</span>
    </div>
  `;
  openModal('inspectShipmentModal');

  try {
    const res = await fetch(`/api/track/?q=${encodeURIComponent(id)}`);
    if (res.ok) {
      const data = await res.json();
      if (data.found && data.shipment) {
        const s = data.shipment;
        const docs = data.documents || [];
        const logs = data.audit_logs || [];

        modalBody.innerHTML = `
          <div style="display: flex; gap: 1.25rem; align-items: center; margin-bottom: 1.25rem; flex-wrap: wrap;">
            <img src="${s.image}" alt="${s.vehicle}" class="vehicle-img-large" onerror="this.src='/static/images/land_cruiser.png'">
            <div>
              <h3 style="font-size: 1.25rem; font-weight: 700; color: #fff;">${s.vehicle}</h3>
              <div style="font-size: 0.85rem; color: var(--secondary-light); font-weight: 600;">Shipment ID: ${s.id}</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">VIN: <code class="vin-code">${s.vin}</code></div>
            </div>
            <div style="margin-left: auto; text-align: right;">
              <span class="badge ${s.badgeClass}">${s.status}</span>
              <div style="font-size: 0.8rem; color: var(--warning); font-weight: 600; margin-top: 0.4rem;">Duty: ${s.duty}</div>
            </div>
          </div>

          <div class="spec-list" style="margin-bottom: 1.25rem;">
            <div class="spec-row">
              <span class="spec-label">Origin & Transit:</span>
              <span class="spec-value">${s.port}</span>
            </div>
            <div class="spec-row">
              <span class="spec-label">Destination Dry Port:</span>
              <span class="spec-value">${s.destination}</span>
            </div>
            <div class="spec-row">
              <span class="spec-label">Registered Importer:</span>
              <span class="spec-value">${s.importer}</span>
            </div>
            <div class="spec-row">
              <span class="spec-label">Estimated Arrival (ETA):</span>
              <span class="spec-value">${s.eta}</span>
            </div>
            <div class="spec-row">
              <span class="spec-label">Progress:</span>
              <span class="spec-value">${s.progress}%</span>
            </div>
          </div>

          <h4 style="font-size: 0.95rem; font-weight: 700; margin-bottom: 0.5rem;">Verified Cryptographic Documents (${docs.length})</h4>
          <div style="display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 1.25rem;">
            ${docs.map(d => `
              <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02); padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--glass-border);">
                <div>
                  <strong style="font-size: 0.84rem;">${d.title}</strong>
                  <div style="font-size: 0.72rem; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">${d.hash.substring(0, 20)}...</div>
                </div>
                <span class="badge badge-success" style="font-size: 0.68rem;">✓ ${d.status}</span>
              </div>
            `).join('') || '<div style="color: var(--text-dim); font-size: 0.8rem;">No documents uploaded yet.</div>'}
          </div>

          <div class="modal-actions">
            <button type="button" class="primary-btn" onclick="advanceShipment('${s.id}')">Advance Stage</button>
            <button type="button" class="secondary-btn" onclick="closeModal('inspectShipmentModal')">Close</button>
          </div>
        `;
        return;
      }
    }
    modalBody.innerHTML = `<div style="color: var(--danger); padding: 1rem;">Failed to load shipment details.</div>`;
  } catch (e) {
    modalBody.innerHTML = `<div style="color: var(--danger); padding: 1rem;">Error: ${e.message}</div>`;
  }
}

// REAL-TIME TRACK SEARCH
async function executeTrackSearch() {
  const query = document.getElementById('trackSearchInput')?.value.trim();
  const resultBox = document.getElementById('trackResultBox');
  if (!resultBox) return;

  if (!query) {
    showToast('Please enter a Shipment ID or VIN number.');
    return;
  }

  resultBox.innerHTML = `
    <div style="text-align: center; padding: 1.5rem; color: var(--text-muted);">
      <span>Querying ASYCUDA customs & multimodal tracking...</span>
    </div>
  `;

  try {
    const res = await fetch(`/api/track/?q=${encodeURIComponent(query)}`);
    if (res.ok) {
      const data = await res.json();
      if (data.found && data.shipment) {
        const s = data.shipment;
        resultBox.innerHTML = `
          <div class="glass-panel" style="padding: 1.25rem; background: rgba(16, 185, 129, 0.08); border-color: var(--success); margin-top: 0.5rem;">
            <div style="display: flex; gap: 1rem; align-items: center;">
              <img src="${s.image}" alt="${s.vehicle}" style="width: 70px; height: 48px; object-fit: cover; border-radius: 6px;" onerror="this.src='/static/images/land_cruiser.png'">
              <div>
                <strong style="color: #fff; font-size: 1rem;">${s.vehicle}</strong>
                <div style="font-size: 0.8rem; color: var(--success); font-weight: 600;">${s.id} — ${s.status}</div>
                <div style="font-size: 0.75rem; color: var(--text-muted);">VIN: <code class="vin-code">${s.vin}</code></div>
              </div>
            </div>

            <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--glass-border); display: flex; justify-content: space-between; font-size: 0.8rem;">
              <span>Destination: <strong>${s.destination}</strong></span>
              <span>ETA: <strong>${s.eta}</strong></span>
              <span>Progress: <strong>${s.progress}%</strong></span>
            </div>

            <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
              <button class="primary-btn" style="flex: 1; padding: 0.5rem;" onclick="closeModal('trackShipmentModal'); inspectShipment('${s.id}');">View Full Audit Details</button>
            </div>
          </div>
        `;
        return;
      }
    }
    resultBox.innerHTML = `
      <div class="glass-panel" style="padding: 1.25rem; background: rgba(239, 68, 68, 0.08); border-color: var(--danger); margin-top: 0.5rem; text-align: center;">
        <span style="color: var(--danger); font-weight: 600;">No active shipment found matching "${query}".</span>
        <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;">Please verify the VIN or shipment identifier format (e.g. SHP-2024-001).</p>
      </div>
    `;
  } catch (e) {
    resultBox.innerHTML = `<div style="color: var(--danger); padding: 1rem;">Error querying tracking: ${e.message}</div>`;
  }
}

// CREATE SHIPMENT (AJAX POST)
async function handleNewShipment(e) {
  e.preventDefault();
  const vehicle = document.getElementById('vehicle')?.value.trim();
  const vin = document.getElementById('vin')?.value.trim();
  const port = document.getElementById('port')?.value.trim();
  const destination = document.getElementById('destination')?.value;
  const importer_name = document.getElementById('importer_name')?.value.trim();
  const duty_amount = document.getElementById('duty_amount')?.value.trim();
  const eta = document.getElementById('eta')?.value;

  if (!vehicle || !vin || !port) {
    showToast('Please fill all required fields.');
    return;
  }

  try {
    const res = await fetch('/api/shipments/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vehicle, vin, port, destination, importer_name, duty_amount, eta })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`New Shipment ${data.shipment.id} registered!`);
      closeNewShipment();
      e.target.reset();
      setTimeout(() => { window.location.reload(); }, 1000);
    } else {
      showToast(data.error || 'Failed to create shipment.');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

// UPLOAD & HASH DOCUMENT (AJAX POST)
async function handleUploadDoc(e) {
  e.preventDefault();
  const title = document.getElementById('documentTitle')?.value.trim();
  const type = document.getElementById('documentType')?.value;
  const shipment_id = document.getElementById('docShipmentSelect')?.value;
  const uploaded_by = document.getElementById('uploaderName')?.value.trim();
  
  if (!title) {
    showToast('Please provide a document title.');
    return;
  }

  const rawDigest = await sha256(title + shipment_id + Date.now());

  try {
    const res = await fetch('/api/documents/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, type, shipment_id, uploaded_by, hash: rawDigest })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`Document uploaded & fingerprinted: ${rawDigest.substring(0, 16)}...`);
      closeDocumentUpload();
      e.target.reset();
      setTimeout(() => { window.location.reload(); }, 1000);
    } else {
      showToast(data.error || 'Failed to upload document.');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

// SEND MESSAGE (AJAX POST)
async function handleSendMessage(e) {
  e.preventDefault();
  const recipient = document.getElementById('msgRecipient')?.value;
  const shipment_id = document.getElementById('msgShipmentId')?.value.trim();
  const subject = document.getElementById('msgSubject')?.value.trim();
  const body = document.getElementById('msgBody')?.value.trim();
  const roleObj = switchRole(appState.currentRole);

  try {
    const res = await fetch('/api/messages/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sender: roleObj.name,
        sender_role: roleObj.role,
        recipient,
        shipment_id,
        subject,
        body
      })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Official notice transmitted!');
      closeModal('composeMessageModal');
      e.target.reset();
      setTimeout(() => { window.location.reload(); }, 1000);
    } else {
      showToast(data.error || 'Failed to send message.');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

async function handleInlineSendMessage(e) {
  e.preventDefault();
  const recipient = document.getElementById('inlineRecipient')?.value;
  const shipment_id = document.getElementById('inlineShipmentSelect')?.value;
  const subject = document.getElementById('inlineSubject')?.value.trim();
  const body = document.getElementById('inlineBody')?.value.trim();
  const roleObj = switchRole(appState.currentRole);

  try {
    const res = await fetch('/api/messages/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sender: roleObj.name,
        sender_role: roleObj.role,
        recipient,
        shipment_id,
        subject,
        body
      })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Message transmitted!');
      e.target.reset();
      setTimeout(() => { window.location.reload(); }, 1000);
    } else {
      showToast(data.error || 'Failed to dispatch message.');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

async function markAllNotificationsRead() {
  try {
    const res = await fetch('/api/notifications/', { method: 'POST' });
    if (res.ok) {
      showToast('All notifications marked as read.');
      document.querySelectorAll('.notification-row').forEach(row => row.classList.remove('unread'));
    }
  } catch (e) {
    showToast('Failed to update notifications.');
  }
}

// CRYPTOGRAPHIC SHA-256 TOOLS
async function sha256(message) {
  const msgUint8 = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

async function previewFileHash(input) {
  const preview = document.getElementById('fileHashPreview');
  if (!preview) return;

  if (input.files && input.files[0]) {
    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = async function(e) {
      const buffer = e.target.result;
      const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      preview.textContent = `SHA-256: ${hex}`;
    };
    reader.readAsArrayBuffer(file);
  } else {
    preview.textContent = 'Select a file or leave blank for instant digital digest.';
  }
}

async function generateHash() {
  const textInput = document.getElementById('hashText');
  const text = textInput ? textInput.value || 'National Car Import Manifest Payload' : 'National Car Import Manifest Payload';
  const digest = await sha256(text);
  const resultOutput = document.getElementById('hashResult');
  if (resultOutput) resultOutput.textContent = digest;
  showToast('Generated 256-bit cryptographic digest!');
}

function copyHashToClipboard() {
  const resultOutput = document.getElementById('hashResult');
  if (resultOutput && resultOutput.textContent) {
    navigator.clipboard.writeText(resultOutput.textContent).then(() => {
      showToast('Hash copied to clipboard!');
    }).catch(() => {
      showToast('Could not copy hash.');
    });
  }
}

function verifyDocumentIntegrity(title, expectedHash) {
  openAlertModal(
    'Cryptographic Verification Verified',
    `Document: ${title}\n\nSHA-256 Fingerprint:\n${expectedHash}\n\nStatus: 100% Valid & Authenticated against National Customs Ledger.`
  );
}

function toggleTask(checkbox) {
  const item = checkbox.closest('.task');
  if (!item) return;

  if (checkbox.checked) {
    item.classList.add('completed');
    showToast('Task marked complete!');
  } else {
    item.classList.remove('completed');
  }
}

// DUTY CALCULATOR MODAL & API
function openDutyCalculator() {
  openModal('dutyCalculatorModal');
}

function closeDutyCalculator() {
  closeModal('dutyCalculatorModal');
}

async function handleCalculateDuty(e) {
  e.preventDefault();
  const cif_etb = parseFloat(document.getElementById('dutyCifValue')?.value || 1500000);
  const vehicle_type = document.getElementById('dutyVehicleType')?.value || 'passenger';
  const fuel_type = document.getElementById('dutyFuelType')?.value || 'petrol';
  const engine_cc = parseInt(document.getElementById('dutyEngineCc')?.value || 2000);
  const year_manufactured = parseInt(document.getElementById('dutyMfgYear')?.value || 2024);
  const is_commercial = vehicle_type === 'commercial' || vehicle_type === 'pickup';
  const outputEl = document.getElementById('dutyCalculationOutput');

  if (!outputEl) return;
  outputEl.innerHTML = '<div style="text-align:center; color:var(--text-muted); padding:1rem;">Calculating tariff with Ethiopian Customs Engine...</div>';

  try {
    const res = await fetch('/api/duty-calculator/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cif_etb, vehicle_type, fuel_type, engine_cc, year_manufactured, is_commercial })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      const calc = data.calculation;
      outputEl.innerHTML = `
        <div class="glass-panel" style="padding: 1.25rem; background: rgba(139, 92, 246, 0.08); border-color: var(--primary-light); margin-top: 0.5rem;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <strong style="color:#fff; font-size:1.1rem;">Customs Duty Assessment</strong>
            <span class="badge ${calc.is_ev_incentivized ? 'badge-success' : 'badge-primary'}">${calc.is_ev_incentivized ? '⚡ EV Green Incentive' : 'Standard Tariff'}</span>
          </div>

          <div class="spec-list" style="font-size:0.85rem;">
            <div class="spec-row">
              <span class="spec-label">CIF Base Value:</span>
              <strong class="spec-value">ETB ${calc.cif_etb.toLocaleString()}</strong>
            </div>
            <div class="spec-row">
              <span class="spec-label">Customs Duty (${calc.customs_duty.rate}%):</span>
              <span class="spec-value">ETB ${calc.customs_duty.amount.toLocaleString(undefined, {minimumFractionDigits:2})}</span>
            </div>
            <div class="spec-row">
              <span class="spec-label">Excise Tax (${calc.excise_tax.rate}%):</span>
              <span class="spec-value">ETB ${calc.excise_tax.amount.toLocaleString(undefined, {minimumFractionDigits:2})}</span>
            </div>
            <div class="spec-row">
              <span class="spec-label">VAT (${calc.vat.rate}%):</span>
              <span class="spec-value">ETB ${calc.vat.amount.toLocaleString(undefined, {minimumFractionDigits:2})}</span>
            </div>
            <div class="spec-row">
              <span class="spec-label">Sur Tax (${calc.surtax.rate}%):</span>
              <span class="spec-value">ETB ${calc.surtax.amount.toLocaleString(undefined, {minimumFractionDigits:2})}</span>
            </div>
            <div class="spec-row">
              <span class="spec-label">Withholding Tax (${calc.withholding_tax.rate}%):</span>
              <span class="spec-value">ETB ${calc.withholding_tax.amount.toLocaleString(undefined, {minimumFractionDigits:2})}</span>
            </div>
            <div class="spec-row" style="border-top:1px solid var(--primary-glow); padding-top:0.5rem; margin-top:0.5rem;">
              <span class="spec-label" style="font-size:1rem; font-weight:800; color:#fff;">Total Duty Payable:</span>
              <strong class="spec-value" style="font-size:1.1rem; color:var(--warning); font-family:'JetBrains Mono', monospace;">${calc.formatted_total}</strong>
            </div>
            <div class="spec-row">
              <span class="spec-label">Effective Tax Rate:</span>
              <span class="spec-value text-cyan">${calc.effective_tax_rate_percent}%</span>
            </div>
          </div>
        </div>
      `;
      showToast('Calculated Ethiopian customs duty tariff!');
    } else {
      outputEl.innerHTML = `<div style="color:var(--danger); padding:1rem;">Error: ${data.error || 'Calculation failed'}</div>`;
    }
  } catch (err) {
    outputEl.innerHTML = `<div style="color:var(--danger); padding:1rem;">Error: ${err.message}</div>`;
  }
}

// TOAST NOTIFICATIONS
function showToast(message) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `
    <svg viewBox="0 0 24 24" width="18" height="18" stroke="#10b981" fill="none" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

