import json,sys;sys.path.insert(0,'.')
from harness import *
reset()
U={"uid":"userIA00001","email":"a@x.com","displayName":"A"}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx,pg,errs=mkpage(b);boot(pg)
    pg.evaluate("()=>{db.sermoes.push({id:'g1',titulo:'S',topicos:[]});ajustar();gravaLocal();localStorage.setItem('pulpito.ia',JSON.stringify({p:'gemini',k:'AIza-teste',u:1}));}")
    pg.evaluate("window.__NEXT=%s"%json.dumps(U));pg.evaluate("entrarGoogle()");pg.wait_for_timeout(1200)
    pg.evaluate("document.querySelector('[data-a=migvinc]').click()");pg.wait_for_timeout(2500)
    print("NS",pg.evaluate("NS"),"| chave na conta:",pg.evaluate("iaCfg().k"),"| persiste:",pg.evaluate("localStorage.getItem('pulpito.ia.u.userIA00001')!==null"))
    pg.evaluate("location.reload()");pg.wait_for_timeout(1500)
    print("após reload:",pg.evaluate("iaCfg().k"),errs)
    b.close()
