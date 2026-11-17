import json
from playwright.sync_api import sync_playwright
bad={"sermoes":[{"id":"<img src=x onerror=window.PWN=1>","titulo":"<img src=x onerror=window.PWN=2>","topicos":[{"id":"a","titulo":"t","blocos":[{"id":"b","tipo":"texto","t":"<b>ok</b><img src=x onerror=window.PWN=3><script>window.PWN=4</script>"}]}],"status":"zzz"},
 {"id":"dup","titulo":"A"},{"id":"dup","titulo":"B"}],"eventos":[{"id":"e1","titulo":"E","data":"2026-01-01","msgId":"dup"}],"cfg":{"foto":"javascript:alert(1)","bf":"99999","tema":"x\"><svg onload=1>"}}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    pg=b.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto("http://localhost:8765/index.html");pg.wait_for_timeout(1500)
    pg.evaluate("db.cfg.nome='Bruno';db.cfg.nomeAsk=true;document.getElementById('modal').classList.remove('show')")
    def t(x): return pg.evaluate(x)
    print("invalid json:",t("(()=>{abrirRestaurar();lerRestauro('{x');return [RESTAURO,document.getElementById('toast')?.textContent]})()"))
    print("not backup:",t("(()=>{lerRestauro('{\"a\":1}');return RESTAURO})()"))
    print("bad field:",t("(()=>{lerRestauro('{\"sermoes\":[{\"titulo\":5}]}');return RESTAURO})()"))
    pg.evaluate("t=>{abrirRestaurar();lerRestauro(t)}",json.dumps(bad))
    print("valid:",t("RESTAURO&&{n:RESTAURO.sermoes.map(x=>x.id),st:RESTAURO.sermoes[0].status,msg:RESTAURO.eventos[0].msgId,cfg:RESTAURO.cfg}"))
    t("db.sermoes.length")
    before=t("db.sermoes.length")
    pg.evaluate("aplicarRestauro(false)");pg.wait_for_timeout(800)
    print("added:",before,t("db.sermoes.length"),"PWN",t("window.PWN"))
    pg.evaluate("abrirRestaurar();lerRestauro(JSON.stringify(db))");
    pg.evaluate("aplicarRestauro(true)");pg.wait_for_timeout(800)
    print("replaced:",t("db.sermoes.length"),"snaps",t("snapLista().then(l=>l.length)"),"PWN",t("window.PWN"))
    # snapshot fail blocks replace
    pg.evaluate("window.snapSalva=async()=>false;abrirRestaurar();lerRestauro(JSON.stringify(db))")
    n=t("db.sermoes.length");pg.evaluate("db.sermoes=db.sermoes.slice(0,1)");
    pg.evaluate("aplicarRestauro(true)");pg.wait_for_timeout(500)
    print("blocked keeps:",t("db.sermoes.length"),"(esperado 1)")
    print("errors:",errs)
    b.close()
