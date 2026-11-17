import json,sys,re
sys.path.insert(0,'.')
from harness import *
R=[]
def ok(n,c,extra=""):
    R.append((n,bool(c)));print(("PASS " if c else "FAIL ")+n,extra)
reset()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx,pg,errs=mkpage(b);boot(pg)
    # --- Bíblias
    pg.evaluate("""()=>{const mk=t=>Array.from({length:66},()=>[[t]]);
      BIBS.c_a=mk('x');BIBS.c_b=mk('x');BIBS.c_c=mk('y');
      db.cfg.custom=[{k:'c_a',n:'NVI'},{k:'c_b',n:'NVI'},{k:'c_c',n:'NVI'}];db.cfg.versao='c_b';}""")
    ok("plano une só idênticas (1 repetida)", pg.evaluate("bibPlano().length")==1 and pg.evaluate("bibPlano()[0].k")=="c_b")
    pg.evaluate("bibNomes()")
    ok("versão diferente de mesmo nome é mantida e renomeada", pg.evaluate("db.cfg.custom.map(c=>c.n).join()").count("NVI (2)")==1, pg.evaluate("db.cfg.custom.map(c=>c.n).join()"))
    ok("leitura/init não remove nada", pg.evaluate("db.cfg.custom.length")==3)
    pg.evaluate("bibUne()")
    ok("união mantém uma e remove a idêntica", pg.evaluate("db.cfg.custom.map(c=>c.k).sort().join()")=="c_a,c_c")
    ok("versão selecionada migra para a mantida", pg.evaluate("db.cfg.versao")=="c_a")
    ok("Bíblia mantida segue carregada", pg.evaluate("!!BIBS.c_a&&!!BIBS.c_c"))
    # --- IA
    pg.evaluate("()=>{IA.cfg=null;localStorage.removeItem('pulpito.ia');iaCfg().k='sk-sessao-999';iaCfg().p='claude';iaCfg().persist=false;iaSave();}")
    ok("chave só de sessão não é gravada", "sk-sessao-999" not in pg.evaluate("JSON.stringify(Object.assign({},localStorage))"))
    ok("chave de sessão fica disponível em memória", pg.evaluate("iaCfg().k")=="sk-sessao-999")
    pg.evaluate("()=>{iaCfg().persist=true;iaSave();}")
    ok("com opt-in a chave persiste localmente", "sk-sessao-999" in pg.evaluate("localStorage.getItem('pulpito.ia')"))
    ok("backup não contém a chave", "sk-sessao-999" not in pg.evaluate("JSON.stringify(db)"))
    pg.evaluate("iaSave('tira')")
    ok("remover apaga cópia local", pg.evaluate("localStorage.getItem('pulpito.ia')")is None)
    # --- XSS via dados
    pg.evaluate("""()=>{db.cfg.foto='x);}body{display:none}/*';db.sermoes.push({id:'x1',titulo:'<img src=x onerror=window.PWN=9>',topicos:[]});ajustar();render();}""")
    pg.wait_for_timeout(500)
    ok("foto inválida não vira CSS", pg.evaluate("document.body.innerHTML.includes('display:none}')")==False)
    ok("título com HTML é exibido como texto", pg.evaluate("window.PWN")is None)
    pg.evaluate("()=>{V.tela='lista';V.tab='msgs';render();}")
    # --- falha de gravação
    pg.evaluate("""()=>{window.__orig=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new DOMException('x','QuotaExceededError')};}""")
    pg.evaluate("()=>{db.sermoes.push({id:'q1',titulo:'novo',topicos:[]});ajustar();salvarJa();}")
    ok("falha de gravação é sinalizada", pg.evaluate("salvoEstado().c")=="err" and pg.evaluate("!!document.getElementById('savebar')&&document.getElementById('savebar').offsetHeight>0"))
    pg.evaluate("Storage.prototype.setItem=window.__orig;gravaLocal()")
    ok("retry recupera e limpa o aviso", pg.evaluate("salvoEstado().c")!="err")
    # --- telas principais renderizam
    for t in ["msgs","agenda","biblia","mais"]:
        pg.evaluate("t=>{V.tela='lista';V.tab=t;render();}",t)
    ok("sem erros de página", not errs, errs)
    # --- SW
    sw=open('/home/claude/pulpito-repo/sw.js').read();ix=open('/home/claude/pulpito-repo/index.html').read()
    v1=re.search(r'pulpito-v(\d+)',sw).group(1);v2=re.search(r'const VER="(\d+)"',ix).group(1)
    ok("versão do SW e do app coerentes", v1==v2,(v1,v2))
    ok("SW só apaga caches do Púlpito", "/^pulpito-/.test(x)" in sw)
    ok("download incompleto derruba a instalação (mantém versão antiga)", 'throw new Error("download")' in sw)
    b.close()
print("\nRESUMO", sum(1 for _,c in R if c),"/",len(R))
