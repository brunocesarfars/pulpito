(()=>{
const S="http://127.0.0.1:8766";
const call=(p,b)=>fetch(S+p,{method:"POST",body:JSON.stringify(b)}).then(r=>r.json());
const mk=(path,id,r)=>({id,exists:r.exists,ver:r.ver,ref:null,data:()=>r.data});
function ref(path){
  const o={path,id:path.split("/").pop(),
    collection:n=>col(path+"/"+n),
    get:async()=>{const r=await call("/get",{path});const s=mk(path,o.id,r);s.ref=o;return s;},
    set:async d=>{if(window.__FAIL)throw {code:"permission-denied"};await call("/commit",{writes:[{path,data:JSON.parse(JSON.stringify(d))}]});},
    delete:async()=>{await call("/commit",{writes:[{path,del:true}]});},
    onSnapshot:(cb)=>{let last={},stop=false;const tick=async()=>{if(stop)return;try{const r=await call("/get",{path});const key=JSON.stringify(r.data);if(key!==last.k){last.k=key;cb(mk(path,o.id,r));}}catch(e){}if(!stop)setTimeout(tick,250);};tick();return()=>{stop=true;};}};
  return o;
}
function col(path){
  return {path,doc:id=>ref(path+"/"+id),
    get:async()=>{const r=await call("/list",{path});const docs=r.docs.map(d=>({id:d.id,data:()=>d.data,ref:ref(path+"/"+d.id)}));return{forEach:f=>docs.forEach(f),docs};},
    where:(f,op,v)=>({get:async()=>{const r=await call("/list",{path});const docs=r.docs.filter(d=>d.data[f]===v).map(d=>({id:d.id,data:()=>d.data,ref:ref(path+"/"+d.id)}));return{forEach:fn=>docs.forEach(fn)};}}),
    onSnapshot:(cb)=>{let seen={},stop=false;const tick=async()=>{if(stop)return;try{const r=await call("/list",{path});const ch=[];r.docs.forEach(d=>{const k=JSON.stringify(d.data);if(seen[d.id]!==k){ch.push({type:seen[d.id]?"modified":"added",doc:{id:d.id,data:()=>d.data}});seen[d.id]=k;}});if(ch.length||!seen.__i){seen.__i=1;cb({docChanges:()=>ch});}}catch(e){}if(!stop)setTimeout(tick,250);};tick();return()=>{stop=true;};}};
}
const fs={collection:n=>col(n),
  batch:()=>{const w=[];return{set:(r,d)=>w.push({path:r.path,data:JSON.parse(JSON.stringify(d))}),delete:r=>w.push({path:r.path,del:true}),commit:async()=>{await call("/commit",{writes:w});}};},
  runTransaction:async fn=>{
    for(let i=0;i<6;i++){
      const checks=[],writes=[];
      const tx={get:async r=>{const x=await r.get();checks.push({path:r.path,ver:x.ver});return x;},set:(r,d)=>writes.push({path:r.path,data:JSON.parse(JSON.stringify(d))}),delete:r=>writes.push({path:r.path,del:true})};
      if(window.__FAIL)throw {code:"permission-denied"};
      const res=await fn(tx);
      const c=await call("/commit",{checks,writes});
      if(!c.conflict)return res;
    }
    throw {code:"aborted"};
  }};
let cbs=[];const cur=()=>{try{return JSON.parse(localStorage.getItem("fake.user")||"null");}catch(e){return null;}};
const auth={get currentUser(){return cur();},onAuthStateChanged:cb=>{cbs.push(cb);setTimeout(()=>cb(cur()),30);},
  signOut:async()=>{localStorage.removeItem("fake.user");cbs.forEach(c=>c(null));},
  signInWithPopup:async()=>{const u=window.__NEXT;localStorage.setItem("fake.user",JSON.stringify(u));cbs.forEach(c=>c(u));}};
window.firebase={initializeApp:()=>{},firestore:()=>fs,auth:Object.assign(()=>auth,{GoogleAuthProvider:function(){}})};
})();
