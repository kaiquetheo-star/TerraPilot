const EVENT_CLASSES = {
  car_submitted: 'car',
  notification_sent: 'notification',
  producer_response: 'response',
  rectification: 'rectification',
  approved: 'approved',
};

function buildCaseDataFromMock(caseId) {
  const mockCase = MOCK_CASES.find((c) => c.case_id === String(caseId));
  if (!mockCase) return { ...MOCK_UNIFIED_CASE };

  return {
    ...MOCK_UNIFIED_CASE,
    case_id: mockCase.case_id,
    producer_id: mockCase.producer_id,
    producer_name: mockCase.producer_name,
    municipality: mockCase.municipality,
    property_size_ha: mockCase.property_size_ha,
    biome: mockCase.biome,
    pending_issues: [{ issue_code: mockCase.issue_code }],
  };
}

function closeDetails() {
  const detailsSection = document.getElementById('case-details');
  const listSection = document.getElementById('case-list');

  if (detailsSection) detailsSection.hidden = true;
  if (listSection) listSection.hidden = false;
}

function showCaseDetails(caseId) {
  const detailsSection = document.getElementById('case-details');
  const listSection = document.getElementById('case-list');

  if (detailsSection) detailsSection.hidden = false;
  if (listSection) listSection.hidden = true;

  loadUnifiedView(buildCaseDataFromMock(caseId));
}

function renderCaseList(cases, filterQuery = '') {
  const tbody = document.getElementById('case-list-body');
  const query = filterQuery.trim().toLowerCase();

  const filtered = cases.filter((c) => {
    if (!query) return true;
    return (
      c.producer_name.toLowerCase().includes(query)
      || c.case_id.includes(query)
      || c.municipality.toLowerCase().includes(query)
      || c.producer_id.includes(query.replace(/\D/g, ''))
    );
  });

  if (!filtered.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Nenhum caso encontrado.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map((c) => `
    <tr data-case-id="${c.case_id}">
      <td><strong>${c.producer_name}</strong></td>
      <td>${c.municipality}</td>
      <td>${translateIssue(c.issue_code)}</td>
      <td class="mono">${c.days_since_last_contact}</td>
      <td>
        <button type="button" class="btn btn--primary btn--sm btn-view-details" data-case-id="${c.case_id}">
          Ver detalhes
        </button>
      </td>
    </tr>
  `).join('');

  tbody.querySelectorAll('.btn-view-details').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      showCaseDetails(e.currentTarget.dataset.caseId);
    });
  });
}

async function initUnified() {
  const form = document.getElementById('unified-search-form');
  const closeBtn = document.getElementById('btn-close-details');

  closeBtn?.addEventListener('click', closeDetails);

  form?.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = document.getElementById('search-query').value.trim();
    renderCaseList(MOCK_CASES, query);

    const match = MOCK_CASES.find((c) => {
      if (!query) return false;
      if (/^\d+$/.test(query)) return c.case_id === query;
      if (/^\d{11}$/.test(query.replace(/\D/g, ''))) {
        return c.producer_id === query.replace(/\D/g, '');
      }
      return c.producer_name.toLowerCase().includes(query.toLowerCase());
    });

    if (match) showCaseDetails(match.case_id);
  });

  renderCaseList(MOCK_CASES);

  const params = new URLSearchParams(window.location.search);
  const caseId = params.get('case_id');
  if (caseId) showCaseDetails(caseId);
}

function getSearchParams() {
  const query = document.getElementById('search-query').value.trim();
  const mock = { ...MOCK_UNIFIED_CASE };

  if (!query) return mock;

  if (/^\d+$/.test(query)) {
    return buildCaseDataFromMock(query);
  }
  if (/^\d{11}$/.test(query.replace(/\D/g, ''))) {
    return { ...mock, producer_id: query.replace(/\D/g, '') };
  }
  return { ...mock, producer_name: query };
}

async function loadUnifiedView(caseData) {
  const timelineEl = document.getElementById('timeline');
  const sidebarEl = document.getElementById('case-sidebar');
  const loading = document.getElementById('unified-loading');

  loading.hidden = false;
  timelineEl.innerHTML = '';
  sidebarEl.innerHTML = '';

  try {
    const view = await api.getUnifiedView(caseData);
    loading.hidden = true;
    renderTimeline(timelineEl, view.timeline);
    renderSidebar(sidebarEl, view);
  } catch (err) {
    showError(`Erro ao carregar visão unificada: ${err.message}`);
    loading.innerHTML = '<div class="alert alert--critical">Não foi possível construir a timeline.</div>';
  }
}

function renderTimeline(container, events) {
  if (!events?.length) {
    container.innerHTML = '<p class="empty-state">Nenhum evento na timeline.</p>';
    return;
  }

  const sorted = [...events].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
  );

  container.innerHTML = `<div class="timeline">${sorted.map((ev) => {
    const cls = EVENT_CLASSES[ev.event_type] || 'car';
    const channel = ev.details?.channel ? ` · ${ev.details.channel}` : '';
    return `
      <div class="timeline__item timeline__item--${cls}">
        <div class="timeline__dot" aria-hidden="true">${timelineIcon(ev.event_type)}</div>
        <div class="timeline__date">${formatDateTime(ev.timestamp)}</div>
        <div class="timeline__desc">${ev.description}${channel}</div>
      </div>
    `;
  }).join('')}</div>`;
}

function renderSidebar(container, view) {
  container.innerHTML = `
    <div class="panel" style="margin-bottom:16px;">
      <h3>Produtor</h3>
      <dl style="font-size:13px;display:grid;grid-template-columns:100px 1fr;gap:6px;">
        <dt>Nome</dt><dd>${view.producer_name}</dd>
        <dt>ID</dt><dd class="mono">${view.producer_id}</dd>
        <dt>Município</dt><dd>${view.municipality}</dd>
      </dl>
    </div>

    <div class="panel" style="margin-bottom:16px;">
      <h3>Propriedade</h3>
      <dl style="font-size:13px;display:grid;grid-template-columns:100px 1fr;gap:6px;">
        <dt>Área</dt><dd>${view.property_size_ha} ha</dd>
        <dt>Bioma</dt><dd>${view.biome}</dd>
        <dt>Status</dt><dd>${view.current_status}</dd>
        <dt>Dias desde envio</dt><dd>${view.total_days_since_submission}</dd>
      </dl>
    </div>

    <div class="panel" style="margin-bottom:16px;">
      <h3>Pendências</h3>
      ${view.pending_issues?.length
    ? `<ul>${view.pending_issues.map((i) => `<li>${translateIssue(i.issue_code)}</li>`).join('')}</ul>`
    : '<p class="page-header__meta">Nenhuma pendência.</p>'}
    </div>

    <div class="panel" style="margin-bottom:16px;">
      <h3>Comunicações</h3>
      ${view.communications?.length
    ? `<ul style="font-size:12px;padding-left:16px;">${view.communications.map((c) => `
          <li style="margin-bottom:8px;">
            <span class="mono">${formatDateTime(c.timestamp)}</span><br>
            ${c.direction === 'outbound' ? 'Enviado' : 'Recebido'} · ${c.channel}: ${c.content_summary}
          </li>
        `).join('')}</ul>`
    : '<p class="page-header__meta">Sem comunicações.</p>'}
    </div>

    <div class="alert alert--info">
      <strong>Próxima ação sugerida</strong><br>
      ${view.suggested_next_action}
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', initUnified);
