const CACHE_NAME = 'terrapilot-v8-regularizacao';
const STATIC_ASSETS = [
  './',
  './index.html',
  './app.js',
  './manifest.json',
  './css/main.css',
  './css/accessibility.css',
  './js/router.js',
  './js/api.js',
  './js/offline-manager.js',
  './js/mock-prefill.js',
  './js/accessibility.js',
  './data/rules.json',
  './data/dictionary.json',
  './data/capability.json',
  './data/faq-contextual.json',
  './data/guides.json',
  './data/prefill/municipalities_ibge.json',
  './data/prefill/samples/hydrography.geojson',
  './data/prefill/samples/land_cover.geojson',
  './data/prefill/samples/car_reference.geojson',
  './views/home.html',
  './views/learn/what-is-app.html',
  './views/learn/what-is-rl.html',
  './views/learn/calculator.html',
  './views/declare/prefill.html',
  './views/declare/draw-guide.html',
  './views/declare/validate-local.html',
  './views/notifications/list.html',
  './views/notifications/detail.html',
  './views/notifications/fix-guide.html',
  './views/progress/dashboard.html',
  './views/progress/history.html',
  './views/help/faq.html',
  './views/help/audio-help.html',
  './views/help/capability.html',
  './assets/illustrations/app-river.svg',
  './assets/illustrations/rl-forest.svg',
  './assets/icons/icon-192.svg',
  './assets/icons/icon-512.svg',
  './assets/screenshots-sicar/sicar-open.svg',
  './assets/screenshots-sicar/draw-button.svg',
  './assets/screenshots-sicar/select-river.svg',
  './assets/screenshots-sicar/drag-app-margin.svg',
  './assets/screenshots-sicar/save-sync.svg',
  './assets/screenshots-sicar/rl-adjust.svg',
  './assets/screenshots-sicar/geometry-fix.svg',
  './assets/screenshots-sicar/boundary-fix.svg',
  './assets/knowledge/scripts/faq_car_oque_e.txt',
  './assets/knowledge/scripts/faq_rl_oque_e.txt',
  './assets/knowledge/scripts/faq_app_rio.txt',
  './assets/knowledge/scripts/faq_rl_amazonia.txt',
  './assets/knowledge/scripts/faq_rl_cerrado.txt',
  './assets/knowledge/scripts/faq_pequena_propriedade.txt',
  './assets/knowledge/scripts/faq_retificacao_medo.txt',
  './assets/knowledge/scripts/faq_credito_rural.txt',
  './assets/knowledge/scripts/faq_pasto_cerrado.txt',
  './assets/knowledge/scripts/faq_extrativismo.txt',
  './assets/knowledge/scripts/faq_offline_sicar.txt',
  './assets/knowledge/scripts/faq_grande_propriedade.txt',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/api/') || url.port === '8001') {
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request)
        .then((response) => {
          if (response && response.status === 200 && event.request.method === 'GET') {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => {
          if (event.request.mode === 'navigate') {
            return caches.match('./index.html');
          }
        });
    })
  );
});
