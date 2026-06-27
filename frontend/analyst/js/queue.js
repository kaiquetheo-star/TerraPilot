let allCases = [];
let filteredCases = [];

async function initQueue() {
  const tableBody = document.getElementById('queue-table-body');
  const loading = document.getElementById('queue-loading');

  try {
    const mockCases = MOCK_CASES;
    const data = await api.prioritize(mockCases);
    allCases = data.cases;
    filteredCases = [...allCases];
    loading.hidden = true;
    renderTable(tableBody);
    bindFilters();
    bindTableEvents();
  } catch (err) {
    showError(`Erro ao carregar fila: ${err.message}`);
    loading.innerHTML = `<div class="alert alert--critical">Não foi possível carregar a fila. Verifique a API em ${API_BASE}</div>`;
  }
}

function bindFilters() {
  ['filter-priority', 'filter-biome', 'filter-issue', 'filter-days'].forEach((id) => {
    document.getElementById(id)?.addEventListener('change', applyFilters);
  });
}

function applyFilters() {
  const priority = document.getElementById('filter-priority').value;
  const biome = document.getElementById('filter-biome').value;
  const issue = document.getElementById('filter-issue').value;
  const days = document.getElementById('filter-days').value;

  filteredCases = allCases.filter((pc) => {
    if (priority && pc.priority_level !== priority) return false;
    if (biome && pc.case.biome !== biome) return false;
    if (issue && pc.case.issue_code !== issue) return false;
    if (days) {
      const min = parseInt(days, 10);
      if (pc.case.days_since_last_contact < min) return false;
    }
    return true;
  });

  renderTable(document.getElementById('queue-table-body'));
}

function renderTable(tbody) {
  if (!filteredCases.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state">Nenhum caso encontrado com os filtros selecionados.</td></tr>`;
    return;
  }

  tbody.innerHTML = filteredCases.map((pc) => {
    const c = pc.case;
    return `
      <tr tabindex="0" data-case-id="${c.case_id}" aria-label="Caso ${c.producer_name}">
        <td>${priorityBadge(pc.priority_level)}</td>
        <td><strong>${c.producer_name}</strong><br><span class="page-header__meta">${c.municipality}</span></td>
        <td>${translateIssue(c.issue_code)}</td>
        <td class="mono">${c.days_since_last_contact}</td>
        <td class="mono">${pc.priority_score.toFixed(1)}</td>
        <td>
          <button type="button" class="btn btn--ghost btn--sm btn-detail" data-case-id="${c.case_id}">Detalhes</button>
          <button type="button" class="btn btn--primary btn--sm btn-notify" data-case-id="${c.case_id}">Notificar</button>
          <a href="tel:+5571999999999" class="btn btn--ghost btn--sm" aria-label="Ligar para ${c.producer_name}">Ligar</a>
        </td>
      </tr>
    `;
  }).join('');
}

function bindTableEvents() {
  const tbody = document.getElementById('queue-table-body');
  tbody.addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const caseId = btn.dataset.caseId;
    const pc = allCases.find((c) => c.case.case_id === caseId);
    if (!pc) return;

    if (btn.classList.contains('btn-detail')) {
      openCaseModal(pc);
    } else if (btn.classList.contains('btn-notify')) {
      openNotifyModal(pc);
    }
  });

  tbody.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.target.tagName === 'TR') {
      const pc = allCases.find((c) => c.case.case_id === e.target.dataset.caseId);
      if (pc) openCaseModal(pc);
    }
  });

  tbody.addEventListener('click', (e) => {
    const row = e.target.closest('tr[data-case-id]');
    if (row && !e.target.closest('button') && !e.target.closest('a')) {
      const pc = allCases.find((c) => c.case.case_id === row.dataset.caseId);
      if (pc) openCaseModal(pc);
    }
  });
}

function openCaseModal(pc) {
  const c = pc.case;
  const modal = document.getElementById('case-modal');
  document.getElementById('case-modal-title').textContent = c.producer_name;
  document.getElementById('case-modal-body').innerHTML = `
    <p>${priorityBadge(pc.priority_level)} <span class="mono">Score: ${pc.priority_score.toFixed(1)}</span></p>
    <dl style="display:grid;grid-template-columns:140px 1fr;gap:8px;font-size:13px;margin-top:16px;">
      <dt>Município</dt><dd>${c.municipality}</dd>
      <dt>Bioma</dt><dd>${c.biome}</dd>
      <dt>Área</dt><dd>${c.property_size_ha} ha (${c.modulo_fiscal} módulos)</dd>
      <dt>Erro</dt><dd>${translateIssue(c.issue_code)}</dd>
      <dt>Dias sem resposta</dt><dd>${c.days_since_last_contact}</dd>
      <dt>Canal</dt><dd>${c.channel_reached}</dd>
      <dt>Contexto legal</dt><dd>${pc.legal_context}</dd>
    </dl>
    <h3 style="margin-top:16px;">Motivos da prioridade</h3>
    <ul>${pc.reasons.map((r) => `<li>${r}</li>`).join('')}</ul>
    <p><strong>Ação recomendada:</strong> ${pc.recommended_action}</p>
  `;
  modal.hidden = false;
}

async function openNotifyModal(pc) {
  const c = pc.case;
  const modal = document.getElementById('notify-modal');
  const body = document.getElementById('notify-modal-body');
  modal.hidden = false;
  body.innerHTML = '<div class="loading"><div class="loading__spinner"></div> Renderizando template...</div>';

  try {
    const result = await api.renderTemplate(c.issue_code, {
      producer_name: c.producer_name,
      river_name: 'Rio local',
      required_m: 50,
      municipality: c.municipality,
    });
    body.innerHTML = `
      <p class="page-header__meta">Canal: WhatsApp · ${translateIssue(c.issue_code)}</p>
      <pre id="notify-text" style="white-space:pre-wrap;background:var(--beige);padding:16px;border-radius:8px;font-size:13px;margin-top:12px;">${result.rendered}</pre>
    `;
    document.getElementById('btn-copy-whatsapp').onclick = () => {
      const text = document.getElementById('notify-text').textContent;
      navigator.clipboard.writeText(text).then(() => showToast('Mensagem copiada! Cole no WhatsApp.'));
    };
  } catch (err) {
    showError(`Erro ao renderizar template: ${err.message}`);
    body.innerHTML = `<div class="alert alert--critical">Não foi possível renderizar o template.</div>`;
  }
}

function closeModals() {
  document.querySelectorAll('.modal-overlay').forEach((m) => { m.hidden = true; });
}

document.addEventListener('DOMContentLoaded', () => {
  initQueue();
  document.querySelectorAll('[data-close-modal]').forEach((btn) => {
    btn.addEventListener('click', closeModals);
  });
  document.querySelectorAll('.modal-overlay').forEach((overlay) => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModals();
    });
  });
});
