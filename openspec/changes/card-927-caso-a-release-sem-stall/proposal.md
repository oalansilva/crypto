## Why

O operador que pede «suba a release» sofre um stall no fecho: o lote sobe a produção com health ok, mas os cards ficam Homologado. O alinhamento do Caso A ainda exige develop e produção iguais (ou develop ancestral de produção com árvores idênticas), um pacote incompleto prende o teste longo ~30 min, e o fecho recusa sem dizer o que fazer se o git não for develop/release.

## What Changes

- Fecho neste turno quando o lote homologado já está em produção (cada card do lote tem commit lá) **e** a produção está contida na develop. Extra na develop (Done ainda não homologado) é inventariado como aviso, não bloqueia. Continua a bloquear se a develop não contém a produção. **Não** se exige árvores iguais nem develop ancestral de produção.
- Depois do lote em produção, um único PR devolve produção à develop (merge normal). Recusa: PR que substitui a develop pela ponta de produção; merge que descarta o lado da develop; apagar o Done da ponta e devolvê-lo depois. Ensaio: o padrão #924 sozinho passa; #926 é recusado; #913+#914+#915 deixa de ser necessário.
- Antes de abrir o PR do lote, pacote incompleto (falta ficheiro nascido noutro card, fora do lote) para localmente — não abre o PR.
- Se o build do ecrã falhou, o teste longo nem arranca; um teste longo não ocupa o runner ~30 min.
- Pedido de fecho no git de produção / `docs-*` / `sync-*`: para e diz a próxima acção (mudar para develop ou release e repetir). Não muda sozinho. A recusa não é a palavra seca `unbound`.
- Overlay passo 5b: deixa de exigir árvores idênticas; passa a «develop contém produção; extra = aviso».

**Não muda / não entra:** fechar o lote #916/#917 neste card; Homologado sem comentário (#658); campos Project vazios ao marcar Homologado (#910); caminho Caso B (#617); watcher nativo de 35 min do CI; write de produto com chat unbound; proibir Caso A; auto-switch de git; só um dos dois cortes (preflight **e** e2e fail-fast). Helper `scripts/release-casoa-closeout.sh` é MAY.

App/UI não mudam.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `release-worktree-hygiene`: alinhamento `post` passa a «produção contida na develop»; extra na develop = aviso; bloqueia se develop não contém produção; `pre` em `release-*` recusa pacote incompleto (build/typecheck local) sem abrir o PR; closeout PASS exige commit em produção por card do lote.
- `release-archive-via-release-branch`: overlay 5b e runbook mandam 1 PR merge normal produção → develop; recusam a dança de 3 PRs e o padrão #926; sync deixa de exigir árvores idênticas.
- `ci-testing-hardening`: job `e2e-playwright` depende de `frontend-build`; se o build do ecrã falhou, o teste longo não arranca.
- `process-fsm-event`: `fechar_release` em `main` / `docs-*` / `sync-*` rejeita com próxima acção (mudar para develop ou `release-*` e repetir); MUST NOT auto-switch; MUST NOT recusar só com `unbound`.

## Impact

- `scripts/release-guard` (`post` alignment; `pre` em `release-*` para pacote incompleto).
- Overlay on-demand `docs/crypto-overlay.md` passo 5b e o runbook de Caso A (skill `covenant-flow` no pin, só o recorte 5b / 1 PR). Stub always-on `AGENTS.md` não cresce.
- `.github/workflows/ci.yml`: `e2e-playwright` `needs` `frontend-build`.
- `scripts/process-fsm/process_event.py` / `t16.py` e testes injectados: recusa T16 com próxima acção.
- Specs acima. Sem produto (`backend/` / `frontend/src/`). Sem `CONTEXT.md` / `docs/adr/`. Sem dual-write Hermes/~/.codex.
- Helper `scripts/release-casoa-closeout.sh` é MAY se overlay + guard já cobrirem.
- `UI impact: none`. Prototype N/A. Snapshot N/A.
