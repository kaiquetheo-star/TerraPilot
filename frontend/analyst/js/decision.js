async function initDecision() {
  const form = document.getElementById('decision-form');
  const resultsPanel = document.getElementById('decision-results');
  const ucTypeGroup = document.getElementById('uc-type-group');
  const finesGroup = document.getElementById('fines-count-group');

  document.getElementById('overlaps-uc').addEventListener('change', (e) => {
    ucTypeGroup.hidden = !e.target.checked;
  });

  document.getElementById('has-fines').addEventListener('change', (e) => {
    finesGroup.hidden = !e.target.checked;
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    resultsPanel.hidden = false;
    resultsPanel.innerHTML = '<div class="loading"><div class="loading__spinner"></div> Analisando caso...</div>';

    const data = {
      case_id: `case_${Date.now()}`,
      producer_name: form.producer_name.value,
      property_size_ha: parseFloat(form.property_size_ha.value),
      municipality: form.municipality.value,
      state: form.state.value,
      biome: form.biome.value,
      issue_code: form.issue_code.value,
      overlaps_uc: form.overlaps_uc.checked,
      uc_type: form.overlaps_uc.checked ? form.uc_type.value : null,
      overlaps_ti: form.overlaps_ti.checked,
      overlaps_quilombo: form.overlaps_quilombo?.checked || false,
      overlaps_border: form.overlaps_border?.checked || false,
      has_pending_fines: form.has_fines.checked,
      fine_count: form.has_fines.checked ? parseInt(form.fine_count.value, 10) || 0 : 0,
      consolidated_before_2008: form.consolidated_before_2008.checked,
      property_size_modulos: parseFloat(form.property_size_modulos.value),
      legal_issues: form.legal_issues.value
        ? form.legal_issues.value.split(',').map((s) => s.trim())
        : [],
    };

    try {
      const result = await api.getDecisionSupport(data);
      renderResults(resultsPanel, result);
    } catch (err) {
      showError(`Erro na análise: ${err.message}`);
      resultsPanel.innerHTML = `<div class="alert alert--critical">Não foi possível analisar o caso.</div>`;
    }
  });
}

function renderResults(container, result) {
  const risks = result.risk_assessment || {};

  container.innerHTML = `
    <h2>Resultado da análise</h2>

    <div class="panel" style="margin-bottom:16px;">
      <h3>Resumo do caso</h3>
      <p>${result.case_summary}</p>
    </div>

    <div class="panel" style="margin-bottom:16px;">
      <h3>Avaliação de risco</h3>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <div>Legal: ${riskBadge(risks.legal_risk || 'medium')}</div>
        <div>Ambiental: ${riskBadge(risks.environmental_risk || 'medium')}</div>
        <div>Social: ${riskBadge(risks.social_risk || 'low')}</div>
      </div>
    </div>

    <h3>Opções legais</h3>
    ${(result.options || []).map((opt, i) => `
      <div class="expandable" id="opt-${i}">
        <button type="button" class="expandable__header" aria-expanded="false" data-expand="opt-${i}">
          ${opt.description}
          <span aria-hidden="true">▼</span>
        </button>
        <div class="expandable__body">
          <p><strong>Base legal:</strong> ${opt.legal_basis}</p>
          <p><strong>Tempo estimado:</strong> ${opt.estimated_time_days} dias</p>
          <p><strong>Prós:</strong></p>
          <ul>${(opt.pros || []).map((p) => `<li>${p}</li>`).join('')}</ul>
          <p><strong>Contras:</strong></p>
          <ul>${(opt.cons || []).map((c) => `<li>${c}</li>`).join('')}</ul>
          <p><strong>Documentos necessários:</strong></p>
          <ul>${(opt.required_documents || []).map((d) => `<li>${d}</li>`).join('')}</ul>
        </div>
      </div>
    `).join('')}

    ${result.precedents?.length ? `
      <div class="panel" style="margin-top:16px;">
        <h3>Precedentes</h3>
        <ul>${result.precedents.map((p) => `<li><strong>${p.case}:</strong> ${p.decision} (${p.date || ''})</li>`).join('')}</ul>
      </div>
    ` : ''}

    ${result.recommended_consultation?.length ? `
      <div class="panel" style="margin-top:16px;">
        <h3>Órgãos a consultar</h3>
        <ul>${result.recommended_consultation.map((org) => `<li>${org}</li>`).join('')}</ul>
      </div>
    ` : ''}
  `;

  container.querySelectorAll('[data-expand]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.expand;
      const el = document.getElementById(id);
      const open = el.classList.toggle('expandable--open');
      btn.setAttribute('aria-expanded', open);
    });
  });
}

document.addEventListener('DOMContentLoaded', initDecision);
