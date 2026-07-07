/* Mermaid Dots service worker — network-first so every deploy shows up on
   the next launch, with the cached copy as an offline fallback. */
const CACHE = "mermaid-dots-v2";
const CORE = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  // Video/audio streams use byte-range requests, which this simple cache
  // can't answer correctly (a 200-for-206 reply stalls the <video> element
  // and cache.put() rejects partial responses). Let media hit the network
  // directly; the game falls back to the flipbook when offline anyway.
  if (e.request.headers.get("range") || /\.(mp4|webm)(\?|$)/.test(e.request.url)) return;
  e.respondWith(
    fetch(e.request)
      .then(resp => {
        const copy = resp.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return resp;
      })
      .catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
