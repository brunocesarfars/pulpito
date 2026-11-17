# Firebase do Púlpito — o que fazer (eu não alterei nada na produção)

1. Abra console.firebase.google.com → projeto **pulpito-6c835** → **Firestore Database** → aba **Regras**.
2. Cole o conteúdo de `firestore.rules` e toque em **Publicar**.
3. Só publique **depois** de atualizar o Púlpito (versão 55) no celular e no tablet e abrir o app uma vez em cada um com internet. Motivo: as regras recusam envios sem o campo `rev`, que só a versão 55 em diante envia.
4. Teste: edite um sermão no celular e veja aparecer no tablet.

Limites honestos
- A chave pública (apiKey) do Firebase no código não é segredo; quem protege os dados são as regras acima.
- Sem publicar as regras, um aparelho com versão antiga do app ainda pode sobrescrever edições novas sem aviso. Com as regras publicadas, ele é recusado e mostra "Sem permissão".
- As regras não foram testadas no emulador do Firebase neste ambiente (sem acesso à rede do Firebase); a lógica de revisões do app foi testada com um Firestore simulado.
- Exclusão de um item é gravada como documento `{del:true}`; não há exclusão física.
