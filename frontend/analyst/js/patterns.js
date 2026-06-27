async function initPatterns() {
  const loading = document.getElementById('patterns-loading');
  const topErrorsEl = document.getElementById('top-errors-chart');
  const biomeEl = document.getElementById('biome-chart');
  const heatmapEl = document.getElementById('heatmap');
  const insightsEl = document.getElementById('insights-list');

  try {
    const records = expandErrorRecords(MOCK_ERROR_RECORDS, 4);
    const data = await api.detectPatterns(records);
    loading.hidden = true;

    renderTopErrors(topErrorsEl, data.insights);
    renderBiomeChart(biomeEl, records);
    renderHeatmap(heatmapEl, records);
    renderInsights(insightsEl, data.insights);
  } catch (err) {
    showError(`Erro ao detectar padrões: ${err.message}`);
    loading.innerHTML = `<div class="alert alert--critical">Não foi possível carregar os padrões.</div>`;
  }
}

function renderTopErrors(container, insights) {
  const topInsight = insights?.find((i) => i.pattern_type === 'top_error');
  const topErrors = topInsight?.evidence?.top_errors || [];

  if (!topErrors.length) {
    container.innerHTML = '<p class="empty-state">Dados insuficientes.</p>';
    return;
  }

  const max = Math.max(...topErrors.map((e) => e.count));
  container.innerHTML = topErrors.map((e) => `
    <div class="bar-chart__row">
      <span class="bar-chart__label">${translateIssue(e.issue_code)}</span>
      <div class="bar-chart__track">
        <div class="bar-chart__fill" style="width:${(e.count / max) * 100}%"></div>
      </div>
      <span class="bar-chart__value">${e.count}</span>
    </div>
  `).join('');
}

function renderBiomeChart(container, records) {
  const byBiome = {};
  records.forEach((r) => {
    byBiome[r.biome] = (byBiome[r.biome] || 0) + 1;
  });

  const entries = Object.entries(byBiome);
  const total = records.length;
  const colors = ['#2D5F3F', '#3D7F5F', '#8BB174', '#D4A574', '#C44536'];
  let offset = 0;
  const radius = 60;
  const cx = 80;
  const cy = 80;
  const circumference = 2 * Math.PI * radius;

  const segments = entries.map(([biome, count], i) => {
    const pct = count / total;
    const dash = pct * circumference;
    const seg = `<circle cx="${cx}" cy="${cy}" r="${radius}" fill="none" stroke="${colors[i % colors.length]}" stroke-width="24" stroke-dasharray="${dash} ${circumference - dash}" stroke-dashoffset="${-offset}" transform="rotate(-90 ${cx} ${cy})"/>`;
    offset += dash;
    return seg;
  }).join('');

  const legend = entries.map(([biome, count], i) => `
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:12px;">
      <span style="width:12px;height:12px;border-radius:2px;background:${colors[i % colors.length]}"></span>
      ${biome}: ${Math.round((count / total) * 100)}%
    </div>
  `).join('');

  container.innerHTML = `
    <div style="display:flex;align-items:center;gap:24px;">
      <svg width="160" height="160" role="img" aria-label="Distribuição de erros por bioma">${segments}</svg>
      <div>${legend}</div>
    </div>
  `;
}

function renderHeatmap(container, records) {
  const byMuni = {};
  records.forEach((r) => {
    byMuni[r.municipality] = (byMuni[r.municipality] || 0) + 1;
  });

  const sorted = Object.entries(byMuni).sort((a, b) => b[1] - a[1]).slice(0, 12);
  const max = sorted[0]?.[1] || 1;

  container.innerHTML = `<div class="heatmap">${sorted.map(([muni, count]) => {
    const intensity = count / max;
    const r = Math.round(196 + (69 - 196) * intensity);
    const g = Math.round(69 + (127 - 69) * (1 - intensity));
    const b = Math.round(54 + (116 - 54) * (1 - intensity));
    const short = muni.split('-')[0];
    return `<div class="heatmap__cell" style="background:rgb(${r},${g},${b})" title="${muni}: ${count} erros">
      <strong>${count}</strong>${short}
    </div>`;
  }).join('')}</div>`;
}

function renderInsights(container, insights) {
  if (!insights?.length) {
    container.innerHTML = '<p class="empty-state">Nenhum insight detectado.</p>';
    return;
  }

  container.innerHTML = insights.map((ins) => `
    <div class="insight-card">
      <div class="insight-card__title">${Icons.insight} ${ins.description}</div>
      <div class="insight-card__rec"><strong>Recomendação:</strong> ${ins.recommendation}</div>
      <div class="page-header__meta" style="margin-top:8px;">Confiança: ${Math.round((ins.confidence || 0) * 100)}%</div>
    </div>
  `).join('');
}

document.addEventListener('DOMContentLoaded', initPatterns);
