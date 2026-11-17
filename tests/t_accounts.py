import json,sys
sys.path.insert(0,'.')
from harness import *
R=[]
def ok(n,c,extra=""):
    R.append((n,bool(c)));print(("PASS " if c else "FAIL ")+n,extra)
reset()
U1={"uid":"user1AAAAAA","email":"fran@x.com","displayName":"Fran"};U2={"uid":"user2BBBBBB","email":"outro@x.com","displayName":"Outro"}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx,pg,errs=mkpage(b)
    boot(pg)
    pg.evaluate("""()=>{db.sermoes.push({id:'g1',titulo:'Sermao guest',topicos:[]});db.sermoes.push({id:'g2',titulo:'Outro guest',topicos:[]});ajustar();gravaLocal();}""")
    pg.evaluate("window.__NEXT=%s"%json.dumps(U1))
    pg.evaluate("entrarGoogle()");pg.wait_for_timeout(1200)
    ok("modal de migração aparece (sem envio automático)", pg.evaluate("document.getElementById('modal').classList.contains('show')&&!!document.querySelector('[data-a=migvinc]')"))
    ok("nada enviado à nuvem antes da escolha", len(dump())==0, dump().keys())
    ok("sem troca de espaço antes da escolha", pg.evaluate("NS===''"))
    pg.evaluate("document.querySelector('[data-a=migvinc]').click()");pg.wait_for_timeout(2500)
    ok("espaço da conta ativo após vincular", pg.evaluate("NS==='user1AAAAAA'"))
    ok("sermões vinculados na conta", pg.evaluate("db.sermoes.filter(s=>!s.ex).length")==2)
    ok("dados guest continuam intactos", pg.evaluate("JSON.parse(localStorage.getItem('pulpito.v1')).sermoes.length")>=2)
    ok("cópia de segurança do guest criada", pg.evaluate("indexedDB.databases().then(l=>l.some(d=>d.name==='pulpito-snap'))"))
    pg.wait_for_timeout(2500)
    d=dump();ok("sincronizou itens da conta (g1,g2) na nuvem", any(k.endswith('/itens/g1') for k in d) and any(k.endswith('/itens/g2') for k in d), [k for k in d][:5])
    ok("docs com v:2 e rev", all(v['data'].get('v')==2 and v['data'].get('rev',0)>=1 for k,v in d.items() if '/itens/' in k))
    # edita na conta
    pg.evaluate("()=>{db.sermoes.find(s=>s.id==='g1').titulo='Editado na conta';salvarJa();}");pg.wait_for_timeout(2000)
    # sair
    pg.evaluate("sairConta()");pg.wait_for_timeout(2500)
    ok("voltou ao espaço sem conta", pg.evaluate("NS===''"))
    ok("guest não mostra edição da conta", pg.evaluate("db.sermoes.find(s=>s.id==='g1').titulo")=="Sermao guest")
    ok("dados da conta continuam no aparelho", pg.evaluate("!!localStorage.getItem('pulpito.v1.u.user1AAAAAA')"))
    # segunda conta
    pg.evaluate("window.__NEXT=%s"%json.dumps(U2));pg.evaluate("document.getElementById('modal').classList.remove('show')")
    pg.evaluate("entrarGoogle()");pg.wait_for_timeout(1200)
    ok("segunda conta também pergunta (não herda dono)", pg.evaluate("!!document.querySelector('[data-a=mignao]')"))
    pg.evaluate("document.querySelector('[data-a=mignao]').click()");pg.wait_for_timeout(2500)
    ok("conta 2 em espaço vazio, sem dados da conta 1", pg.evaluate("NS==='user2BBBBBB'&&db.sermoes.filter(s=>!s.ex).length")==0)
    pg.wait_for_timeout(2000)
    d=dump();ok("nada da conta 1 foi para o caminho da conta 2", not any('user2BBBBBB/itens/g' in k for k in d))
    # chave de IA por conta
    pg.evaluate("()=>{iaCfg().k='sk-teste-123';iaCfg().p='claude';iaCfg().persist=true;iaSave();}")
    ok("chave gravada só no espaço da conta 2", pg.evaluate("!!localStorage.getItem('pulpito.ia.u.user2BBBBBB')&&!localStorage.getItem('pulpito.ia')"))
    pg.evaluate("sairConta()");pg.wait_for_timeout(2500)
    ok("guest sem chave da conta 2", pg.evaluate("!iaCfg().k"))
    ok("sem erros de página", not errs, errs)
    b.close()
print("\nRESUMO", sum(1 for _,c in R if c),"/",len(R))
