import json,subprocess,time,urllib.request,os
from playwright.sync_api import sync_playwright
FAKE=open('/home/claude/pulpito-tests/fakefb.js').read()
def reset():
    urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8766/reset",data=b"{}",method="POST")).read()
def dump():
    return json.loads(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8766/dump",data=b"{}",method="POST")).read())
def mkpage(b):
    ctx=b.new_context(viewport={"width":420,"height":860});pg=ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    def rt(route):
        u=route.request.url
        route.fulfill(status=200,content_type="application/javascript",body=FAKE if u.endswith("firebase-app-compat.js") else "")
    pg.route("**/www.gstatic.com/firebasejs/**",rt)
    pg.route("**/sw.js**",lambda r:r.abort())
    return ctx,pg,errs
def boot(pg):
    pg.goto("http://localhost:8765/index.html");pg.wait_for_timeout(1200)
    pg.evaluate("db.cfg.nome='Bruno';db.cfg.nomeAsk=true;document.getElementById('modal').classList.remove('show')")
