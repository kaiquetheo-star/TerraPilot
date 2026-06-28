const NAV_ITEMS = [
  { href: 'index.html', label: 'Dashboard', icon: 'dashboard' },
  { href: 'queue.html', label: 'Fila de prioridade', icon: 'queue' },
  { href: 'patterns.html', label: 'Padrões de erro', icon: 'patterns' },
  { href: 'impact.html', label: 'Relatório de impacto', icon: 'impact' },
  { href: 'decision.html', label: 'Suporte de decisão', icon: 'decision' },
  { href: 'unified.html', label: 'Visão unificada', icon: 'unified' },
];

const NAV_ICONS = {
  dashboard: '<svg class="sidebar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
  queue: '<svg class="sidebar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>',
  patterns: '<svg class="sidebar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 3v18h18"/><path d="M7 16l4-8 4 4 5-10"/></svg>',
  impact: '<svg class="sidebar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/></svg>',
  decision: '<svg class="sidebar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3v18"/><path d="M5 10h14"/><path d="M5 14h14"/></svg>',
  unified: '<svg class="sidebar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>',
};

function getCurrentPage() {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  return path === '' ? 'index.html' : path;
}

function renderSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  const current = getCurrentPage();
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const links = NAV_ITEMS.map((item) => {
    const active = item.href === current ? ' sidebar__link--active' : '';
    const aria = item.href === current ? ' aria-current="page"' : '';
    return `<a href="${item.href}" class="sidebar__link${active}"${aria}>${NAV_ICONS[item.icon]}${item.label}</a>`;
  }).join('');

  sidebar.innerHTML = `
    <div class="sidebar__brand">
      <img src="../../images/terrapilot-logo.png" alt="" class="sidebar__brand-logo" aria-hidden="true">
      <h1>TerraPilot</h1>
      <p>Módulo Analista — Luana</p>
    </div>
    <nav class="sidebar__nav" aria-label="Navegação principal">${links}</nav>
    <button type="button" class="theme-toggle" id="theme-toggle" aria-label="Alternar tema claro/escuro">
      ${isDark ? Icons.sun : Icons.moon}
      <span>${isDark ? 'Tema claro' : 'Tema escuro'}</span>
    </button>
    <div class="sidebar__footer">${demoModeActive ? 'Modo demonstração (API offline)' : `API: ${API_BASE}`}</div>
  `;

  document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);
}

function toggleTheme() {
  const root = document.documentElement;
  const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  if (next === 'dark') {
    root.setAttribute('data-theme', 'dark');
  } else {
    root.removeAttribute('data-theme');
  }
  renderSidebar();
}

function initMobileNav() {
  const toggle = document.getElementById('mobile-nav-toggle');
  const sidebar = document.getElementById('sidebar');
  if (!toggle || !sidebar) return;

  toggle.innerHTML = Icons.menu;

  toggle.addEventListener('click', () => {
    sidebar.classList.toggle('sidebar--open');
  });

  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 900 && sidebar.classList.contains('sidebar--open')) {
      if (!sidebar.contains(e.target) && e.target !== toggle && !toggle.contains(e.target)) {
        sidebar.classList.remove('sidebar--open');
      }
    }
  });
}

function updateDateTime() {
  const el = document.getElementById('header-datetime');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleString('pt-BR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

document.addEventListener('DOMContentLoaded', () => {
  renderSidebar();
  initMobileNav();
  updateDateTime();
  setInterval(updateDateTime, 60000);
});
