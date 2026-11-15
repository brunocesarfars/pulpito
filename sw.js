const C="pulpito-v39",AS="pulpito-assets-1",A=["./","index.html","manifest.webmanifest","icon-192.png","icon-512.png"],B=["fonts/bricolage.woff2","fonts/dmsans.woff2","lib/pdf.js","lib/pdf.worker.js","lib/jspdf.js","lib/mammoth.js"];
const pesado=u=>/\/(lib|fonts)\/|\/bib-[a-z]+\.json$/.test(new URL(u).pathname);
self.addEventListener("install",e=>{e.waitUntil(Promise.all([
  caches.open(C).then(c=>Promise.all(A.map(u=>fetch(new Request(u,{cache:"reload"})).then(r=>r.ok&&c.put(u,r))))),
  caches.open(AS).then(c=>Promise.all(B.map(u=>c.match(u).then(m=>m||fetch(u).then(r=>r.ok&&c.put(u,r)).catch(()=>{})))))
]));});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C&&x!==AS).map(x=>caches.delete(x)))).then(()=>self.clients.claim()));});
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  const mesma=new URL(e.request.url).origin===location.origin;
  if(mesma&&pesado(e.request.url)){
    e.respondWith(caches.open(AS).then(c=>c.match(e.request).then(m=>m||fetch(e.request).then(r=>{if(r.ok)c.put(e.request,r.clone());return r;}))));
    return;
  }
  e.respondWith(fetch(e.request,mesma?{cache:"no-cache"}:undefined).then(r=>{if(r.ok&&mesma){const c=r.clone();caches.open(C).then(x=>x.put(e.request,c));}return r;}).catch(()=>caches.match(e.request).then(m=>m||caches.match("index.html"))));
});
self.addEventListener("message",e=>{if(e.data==="skip")self.skipWaiting();});
