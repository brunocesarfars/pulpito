import sys;sys.path.insert(0,'.')
from harness import *
R=[]
def ok(n,c,x=""):
    R.append(bool(c));print(("PASS " if c else "FAIL ")+n,x)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx,pg,errs=mkpage(b);boot(pg)
    # --- import: cabeçalhos
    r=pg.evaluate("""()=>{
      const bl=[{k:'p',t:'Título do Sermão'},
        {k:'p',t:'Introdução Bom dia, igreja. Hoje vamos falar sobre a fidelidade de Deus em todos os momentos da nossa vida, e isso muda tudo.'},
        {k:'p',t:'Tópico 1 – Deus é fiel'},{k:'p',t:'A fidelidade de Deus não depende de nós. Ele permanece fiel mesmo quando falhamos.'},
        {k:'p',t:'Tópico 2: Deus cuida'},{k:'p',t:'Ele cuida dos pássaros e muito mais de você, como diz o texto.'},
        {k:'p',t:'Conclusão, portanto, é que Deus é bom.'},
        {k:'p',t:'Conclusão'},{k:'p',t:'Termine confiando.'}];
      const x=estruturar(bl,'a.pdf');return x.topicos.map(t=>t.titulo+' ['+t.blocos.length+']')}""")
    print(r)
    ok("importação reconhece Introdução, Tópico 1, Tópico 2, Conclusão", len(r)>=4 and any(t.startswith("Introdução") for t in r) and any("Deus é fiel" in t for t in r) and any("Deus cuida" in t for t in r) and any(t.startswith("Conclusão") for t in r))
    ok("'Conclusão, portanto…' no meio do texto não vira cabeçalho", not any("portanto" in t for t in r))
    # --- editor
    pg.evaluate("""()=>{abrirNovo();document.getElementById('nv-t').value='T';document.querySelector('[data-a=nvok]').click();
      const s=cur();const t=s.topicos[0];t.blocos=[{id:'p1',tipo:'texto',t:'Parágrafo um'},{id:'p2',tipo:'texto',t:'Parágrafo dois'},{id:'p3',tipo:'texto',t:'Parágrafo três'},{id:'p4',tipo:'texto',t:'Parágrafo quatro'}];V.ab=new Set([t.id]);rerender();}""")
    ok("barra tem Versículo, ✂ Tópico e Selecionar", pg.evaluate("['seltopico','bselmode'].every(a=>!!document.querySelector('[data-a='+a+']'))&&!!document.querySelector('[data-a=ins][data-v=biblico]')"))
    ok("sem botão fixo extra", pg.evaluate("!document.querySelector('.vbtn')"))
    # seleção múltipla
    pg.evaluate("document.querySelector('[data-a=bselmode]').click()")
    ok("modo seleção ativo", pg.evaluate("document.body.classList.contains('bselmode')&&!!document.getElementById('bselbar')"))
    pg.evaluate("()=>{for(const id of ['p2','p3','p4'])document.querySelector('[data-bid='+id+']').click()}")
    ok("seleciona vários parágrafos", pg.evaluate("V.bsel.size")==3, pg.evaluate("document.getElementById('bselbar').innerText"))
    pg.evaluate("document.querySelector('[data-a=bsel-topico]').click()")
    r=pg.evaluate("cur().topicos.map(t=>[t.titulo,t.blocos.length])")
    ok("parágrafos selecionados viram novo tópico", len(r)==7 and r[0][1]==1 and r[1][1]==2 and r[1][0]=="Parágrafo dois", r)
    ok("modo seleção sai ao concluir", pg.evaluate("!V.bsel&&!document.getElementById('bselbar')"))
    # mover
    pg.evaluate("""()=>{const s=cur();s.topicos[0].blocos.push({id:'q1',tipo:'texto',t:'Mover-me'});V.ab=new Set([s.topicos[0].id]);rerender();document.querySelector('[data-a=bselmode]').click();document.querySelector('[data-bid=q1]').click();document.querySelector('[data-a=bsel-mover]').click();}""")
    pg.evaluate("document.querySelector('#mb [data-a=bsel-para]:last-child').click()")
    ok("mover parágrafo para outro tópico", pg.evaluate("cur().topicos[cur().topicos.length-1].blocos.some(b=>b.id==='q1')&&!cur().topicos[0].blocos.some(b=>b.id==='q1')"))
    # trecho -> tópico
    pg.evaluate("""()=>{const s=cur();const t=s.topicos[0];t.blocos=[{id:'z1',tipo:'texto',t:'Antes do corte. TRECHO ESCOLHIDO AQUI com várias palavras que passam de noventa caracteres para virar bloco e não título, certo? Depois do corte.'}];V.ab=new Set([t.id]);rerender();
      const rt=document.querySelector('[data-bid=z1] .rt');const tn=rt.firstChild;const i=tn.data.indexOf('TRECHO'),j=tn.data.indexOf(' Depois');
      const r=document.createRange();r.setStart(tn,i);r.setEnd(tn,j);const sel=getSelection();sel.removeAllRanges();sel.addRange(r);}""")
    n0=pg.evaluate("cur().topicos.length")
    pg.evaluate("document.querySelector('[data-a=seltopico]').click()")
    r=pg.evaluate("({n:cur().topicos.length,a:plain(cur().topicos[0].blocos[0].t),b:cur().topicos[1].blocos.length?plain(cur().topicos[1].blocos[0].t):cur().topicos[1].titulo})")
    ok("texto selecionado vira novo tópico", r["n"]==n0+1 and "TRECHO" in r["b"] and "TRECHO" not in r["a"] and "Antes do corte" in r["a"] and "Depois do corte" in r["a"], r)
    # trecho curto vira título
    pg.evaluate("""()=>{const s=cur();const t=s.topicos[0];t.blocos=[{id:'y1',tipo:'texto',t:'Intro. Deus é fiel. Resto.'}];V.ab=new Set([t.id]);rerender();
      const rt=document.querySelector('[data-bid=y1] .rt');const tn=rt.firstChild;const i=tn.data.indexOf('Deus'),j=tn.data.indexOf('fiel.')+5;
      const r=document.createRange();r.setStart(tn,i);r.setEnd(tn,j);const sel=getSelection();sel.removeAllRanges();sel.addRange(r);}""")
    pg.evaluate("document.querySelector('[data-a=seltopico]').click()")
    ok("trecho curto vira título do tópico", pg.evaluate("cur().topicos[1].titulo")=="Deus é fiel.", pg.evaluate("cur().topicos[1].titulo"))
    ok("sem erros de página", not errs, errs)
    b.close()
print("RESUMO",sum(R),"/",len(R))
