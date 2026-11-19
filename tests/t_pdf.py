import sys;sys.path.insert(0,'.')
from harness import *
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx=b.new_context(accept_downloads=True,viewport={"width":420,"height":860});pg=ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)));pg.route("**/sw.js**",lambda r:r.abort())
    pg.goto("http://localhost:8765/index.html");pg.wait_for_timeout(1200)
    pg.evaluate("db.cfg.nome='B';db.cfg.nomeAsk=true;document.getElementById('modal').classList.remove('show')")
    pg.evaluate("""()=>{const lorem='A fidelidade de Deus não depende das nossas circunstâncias. Ele permanece fiel mesmo quando falhamos, e é nisso que a nossa esperança se firma. ';
      const s={id:'pdf1',titulo:'A Fé em Meio à Tempestade e a Fidelidade de Deus',assunto:'Confiança em Deus nas crises',pasta:'',min:35,at:1,status:'pronto',base:'Marcos 4:35-41',ideia:'Jesus está no barco conosco, e a tempestade não muda quem Ele é nem o que Ele prometeu.',hist:[],fav:false,aberto:0,topicos:[
       {id:'a',titulo:'A Tempestade Chega para Todos',ref:'Marcos 4:37',blocos:[{id:'1',tipo:'biblico',ref:'Marcos 4:37',t:'E levantou-se grande temporal de vento, e as ondas batiam dentro do barco, de modo que já se enchia.'},{id:'2',tipo:'texto',t:lorem.repeat(5)},{id:'3',tipo:'lista',t:'Ela vem sem avisar\\nEla atinge justos e injustos\\nEla revela o que há em nós'},{id:'4',tipo:'citacao',t:'Deus não prometeu céu sempre azul, mas prometeu estar no barco.',aut:'Autor desconhecido'},{id:'5',tipo:'obs',t:'Contar a história do pescador aqui. Pausar após a pergunta.'}]},
       {id:'b',titulo:'O Medo que Silencia a Fé',ref:'Marcos 4:40',blocos:[{id:'6',tipo:'texto',t:lorem.repeat(14)},{id:'7',tipo:'biblico',ref:'Marcos 4:38-40',t:'E ele estava na popa, dormindo sobre uma almofada; e despertaram-no, e disseram-lhe: Mestre, não se te dá que pereçamos? E, levantando-se, repreendeu o vento, e disse ao mar: Cala-te, aquieta-te. E o vento se acalmou, e fez-se grande bonança. E disse-lhes: Por que sois assim tímidos? Ainda não tendes fé?'}]},
       {id:'c',titulo:'Aplicação',ref:'',blocos:[{id:'8',tipo:'texto',t:lorem.repeat(8)}]}]};
      db.sermoes.push(s);ajustar();window.__s=s;}""")
    with pg.expect_download() as d:
        pg.evaluate("exportarPDF(window.__s)")
    d.value.save_as("/tmp/teste.pdf");print("errs",errs)
    b.close()
