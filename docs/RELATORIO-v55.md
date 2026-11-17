# Púlpito v55 — relatório da auditoria

## O que foi corrigido
1. **Injeção de HTML por backup/nuvem**: `validaBackup` valida e normaliza tudo numa estrutura temporária (tipos, ids `[A-Za-z0-9_-]{1,64}`, tamanhos, listas, foto só `data:image/jpeg|png|webp;base64`, configurações numéricas/enumeradas); texto rico passa por `limpa()`. Os mesmos validadores rodam nos documentos vindos da nuvem. Limites: arquivo 20 MB, 2000 sermões, 200 tópicos/sermão, 500 blocos/tópico, 5000 eventos/ilustrações. Arquivo inválido é recusado inteiro, sem mudança parcial.
2. **Falhas silenciosas de gravação**: estados explícitos (Salvando…, Salvo neste aparelho, nuvem em espera/enviando/sem internet/falha, Sincronizado ✓, Falha ao salvar) + barra permanente com "Baixar cópia" e "Tentar de novo"; cópia de emergência no IndexedDB; aviso ao fechar com falha.
3. **Dados por conta**: cada conta Google tem espaço próprio (sermões, meta de sincronização, chave de IA, Bíblias próprias, cópias). Trocar de conta recarrega o app (nenhum temporizador/resposta atrasada da conta anterior atua na nova). Sair não apaga nada. Dados antigos (sem conta): o app **pergunta** — "Vincular à conta" (com cópia de segurança antes) ou "Manter só neste aparelho". Nada vai para a nuvem sozinho.
4. **Sincronização sem perder edição**: revisão por item + transações do Firestore; conflito preserva as duas versões (a sua vira "(conflito dd/mm)") e avisa; edição vence exclusão remota; restaurar-substituir não gera exclusões na nuvem; erros classificados (rede/permissão/conflito).
5. **Restauração segura**: pré-visualização com contagens; "Substituir tudo" só depois de a cópia do estado atual ser confirmada (senão bloqueia e oferece baixar); "Adicionar" remapeia ids e vínculos evento↔sermão; metadados de outra conta não são importados; Bíblias próprias NÃO estão no backup (avisado na tela).
6. **Chave de IA**: por padrão só na memória da sessão; "lembrar neste aparelho" e "sincronizar com a conta" são opcionais e separados; remover apaga local e nuvem. Remover não cancela a chave no provedor; chave guardada no navegador é legível por qualquer script do mesmo site.
7. **Bíblias duplicadas**: identidade = conteúdo. Mesmo nome com texto diferente: ficam as duas (a nova ganha sufixo). Cópias idênticas só são unidas com sua confirmação (botão em Minhas Bíblias); nada é apagado ao abrir/ler.
8. **Firebase**: `firestore.rules` proposto + `docs/FIREBASE.md`. **Não apliquei nada em produção.**
9. **PWA**: o botão Atualizar só troca de versão se salvou suas edições e se a nova versão foi baixada; o SW só apaga caches `pulpito-*`; instalação incompleta mantém a versão antiga.

## Testes (dados fictícios; Firestore e login simulados em `tests/`)
- `t_accounts.py` 18/18, `t_sync.py` 16/16, `t_misc.py` 19/19, `t_backup.py` (segurança/restauração) ok, `t_smoke.py` ok.
- **Não executado**: regras do Firestore no emulador oficial; Firebase/Google real; aparelho físico (iPad/Android); atualização real via GitHub Pages com SW antigo.

## Limitações
- Sem publicar as regras, um aparelho com versão antiga ainda pode sobrescrever edições (o app novo trata o caso, mas não consegue impedir).
- Ajustes (configurações) em conflito: vale o mais recente.
- Backup não contém Bíblias próprias nem a chave de IA.
