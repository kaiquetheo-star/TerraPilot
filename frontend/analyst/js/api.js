const API_BASE = 'http://localhost:8001';
const isGitHubPages = window.location.hostname.includes('github.io');
let demoModeActive = isGitHubPages;

function activateDemoMode(reason) {
  if (demoModeActive) return;
  demoModeActive = true;
  console.warn('TerraPilot Analista: modo demonstração —', reason);
  if (typeof renderSidebar === 'function') renderSidebar();
  if (typeof showToast === 'function') {
    showToast('Modo demonstração — API offline; exibindo dados simulados.', 'info', 5000);
  }
}

function mockAnalystRequest(path, options = {}) {
  const body = options.body ? JSON.parse(options.body) : null;

  if (path === '/api/analyst/prioritize') {
    const cases = Array.isArray(body) ? body : [];
    const prioritized = cases.map((c, i) => ({
      case: c,
      priority_score: Math.max(10, 95 - i * 8),
      priority_level: i < 2 ? 'critical' : i < 5 ? 'high' : 'medium',
      reasons: ['Erro de alto impacto', 'Produtor engajado'],
      recommended_action: 'Enviar notificação traduzida via WhatsApp',
    }));
    return {
      cases: prioritized,
      summary: {
        total_cases: cases.length,
        by_priority_level: {
          critical: prioritized.filter((p) => p.priority_level === 'critical').length,
          high: prioritized.filter((p) => p.priority_level === 'high').length,
          medium: prioritized.filter((p) => p.priority_level === 'medium').length,
        },
        oldest_case_days: Math.max(...cases.map((c) => c.days_since_notification || 0), 0),
      },
    };
  }

  if (path === '/api/analyst/detect-patterns') {
    const records = Array.isArray(body) ? body : [];
    return {
      total_records_analyzed: records.length,
      patterns: [
        { issue_code: 'APP_RIVER_WIDTH', count: Math.ceil(records.length * 0.4), label: 'APP de rio' },
        { issue_code: 'RL_PERCENTAGE', count: Math.ceil(records.length * 0.3), label: 'Reserva Legal (%)' },
      ],
      regional_hotspots: [{ municipality: 'Itaberaba-BA', count: 3 }],
      biome_breakdown: [{ biome: 'Caatinga', count: records.length }],
    };
  }

  if (path === '/api/analyst/templates') {
    return { templates: ['notification_received', 'reminder', 'approval'] };
  }

  if (path === '/api/analyst/render-template') {
    const ctx = body?.context || {};
    return {
      channel: body?.channel || 'whatsapp',
      rendered: `Olá ${ctx.name || 'produtor'}! ${ctx.summary || 'Sua notificação foi traduzida.'}`,
    };
  }

  if (path === '/api/analyst/impact-report') {
    const actions = body?.actions || [];
    const fixed = actions.filter((a) => a.fixed);
    const credit = fixed.reduce((s, a) => s + (a.credit_rural_value_brl || 0), 0);
    return {
      analyst_id: body?.analyst_id || 'luana_01',
      period_days: 30,
      metrics: {
        producers_helped: new Set(fixed.map((a) => a.producer_id)).size,
        cases_resolved: fixed.length,
        avg_days_to_fix: 5.2,
        first_try_success_rate: 0.68,
        credit_rural_unlocked_brl: credit,
        co2_sequestered_tons: 12.4,
      },
      success_stories: [
        { producer_name: 'Seu Raimundo', municipality: 'Itaberaba-BA', outcome: 'CAR aprovado em 3 dias' },
      ],
      narrative: 'Nos últimos 30 dias, a Luana ajudou produtores a destravar crédito rural e regularizar o CAR.',
    };
  }

  if (path === '/api/analyst/decision-support') {
    return {
      case_id: body?.case_id || 'demo',
      complexity: 'high',
      options: [
        { id: 'regularize', label: 'Regularizar via retificação', legal_basis: 'Art. 12, Lei 12.651/2012' },
        { id: 'pra', label: 'Aderir ao PRA', legal_basis: 'Art. 59, Lei 12.651/2012' },
      ],
      recommendation: 'Apresentar opções ao produtor — decisão final da analista.',
    };
  }

  if (path === '/api/analyst/unified-view') {
    const base = typeof MOCK_UNIFIED_CASE !== 'undefined' ? MOCK_UNIFIED_CASE : {};
    return {
      ...base,
      ...body,
      timeline: [
        { event_type: 'car_submitted', timestamp: '2026-01-15T10:00:00', summary: 'CAR submetido' },
        { event_type: 'notification_sent', timestamp: '2026-02-01T14:00:00', summary: 'Notificação APP enviada' },
        { event_type: 'producer_response', timestamp: '2026-02-03T16:20:00', summary: 'Produtor respondeu no WhatsApp' },
        { event_type: 'approved', timestamp: '2026-03-10T15:30:00', summary: 'CAR aprovado' },
      ],
    };
  }

  return { demo: true, path };
}

