## Why

Com a cota GraphQL a 0, Alan não grelha nem move card, e o harness trata o card como se não estivesse no board — ao mesmo tempo o contador REST diz que ainda há 5000 pontos GraphQL. Relacionada, **não** duplicata de #509 / #516: aqueles fecharam a fotografia completa do board no fecho de lote; a cota GraphQL continua a zerar grelha, Status pontual e evidência.

## What Changes

- Superfície issue (body, comentários, labels): leitura e escrita REST. A vista JSON da issue só se o REST não cobrir o campo. Grelha que só reescreve o body: PATCH REST da issue funciona com cota GraphQL a 0.
- A cota GraphQL que manda é a da resposta GraphQL (cabeçalhos, ou o campo de cota da query quando ela passa). O contador REST com remaining=5000 **não** autoriza GraphQL.
- Status de um card N no Project 1: consulta pontual daquele card. Nunca listar o board inteiro para operar um card.
- GraphQL a 0 / RATE_LIMIT (incluindo HTTP 200 com erro RATE_LIMIT no corpo): falha na hora com a hora de reset (Q1=A); não esperar o reset no mesmo comando; não repetir a chamada em ciclo; não tratar Status desconhecido como card fora do board.
- Fecho de lote: o número de cota GraphQL impresso após falha da fotografia vem dos cabeçalhos GraphQL, não do contador REST (Q2=A). A fotografia completa permanece o recorte do #509 (uma por execução).
- Loop periódico (`process_event` / `aceitar_sha`): deixa de bater GraphQL a 0 (cache do reset dos cabeçalhos; sem hang, sem storm). Trocar token / auto-dsh **não entra**.
- Skills `grill-card` / `github-project-board` / `kaizen` e `post-card-evidence-comment.sh` passam a REST na superfície issue.
- **Não entra:** reabrir HTML/apply do #790; reabrir o recorte do #509; esperar o reset GraphQL no mesmo comando (Q1≠B); deixar o fecho de lote a imprimir o remaining do contador REST (Q2≠B); consertar o bug da API GitHub no contador REST; código de produto; ligar/desligar o dsh sozinho; inventar REST para a coluna do Project (não existe; mover coluna continua GraphQL e fica impossível com GraphQL a 0).

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `process-fsm-guard`: `github_status_provider` parseia cabeçalhos GraphQL / `rateLimit` / RATE_LIMIT no corpo; remaining=0 não vira `None` silencioso; REST remaining=5000 não autoriza GraphQL; Status continua pontual (nunca `item-list` para um card).
- `process-fsm-paging`: card bound com coluna desconhecida (cota a 0 / RATE_LIMIT) **não** escreve página unbound (`bound_card=⊥`); falha na hora com a hora de reset.
- `process-fsm-event`: `_item_id_for_issue` / mover GraphQL falham na hora com reset; loop periódico não re-dispara GraphQL até o reset; não rejeita como unbound / card fora do board.
- `grill-card`: body/comentários/labels via REST (`gh issue edit` / PATCH); MUST NOT `gh issue view` (GraphQL). PATCH do body funciona com cota GraphQL a 0.
- `release-worktree-hygiene`: diagnóstico pós-falha da fotografia imprime remaining/reset dos **cabeçalhos GraphQL** da resposta que falhou, não `GET /rate_limit` `.resources.graphql` (substitui D5 do #509 sem reabrir a fotografia).
- `kaizen-continuous-improvement`: evidência de issue em REST; Status de um card = consulta pontual; MUST NOT listar o board inteiro para operar um card; GraphQL a 0 = falha na hora com reset.
- `documental-board-evidence-validation`: `post-card-evidence-comment.sh` lê comentários por REST, não `gh issue view --json comments`.

## Impact

- Altera (Apply, após Pronto para Dev): `scripts/process-fsm/guard.py` (`github_status_provider` + cache de reset), `paging.py`, `process_event.py` (`_item_id_for_issue`, rejeição de cota), testes `test_guard.py` / `test_paging.py` / `test_process_event.py`; `scripts/post-card-evidence-comment.sh`; `scripts/release-guard` `snapshot_fail_diagnose`; skills `.cursor/skills/grill-card/SKILL.md`, `.cursor/skills/github-project-board/` (SKILL + references), `.cursor/skills/kaizen/SKILL.md` (+ peles thin MUST Read inalteradas em tamanho); goldens REST vs GraphQL (REST remaining=5000 + cabeçalhos GraphQL 0).
- Não toca `backend/` / `frontend/src/`, `DESIGN.md`, HTML, `process-fsm.yaml` Σ/colunas, pin `covenant-flow`, Auto, troca de token.
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A.
- Origem: issue #820. Relacionado e **não** reaberto: #509, #516, #790.
