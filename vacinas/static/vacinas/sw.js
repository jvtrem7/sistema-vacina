/* EasyVacc — service worker na raiz (/sw.js) para escopo global e instalação PWA */

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET' || req.mode !== 'navigate') {
    return;
  }
  event.respondWith(fetch(req));
});
