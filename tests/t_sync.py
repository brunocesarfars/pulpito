import json,sys
sys.path.insert(0,'.')
from harness import *
R=[]
def ok(n,c,extra=""):
    R.append((n,bool(c)));print(("PASS " if c else "FAIL ")+n,extra)
reset()
U={"uid":"userSYNC001","email":"fran@x.com","displayName":"Fran"}
def login(pg):
    pg.evaluate("window.__NEXT=%s"%json.dumps(U));pg.evaluate("entrarGoogle()");pg.wait_for_timeout(2500)
    pg.evaluate("document.getElementById('modal').classList.remove('show');db.cfg.nome='X';db.cfg.nomeAsk=true")
def T(pg,id):return pg.evaluate("id=>{const s=db.sermoes.find(x=>x.id===id);return s?s.titulo:null}",id)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    cA,A,eA=mkpage(b);cB,B,eB=mkpage(b)
    boot(A);boot(B)
    login(A);login(B)
    ok("A e B no espaço da conta", A.evaluate("NS")=="userSYNC001" and B.evaluate("NS")=="userSYNC001")
    A.evaluate("()=>{db.sermoes.push({id:'s1',titulo:'Base',topicos:[{id:'t1',titulo:'T',blocos:[{id:'b1',tipo:'texto',t:'original'}]}]});ajustar();salvarJa();}")
    A.wait_for_timeout(3000);B.wait_for_timeout(2000)
    ok("sermão criado em A chega em B", T(B,'s1')=="Base")
    # edição simples A->B
    A.evaluate("()=>{db.sermoes.find(s=>s.id==='s1').titulo='Base v2';salvarJa();}");A.wait_for_timeout(2500);B.wait_for_timeout(1500)
    ok("edição simples propaga", T(B,'s1')=="Base v2")
    # conflito: B offline edita; A edita e envia; B volta
    B.evaluate("()=>{window.__FAIL=true}")
    B.evaluate("()=>{const s=db.sermoes.find(x=>x.id==='s1');s.titulo='Versao do B';s.topicos[0].blocos[0].t='texto do B';salvarJa();}")
    A.evaluate("()=>{const s=db.sermoes.find(x=>x.id==='s1');s.titulo='Versao do A';s.topicos[0].blocos[0].t='texto do A';salvarJa();}");A.wait_for_timeout(3000)
    ok("falha de nuvem mostra estado (não 'Sincronizado')", B.evaluate("salvoEstado().t.includes('falha')||salvoEstado().t.includes('enviando')||salvoEstado().t.includes('Salvo no aparelho')"), B.evaluate("salvoEstado().t"))
    ok("edição de B segue salva no aparelho durante a falha", "Versao do B" in B.evaluate("localStorage.getItem(lsk())"))
    B.evaluate("()=>{window.__FAIL=false;syncPush();}");B.wait_for_timeout(4000);A.wait_for_timeout(2000)
    tit=B.evaluate("db.sermoes.map(s=>s.titulo)")
    ok("conflito preserva as duas versões em B", any('Versao do A'==t for t in tit) and any('Versao do B' in t and 'conflito' in t for t in tit), tit)
    txt=B.evaluate("db.sermoes.map(s=>s.topicos.map(t=>t.blocos.map(x=>x.t).join()).join()).join('|')")
    ok("textos de A e de B preservados", 'texto do A' in txt and 'texto do B' in txt, txt)
    A.wait_for_timeout(2500)
    ok("cópia de conflito também chega em A", any('conflito' in t for t in A.evaluate("db.sermoes.map(s=>s.titulo)")))
    # sem loop: contagem estável
    n1=len(dump());A.wait_for_timeout(3000);n2=len(dump());ok("sem loop/duplicação (docs estáveis)", n1==n2,(n1,n2))
    cv=A.evaluate("db.sermoes.length")
    A.wait_for_timeout(2500);ok("contagem em A estável", A.evaluate("db.sermoes.length")==cv)
    # exclusão vs edição
    B.evaluate("window.__FAIL=true")
    B.evaluate("()=>{const s=db.sermoes.find(x=>x.titulo==='Versao do A');s.titulo='Editado no B depois';salvarJa();}")
    A.evaluate("()=>{db.sermoes=db.sermoes.filter(x=>x.id!=='s1');salvarJa();}");A.wait_for_timeout(3000)
    B.evaluate("()=>{window.__FAIL=false;syncPush();}");B.wait_for_timeout(4000);A.wait_for_timeout(3000)
    ok("edição vence exclusão remota (item continua em B)", B.evaluate("db.sermoes.some(s=>s.id==='s1')"))
    ok("e volta para A", A.evaluate("db.sermoes.some(s=>s.id==='s1')"))
    # restaurar-substituir em A não apaga na nuvem
    antes=sum(1 for k in dump() if '/itens/' in k and not dump()[k]['data'].get('del'))
    A.evaluate("()=>{abrirRestaurar();lerRestauro(JSON.stringify({sermoes:[{id:'r1',titulo:'Restaurado',topicos:[]}]}));}")
    A.evaluate("aplicarRestauro(true)");A.wait_for_timeout(4000)
    dels=[k for k,v in dump().items() if v['data'].get('del')]
    ok("restaurar-substituir não gera exclusões na nuvem", not [k for k in dels if 's1' in k], dels)
    # cliente antigo escreve sem rev
    import urllib.request
    d=dump();k='users/userSYNC001/itens/s1'
    old=dict(d[k]['data']);old.pop('rev',None);old.pop('v',None);old['u']=9999999999999
    od=json.loads(old['d']);od['titulo']='Escrito por versao antiga';old['d']=json.dumps(od)
    urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8766/commit",data=json.dumps({"writes":[{"path":k,"data":old}]}).encode(),method="POST")).read()
    B.wait_for_timeout(3500)
    ok("doc sem rev (cliente antigo) é aceito sem quebrar", B.evaluate("db.sermoes.some(s=>s.id==='s1')")==True and not eB, eB)
    # dados inválidos da nuvem rejeitados
    bad={"v":2,"rev":99,"k":"s","u":9999999999999,"d":json.dumps({"id":"x","titulo":123,"topicos":"x"})}
    urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8766/commit",data=json.dumps({"writes":[{"path":"users/userSYNC001/itens/badid","data":bad}]}).encode(),method="POST")).read()
    B.wait_for_timeout(3000)
    ok("documento inválido da nuvem é rejeitado sem alterar dados", not B.evaluate("db.sermoes.some(s=>s.id==='badid')") and B.evaluate("SY.rejeit||0")>=1)
    ok("sem erros de página A/B", not eA and not eB,(eA,eB))
    b.close()
print("\nRESUMO", sum(1 for _,c in R if c),"/",len(R))
