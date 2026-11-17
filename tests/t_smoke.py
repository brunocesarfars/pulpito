import sys;sys.path.insert(0,'.')
from harness import *
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx,pg,errs=mkpage(b);boot(pg)
    pg.evaluate("()=>{const s=db.sermoes[0];abrirSermao?abrirSermao(s.id):0}") if False else None
    r=pg.evaluate("""()=>{const out=[];const s=db.sermoes[0];
      try{V.id=s.id;V.tela='edit';render();out.push('edit '+document.querySelectorAll('.blk,.bloco,textarea,[contenteditable]').length);}catch(e){out.push('edit ERR '+e.message)}
      try{V.tela='lista';V.tab='biblia';render();out.push('biblia ok')}catch(e){out.push('bib ERR '+e.message)}
      try{V.tab='mais';render();out.push('mais ok')}catch(e){out.push('mais ERR '+e.message)}
      try{abrirSheet('conta');out.push('conta '+document.getElementById('mb').innerText.slice(0,40))}catch(e){out.push('conta ERR '+e.message)}
      return out}""")
    print(r)
    # updgo offline abort
    pg.evaluate("document.getElementById('modal').classList.remove('show')")
    pg.evaluate("mostraAtualiza()");ctx.set_offline(True)
    pg.evaluate("document.querySelector('[data-a=updgo]').click()");pg.wait_for_timeout(500)
    print("toast offline:",pg.evaluate("document.getElementById('toast')&&document.getElementById('toast').innerText"), "| botão ainda disponível:",pg.evaluate("!document.querySelector('[data-a=updgo]').disabled"))
    print("errs",errs)
    b.close()
