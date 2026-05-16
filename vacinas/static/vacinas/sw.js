/* EasyVacc — PWA instalável + cache mínimo da página inicial (pública).

   Sem rede: apenas a rota '/' pode aparecer em cache (último HTML visitado /
   pré-cache). Áreas logadas e API continuam exigindo conexão. */

const CACHE = 'easyvacc-static-v2';
const HOMEPAGES = ['/']; // apenas rotas públicas seguras para fallback offline

function homeUrlCandidates() {
  const base = self.registration.scope;
  return HOMEPAGES.map((p) => new URL(p, base).href);
}

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      .then((cache) =>
        cache.addAll(homeUrlCandidates()).catch(() => {
          /* rede indisponível no install ou bloqueio: ignora */
        }),
      ),
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((k) => k !== CACHE && k.startsWith('easyvacc-static-'))
            .map((k) => caches.delete(k)),
        ),
      )
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  const isSameOrigin = url.origin === self.location.origin;

  /* Navegação: rede primeiro; atualiza cache da home só se for página inicial */
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((response) => {
          if (
            response &&
            response.status === 200 &&
            response.type === 'basic' &&
            isSameOrigin &&
            HOMEPAGES.includes(url.pathname)
          ) {
            const clone = response.clone();
            caches.open(CACHE).then((cache) => cache.put(req, clone));
          }
          return response;
        })
        .catch(() => {
          /* offline: só servir cache para a página inicial explícita */
          if (
            isSameOrigin &&
            HOMEPAGES.includes(url.pathname)
          ) {
            return caches.match(new URL('/', self.registration.scope).href);
          }
          return Response.error();
        }),
    );
    return;
  }

  /* Demais GET: passa direto pela rede */
});
