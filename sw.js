// HWO Autocue service worker: network first (so new scripts show up straight away), cache fallback for offline.
const CACHE='autocue-v2';
const SHELL=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png','scripts/index.json'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
const keyOf=req=>{const u=new URL(req.url);u.search='';return u.href};
self.addEventListener('fetch',e=>{
  const req=e.request;if(req.method!=='GET')return;
  const url=new URL(req.url);
  if(url.origin!==location.origin){ // fonts: cache first
    e.respondWith(caches.match(req).then(r=>r||fetch(req).then(res=>{const c=res.clone();caches.open(CACHE).then(x=>x.put(req,c));return res}).catch(()=>r)));return;
  }
  e.respondWith(fetch(req,{cache:'no-store'}).then(res=>{
    if(res.ok){const c=res.clone();caches.open(CACHE).then(x=>x.put(keyOf(req),c));
      if(url.pathname.endsWith('scripts/index.json')){res.clone().json().then(j=>caches.open(CACHE).then(x=>Promise.all((j.scripts||[]).map(s=>fetch('scripts/'+s.file,{cache:'no-store'}).then(r=>r.ok&&x.put(new URL('scripts/'+s.file,location.href.replace(/sw\.js.*$/,'')).href,r)).catch(()=>{}))))).catch(()=>{})}
    }
    return res;
  }).catch(()=>caches.match(keyOf(req)).then(r=>r||caches.match('index.html'))));
});
