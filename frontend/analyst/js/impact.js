let currentPeriod = 30;

async function initImpact() {
  bindPeriodSelector();
  await loadReport(currentPeriod);
}

function bindPeriodSelector() {
  document.querySelectorAll('[data-period]').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-period]').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      currentPeriod = parseInt(btn.dataset.period, 10);
      loadReport(currentPeriod);
    });
  });
}

async function loadReport(days) {
  const loading = document.getElementById('impact-loading');
  const metricsEl = document.getElementById('impact-metrics');
  const narrativeEl = document.getElementById('impact-narrative');
  const storiesEl = document.getElementById('success-stories');
  const comparisonEl = document.getElementById('peer-comparison');

  loading.hidden = false;
  metricsEl.innerHTML = '';
  narrativeEl.innerHTML = '';
  storiesEl.innerHTML = '';
  comparisonEl.innerHTML = '';

  try {
    const actions = filterActionsByPeriod(MOCK_ACTIONS, days);
    const report = await api.getImpactReport(actions, BENCHMARK);
    loading.hidden = true;

    renderMetrics(metricsEl, report);
    renderNarrative(narrativeEl, report);
    renderStories(storiesEl, report.success_stories);
    renderComparison(comparisonEl, report.peer_comparison);
  } catch (err) {
    showError(`Erro ao gerar relatório: ${err.message}`);
    loading.innerHTML = `<div class="alert alert--critical">Não foi possível gerar o relatório de impacto.</div>`;
  }
}

function initPrintExport() {
  document.getElementById('btn-export-pdf')?.addEventListener('click', () => {
    window.print();
  });
}

function renderMetrics(container, report) {
  const m = report.metrics || {};
  const env = report.environmental_impact || {};
  const eco = report.economic_impact || {};

  container.innerHTML = `
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-card__value">${m.cases_analyzed || 0}</div>
        <div class="stat-card__label">Casos analisados</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__value">${m.producers_helped || 0}</div>
        <div class="stat-card__label">Produtores ajudados</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__value">${formatCurrency(eco.credit_rural_unlocked_brl)}</div>
        <div class="stat-card__label">Crédito rural destravado</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__value">${env.co2_sequestered_tons_year || '—'}</div>
        <div class="stat-card__label">CO₂ sequestrado (t/ano)</div>
      </div>
    </div>
    <div class="stat-card" style="margin-top:16px;">
      <div class="stat-card__value">${env.equivalent_trees_planted || '—'}</div>
      <div class="stat-card__label">Árvores equivalentes plantadas</div>
    </div>
  `;
}

function renderNarrative(container, report) {
  const env = report.environmental_impact || {};
  const narrative = env.narrative || report.economic_impact?.narrative || 'Carregando narrativa de impacto...';
  container.innerHTML = `<div class="metric-highlight">${narrative}</div>`;
}

function renderStories(container, stories) {
  if (!stories?.length) {
    container.innerHTML = '<p class="empty-state">Nenhuma história de sucesso no período.</p>';
    return;
  }

  container.innerHTML = stories.map((s, i) => `
    <div class="success-card">
      <img class="success-card__avatar" src="../../images/persona-raimundo.png" alt="" aria-hidden="true">
      <div>
        <div class="success-card__name">${s.producer_name}</div>
        <div class="success-card__detail">
          ${translateIssue(s.issue_code)} · Corrigido em ${s.days_to_fix} dias via ${s.channel}
        </div>
        <div class="success-card__detail" style="margin-top:4px;">${s.narrative}</div>
      </div>
    </div>
  `).join('');
}

function renderComparison(container, comparison) {
  if (!comparison || !Object.keys(comparison).length) {
    container.innerHTML = '<p class="empty-state">Comparação indisponível.</p>';
    return;
  }

  const daysComp = comparison.avg_days_to_fix;
  const rateComp = comparison.first_try_success_rate;

  let html = '';

  if (daysComp) {
    const pct = daysComp.benchmark
      ? Math.round(((daysComp.benchmark - daysComp.your_value) / daysComp.benchmark) * 100)
      : 0;
    html += `
      <div class="panel" style="margin-bottom:12px;">
        <p>Seu tempo médio (<strong>${daysComp.your_value} dias</strong>) é
        <strong>${Math.abs(pct)}% ${pct > 0 ? 'menor' : 'maior'}</strong>
        que a média estadual (${daysComp.benchmark} dias).</p>
        <div class="comparison-bar">
          <span class="mono" style="font-size:11px;">Você</span>
          <div class="comparison-bar__track"><div class="comparison-bar__fill" style="width:${Math.min(100, (daysComp.benchmark - daysComp.your_value) / daysComp.benchmark * 100 + 50)}%"></div></div>
        </div>
      </div>
    `;
  }

  if (rateComp) {
    html += `
      <div class="panel">
        <p>Taxa de sucesso na 1ª tentativa: <strong>${Math.round(rateComp.your_value * 100)}%</strong>
        vs média <strong>${Math.round(rateComp.benchmark * 100)}%</strong></p>
      </div>
    `;
  }

  container.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', () => {
  initImpact();
  initPrintExport();
});
