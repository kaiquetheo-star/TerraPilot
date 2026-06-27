/**
 * Router hash-based — carrega views HTML e executa handlers.
 */
const TerraPilotRouter = (() => {
  const routes = {
    '': 'home',
    home: 'home',
    'learn/what-is-app': 'learn/what-is-app',
    'learn/what-is-rl': 'learn/what-is-rl',
    'learn/calculator': 'learn/calculator',
    'declare/prefill': 'declare/prefill',
    'declare/first-time': 'declare/first-time',
    'declare/draw-guide': 'declare/draw-guide',
    'declare/validate-local': 'declare/validate-local',
    'notifications/list': 'notifications/list',
    'notifications/detail': 'notifications/detail',
    'notifications/fix-guide': 'notifications/fix-guide',
    'progress/dashboard': 'progress/dashboard',
    'progress/history': 'progress/history',
    'help/faq': 'help/faq',
    'help/capability': 'help/capability',
    'help/audio-help': 'help/audio-help',
    'help/contact-oema': 'help/contact-oema',
    'network/community': 'network/community',
    'benefits/pra': 'benefits/pra',
    'benefits/collective-impact': 'benefits/collective-impact',
  };

  const handlers = {};
  let currentRoute = '';

  function register(route, fn) {
    handlers[route] = fn;
  }

  function getRoute() {
    const hash = location.hash.replace(/^#\/?/, '').split('?')[0] || 'home';
    return routes[hash] ? hash : 'home';
  }

  async function loadComponent(name) {
    const res = await fetch(`components/${name}.html`);
    if (!res.ok) return '';
    return res.text();
  }

  async function navigate(route) {
    const viewPath = routes[route] || routes.home;
    currentRoute = route;

    const main = document.getElementById('main-content');
    main.innerHTML = '<p class="text-muted" role="status">Carregando...</p>';

    try {
      const res = await fetch(`views/${viewPath}.html`);
      if (!res.ok) throw new Error('View não encontrada');
      main.innerHTML = await res.text();
      document.title = `TerraPilot — ${main.querySelector('[data-page-title]')?.textContent || 'Assistente CAR'}`;
      updateNav(route);
      if (handlers[viewPath]) await handlers[viewPath](main);
      TerraPilotA11y.announce(document.title);
      main.focus();
    } catch (e) {
      main.innerHTML = `<div class="card"><p>Não foi possível carregar esta tela. Tente novamente offline.</p>
        <a href="#/home" class="btn btn--primary">Voltar ao início</a></div>`;
    }
  }

  function updateNav(route) {
    document.querySelectorAll('.bottom-nav a').forEach((a) => {
      const r = a.getAttribute('data-route');
      a.setAttribute('aria-current', r === route || (route.startsWith(r + '/') && r !== 'home') ? 'page' : 'false');
    });
  }

  function start() {
    window.addEventListener('hashchange', () => navigate(getRoute()));
    navigate(getRoute());
  }

  return { register, navigate, getRoute, loadComponent, start };
})();
