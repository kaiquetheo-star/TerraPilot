const API_BASE = 'http://localhost:8001';

async function request(path, options = {}) {
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
