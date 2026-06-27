async function initDashboard() {
  const statsEl = document.getElementById('stats-grid');
  const trendEl = document.getElementById('trend-chart');
  const actionsEl = document.getElementById('next-actions');
  const alertsEl = document.getElementById('alerts-list');

  try {
    const cases = MOCK_CASES;
    const actions = filterActionsByPeriod(MOCK_ACTIONS, 30);

    const [queueData, impactData] = await Promise.all([
      api.prioritize(cases),
      api.getImpactReport(actions, BENCHMARK),
    ]);

    renderStats(statsEl, queueData.summary, impactData);
    renderTrendChart(trendEl, actions);
    renderNextActions(actionsEl, queueData.cases.slice(0, 5));
    renderAlerts(alertsEl, queueData.cases);
  } catch (err) {
    console.error(err);
    showError(`Erro ao carregar dashboard: ${err.message}. Verifique a API em ${API_BASE}`);
    statsEl.innerHTML = `<div class="alert alert--critical">Não foi possível carregar os dados. Verifique se a API está em ${API_BASE}</div>`;
  }
}

function renderStats(container, summary, impact) {
  const metrics = impact.metrics || {};
  const critical = summary.by_priority_level?.critical || 0;
  const pending = summary.total_cases || 0;
  const avgDays = metrics.avg_days_to_fix || summary.oldest_case_days || 0;
  const firstTry = metrics.first_try_success_rate
    ? `${Math.round(metrics.first_try_success_rate * 100)}%`
    : '—';

  container.innerHTML = `
    <div class="stat-card">
      <div class="stat-card__value">${pending}</div>
      <div class="stat-card__label">Casos pendentes</div>
    </div>
    <div class="stat-card">
      <div class="stat-card__value">${critical}</div>
      <div class="stat-card__label">Casos críticos</div>
    </div>
    <div class="stat-card">
      <div class="stat-card__value">${avgDays}</div>
      <div class="stat-card__label">Tempo médio de correção (dias)</div>
    </div>
    <div class="stat-card">
      <div class="stat-card__value">${firstTry}</div>
      <div class="stat-card__label">Correções na 1ª tentativa</div>
    </div>
  `;
}

function renderTrendChart(container, actions) {
  const byDay = {};
  actions.filter((a) => a.fixed).forEach((a) => {
    const day = a.timestamp.slice(0, 10);
    byDay[day] = (byDay[day] || 0) + 1;
  });

  const days = Object.keys(byDay).sort();
  const values = days.map((d) => byDay[d]);
  const max = Math.max(...values, 1);
  const width = 600;
  const height = 200;
  const pad = 30;

  const points = values.map((v, i) => {
    const x = pad + (i / Math.max(values.length - 1, 1)) * (width - pad * 2);
    const y = height - pad - (v / max) * (height - pad * 2);
    return `${x},${y}`;
  }).join(' ');

  const bars = values.map((v, i) => {
    const barW = (width - pad * 2) / values.length - 4;
    const x = pad + i * ((width - pad * 2) / values.length);
    const h = (v / max) * (height - pad * 2);
    return `<rect x="${x}" y="${height - pad - h}" width="${barW}" height="${h}" fill="#2D5F3F" opacity="0.7" rx="2"/>`;
  }).join('');

  container.innerHTML = `
    <svg class="chart-svg trend-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Gráfico de casos resolvidos nos últimos 30 dias">
      ${bars}
      <polyline points="${points}" fill="none" stroke="#D4A574" stroke-width="2"/>
      <text x="${pad}" y="${height - 8}" font-size="10" fill="#888">${days[0] ? formatDate(days[0]) : ''}</text>
      <text x="${width - pad - 60}" y="${height - 8}" font-size="10" fill="#888">${days.length ? formatDate(days[days.length - 1]) : ''}</text>
    </svg>
  `;
}

function renderNextActions(container, topCases) {
  if (!topCases.length) {
    container.innerHTML = '<p class="empty-state">Nenhuma ação pendente.</p>';
    return;
  }

  container.innerHTML = `<ul class="action-list">${topCases.map((pc, i) => `
    <li class="action-list__item">
      <span class="action-list__rank">${i + 1}</span>
      <div class="action-list__content">
        <div class="action-list__title">${pc.case.producer_name} — ${translateIssue(pc.case.issue_code)}</div>
        <div class="action-list__meta">${pc.recommended_action} · ${pc.case.municipality}</div>
      </div>
      ${priorityBadge(pc.priority_level)}
    </li>
  `).join('')}</ul>`;
}

function renderAlerts(container, cases) {
  const abandoned = cases.filter((pc) => pc.case.days_since_last_contact > 30);

  if (!abandoned.length) {
    container.innerHTML = '<p class="empty-state">Nenhum produtor abandonado no momento.</p>';
    return;
  }

  container.innerHTML = abandoned.map((pc) => `
    <div class="alert alert--warning">
      <strong>${pc.case.producer_name}</strong> (${pc.case.municipality}) —
      ${pc.case.days_since_last_contact} dias sem resposta · ${translateIssue(pc.case.issue_code)}
    </div>
  `).join('');
}

document.addEventListener('DOMContentLoaded', initDashboard);
