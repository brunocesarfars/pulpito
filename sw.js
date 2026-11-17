const C="pulpito-v53",AS="pulpito-assets-1",A=["./","index.html","manifest.webmanifest","icon-192.png","icon-512.png"],B=["fonts/bricolage.woff2","fonts/dmsans.woff2","lib/pdf.js","lib/pdf.worker.js","lib/jspdf.js","lib/mammoth.js"];
const pesado=u=>/\/(lib|fonts)\/|\/bib-[a-z]+\.json$/.test(new URL(u).pathname);
self.addEventListener("install",e=>{self.skipWaiting();e.waitUntil(Promise.all([
  caches.open(C).then(c=>Promise.all(A.map(u=>fetch(new Request(u,{cache:"reload"})).then(r=>r.ok&&c.put(u,r))))),
  caches.open(AS).then(c=>Promise.all(B.map(u=>c.match(u).then(m=>m||fetch(u).then(r=>r.ok&&c.put(u,r)).catch(()=>{})))))
]));});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C&&x!==AS).map(x=>caches.delete(x)))).then(()=>self.clients.claim()));});
self.addEventListener("fetch",e=>{
  const r=e.request;if(r.method!=="GET")return;
  const u=new URL(r.url);if(u.origin!==location.origin)return;
  if(pesado(r.url)){
    e.respondWith(caches.open(AS).then(c=>c.match(r).then(m=>m||fetch(r).then(x=>{if(x.ok)c.put(r,x.clone());return x;}))));
    return;
  }
  if(u.pathname.endsWith("/sw.js")||u.searchParams.has("_"))return;
  /* Abre na hora com a cópia guardada (funciona sem internet) e atualiza por trás */
  e.respondWith(caches.open(C).then(async c=>{
    const m=(await c.match(r,{ignoreSearch:true}))||(r.mode==="navigate"?await c.match("index.html"):null);
    const rede=fetch(r,{cache:"no-cache"}).then(x=>{if(x.ok)c.put(r,x.clone());return x;});
    if(m){e.waitUntil(rede.catch(()=>{}));return m;}
    return rede.catch(()=>caches.match("index.html"));
  }));
});
self.addEventListener("message",e=>{if(e.data==="skip")self.skipWaiting();});
