const CACHE_NAME = 'terrapilot-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/app.js'
];

// Instalar - cachear recursos
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

// Fetch - servir do cache quando offline
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Retornar do cache ou fazer fetch
                return response || fetch(event.request);
            })
    );
});