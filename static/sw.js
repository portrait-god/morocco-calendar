const CACHE_NAME = 'morocco-calendar-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/style.css',
    '/static/manifest.json',
    '/api/calendar'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