async function request(path, options = {}) {
  if (isGitHubPages) {
    return mockAnalystRequest(path, options);
  }
  try {
    const resp = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      const detail = err.detail;
      const msg = typeof detail === 'string' ? detail : `HTTP ${resp.status}`;
      throw new Error(msg);
    }
    return resp.json();
  } catch (err) {
    activateDemoMode(err.message || 'API indisponível');
    return mockAnalystRequest(path, options);
  }
}

const api = {
  async prioritize(cases) {
    return request('/api/analyst/prioritize', {
      method: 'POST',
      body: JSON.stringify(cases),
    });
  },

  async detectPatterns(records) {
    return request('/api/analyst/detect-patterns', {
      method: 'POST',
      body: JSON.stringify(records),
    });
  },

  async getTemplates() {
    return request('/api/analyst/templates');
  },

  async renderTemplate(issueCode, context, channel = 'whatsapp') {
    return request('/api/analyst/render-template', {
      method: 'POST',
      body: JSON.stringify({ issue_code: issueCode, context, channel }),
    });
  },

  async getImpactReport(actions, benchmark = {}) {
    return request('/api/analyst/impact-report', {
      method: 'POST',
      body: JSON.stringify({
        analyst_id: 'luana_01',
        actions,
        benchmark,
      }),
    });
  },

  async getDecisionSupport(caseData) {
    return request('/api/analyst/decision-support', {
      method: 'POST',
      body: JSON.stringify(caseData),
    });
  },

  async getUnifiedView(caseData) {
    return request('/api/analyst/unified-view', {
      method: 'POST',
      body: JSON.stringify(caseData),
    });
  },
};

const ISSUE_LABELS = {
  APP_RIVER_WIDTH: 'APP de rio',
  APP_SPRING_RADIUS: 'APP de nascente',
  APP_LAKE_MARGIN: 'APP de lago',
  APP_VEREDA: 'APP de vereda',
  APP_MANGROVE: 'APP de manguezal',
  APP_RESTINGA: 'APP de restinga',
  APP_HILLTOP: 'APP de topo de morro',
  APP_SLOPE_45: 'APP de encosta >45°',
  RL_PERCENTAGE: 'Reserva Legal (%)',
  RL_LOCATION: 'Localização da RL',
  RL_OVERLAP_UC: 'RL sobrepõe UC',
  RL_OVERLAP_TI: 'RL sobrepõe TI',
  CONSOLIDATED_APP: 'APP consolidada',
  CONSOLIDATED_RL: 'RL consolidada',
  DOC_MISSING: 'Documentação faltante',
  DOC_INCONSISTENT: 'Documentação inconsistente',
  PRA_PENDING: 'PRA pendente',
};

function translateIssue(code) {
  return ISSUE_LABELS[code] || code;
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatDateTime(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
}

function showToast(message, type = 'info', duration = 4000) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.className = `toast toast--${type}`;
  toast.hidden = false;
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => { toast.hidden = true; }, duration);
}

function showError(message) {
  showToast(message, 'error', 5000);
}

function priorityBadge(level) {
  const labels = { critical: 'Crítico', high: 'Alto', medium: 'Médio', low: 'Baixo' };
  return `<span class="priority-badge priority-badge--${level}">${labels[level] || level}</span>`;
}

function riskBadge(level) {
  const labels = { low: 'Baixo', medium: 'Médio', high: 'Alto' };
  return `<span class="risk-badge risk-badge--${level}">${labels[level] || level}</span>`;
}

const Icons = {
  menu: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
  insight: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg>',
  timelineCar: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>',
  timelineNotify: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
  timelineResponse: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
  timelineRect: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
  timelineApproved: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>',
  moon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
  sun: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>',
};

function timelineIcon(eventType) {
  const map = {
    car_submitted: Icons.timelineCar,
    notification_sent: Icons.timelineNotify,
    producer_response: Icons.timelineResponse,
    rectification: Icons.timelineRect,
    approved: Icons.timelineApproved,
  };
  return map[eventType] || Icons.timelineCar;
}
