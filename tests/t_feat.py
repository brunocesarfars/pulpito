import sys,json;sys.path.insert(0,'.')
from harness import *
R=[]
def ok(n,c,x=""):
    R.append(bool(c));print(("PASS " if c else "FAIL ")+n,x)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx,pg,errs=mkpage(b);boot(pg)
    # novo sermão com dicas
    pg.evaluate("()=>{abrirNovo();document.getElementById('nv-t').value='Teste Fé';document.querySelector('[data-a=nvok]').click();}")
    pg.wait_for_timeout(400)
    ok("estrutura guiada cria tópicos com dica", pg.evaluate("(()=>{const s=cur();return s.topicos.length===6&&!!s.topicos[0].dica})()"))
    ok("dica aparece no editor", pg.evaluate("!!document.querySelector('.dica')"))
    # texto para busca
    pg.evaluate("()=>{const s=cur();s.topicos[1].blocos.push({id:'bb1',tipo:'texto',t:'A <b>tempestade</b> chegou de repente sobre os discípulos no mar'});s.topicos[1].blocos.push({id:'bb2',tipo:'texto',t:'x '.repeat(300)});salvarJa();}")
    # ensaio: simula tempo
    pg.evaluate("()=>{abrirPregar(cur().id,true)}")
    ok("modo ensaio mostra ENSAIO", "ENSAIO" in pg.evaluate("document.getElementById('preach').innerText"))
    pg.evaluate("()=>{P.t0=Date.now();P.lt=Date.now()-1;}")
    pg.wait_for_timeout(1500)
    pg.evaluate("()=>{const s=cur();P.tt[s.topicos[0].id]=95000;P.tt[s.topicos[1].id]=210000;P.acc=305000;}")
    pg.evaluate("sairPregar()");pg.wait_for_timeout(300)
    ok("resultado do ensaio abre", pg.evaluate("document.getElementById('mb').innerText.includes('Resultado do ensaio')"), pg.evaluate("document.getElementById('mb').innerText.slice(0,120)"))
    ok("ensaio NÃO registra pregação", pg.evaluate("cur().hist.length")==0)
    pg.evaluate("document.querySelector('[data-a=ensok]').click()")
    ok("ensaio guardado", pg.evaluate("cur().ens&&cur().ens.length")==1)
    # pregação real com alerta de 5 min
    pg.evaluate("()=>{cur().min=12;abrirPregar(cur().id,false)}")
    pg.evaluate("()=>{window.__t=[];const o=window.toast;window.toast=(m)=>{window.__t.push(m);};P.t0=Date.now();P.acc=7*60000+5000;}")
    pg.wait_for_timeout(600)
    ok("alerta de 5 minutos dispara", "Faltam 5 minutos" in pg.evaluate("window.__t"), pg.evaluate("window.__t"))
    pg.evaluate("()=>{P.acc=11*60000+5000;P.t0=Date.now();}");pg.wait_for_timeout(600)
    ok("alerta de 1 minuto dispara", "Falta 1 minuto" in pg.evaluate("window.__t"))
    pg.evaluate("()=>{const s=cur();P.tt[s.topicos[0].id]=120000;P.t0=null;P.acc=720000}")
    pg.evaluate("sairPregar()");pg.wait_for_timeout(300)
    ok("registro abre com duração", pg.evaluate("document.getElementById('mb').innerText.includes('Registrar pregação')"))
    pg.evaluate("()=>{document.getElementById('r-local').value='Igreja Central'}")
    pg.evaluate("document.querySelector('[data-a=regok]').click()")
    ok("histórico guarda tempo por tópico", pg.evaluate("cur().hist[0].tt&&cur().hist[0].tt.length>0"), pg.evaluate("JSON.stringify(cur().hist[0].tt)"))
    # aviso de repetição
    pg.evaluate("()=>{REG={id:cur().id,min:5,tt:[]};abrirRegistro(cur().id,5,[]);document.getElementById('r-local').value='igreja central';window.__t=[];const tt=window.toast;window.toast=m=>window.__t.push(m);document.querySelector('[data-a=regok]').click();}")
    pg.wait_for_timeout(700)
    ok("avisa que já pregou no mesmo local", any("já pregou" in m for m in pg.evaluate("window.__t")), pg.evaluate("window.__t"))
    # histórico tela
    pg.evaluate("abrirHistPreg()")
    ok("tela de histórico lista pregações", pg.evaluate("document.querySelectorAll('.hpr').length")>=2)
    pg.evaluate("()=>{const e=document.getElementById('hp-q');e.value='central';e.dispatchEvent(new Event('input',{bubbles:true}))}")
    ok("busca no histórico filtra", pg.evaluate("document.querySelectorAll('.hpr').length")>=2)
    pg.evaluate("fechar()")
    # busca com trecho
    pg.evaluate("()=>{V.tela='lista';V.tab='msgs';V.q='tempestade';render();}")
    ok("busca mostra trecho com destaque", pg.evaluate("!!document.querySelector('.trecho mark')"), pg.evaluate("(document.querySelector('.trecho')||{}).innerText"))
    pg.evaluate("()=>{V.q='';}")
    # Word
    pg.evaluate("()=>{window.__b=null;const oc=URL.createObjectURL;URL.createObjectURL=b=>{window.__b=b;return oc(b)}}")
    pg.evaluate("()=>{V.tela='edit';V.id=cur().id;render();exportarDOC(cur())}")
    ok("exporta Word (.doc) com conteúdo", pg.evaluate("window.__b&&window.__b.size>500"))
    txt=pg.evaluate("window.__b.text()")
    ok("doc contém título e tópicos", "Teste Fé" in txt and "tempestade" in txt and "Introdução" in txt)
    # IA histórico
    pg.evaluate("()=>{IA.cfg=null;IA.msgs=[{r:'u',t:'Pergunta teste'},{r:'a',t:'Resposta teste'}];IA.cid='';iaHSalva();}")
    ok("conversa da IA guardada localmente", pg.evaluate("iaHLe().length")==1 and pg.evaluate("!!localStorage.getItem(iaHK())"))
    pg.evaluate("()=>{IA.msgs=[];IA.cid='';abrirIAHist();}")
    pg.evaluate("document.querySelector('[data-a=iaabre]').click()")
    ok("reabre conversa", pg.evaluate("IA.msgs.length")==2)
    ok("conversa não está no backup", "Pergunta teste" not in pg.evaluate("JSON.stringify(db)"))
    # validação preserva campos novos
    r=pg.evaluate("()=>{const x=validaBackup(JSON.parse(JSON.stringify(db)));const s=x.sermoes.find(z=>z.titulo==='Teste Fé');return {dica:!!s.topicos[0].dica,tt:!!(s.hist[0]&&s.hist[0].tt&&s.hist[0].tt.length),ens:!!(s.ens&&s.ens.length)}}")
    ok("validação preserva dica, tempos e ensaio", all(r.values()), r)
    # tiles
    pg.evaluate("()=>{V.tela='lista';V.tab='mais';render();}")
    ok("tile Histórico em Mais", "Histórico de pregações" in pg.evaluate("document.getElementById('app').innerText"))
    ok("sem erros de página", not errs, errs)
    b.close()
print("RESUMO",sum(R),"/",len(R))
