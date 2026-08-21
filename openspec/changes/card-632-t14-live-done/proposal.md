## Why

O yaml T14 já descreve `integrar_develop` com guarda `checks_green` e ações `squash`, `restart`, `comment_done`, `set_status` (I8: falha ⇒ permanece QA). O #612 deixou o live fail-closed com `checks_green` unset: o Agent não fecha Done e o `./restart` canônico em DEV vira prosa. Cards novos entram em `develop` e o runtime DEV continua no bundle antigo; Alan não consegue homologar o que o board diz que está Done.

## What Changes

- `process_event integrar_develop` no live **mede** `checks_green` (CI `qa-gate` verde no PR da branch `card-<id>-*` contra `develop`). Sem `--checks-green` na CLI. Predicado False/None/erro de medição ⇒ reject, sem squash, sem restart, sem mover.
- Com guarda verdadeira, o script executa as ações Mealy **em ordem, atômicas (I8)**: squash (ou confirma merge já em `develop`) → `./restart` canônico em `/srv/apps/dev/criptofarol/source` → health interno DEV 200 com retry (já no script `restart`) → `comment_done` → `set_status(Done)`.
- Falha em squash ou restart ⇒ Status permanece QA; mover **não** é chamado.
- `--dry-run` avalia δ e **não** faz squash, restart, comentário nem mover.
- `homologar` e `fechar_release` continuam reject para o Agent. T16/PROD fora.
- pytest `scripts/process-fsm` cobre: verde+ações ok → Done; unset/CI vermelho → reject; falha de squash/restart → reject e mover vazio.
- **Não** é aceite um apply que só arrasta Done sem `./restart`.

## Capabilities

### New Capabilities

- (nenhuma) — T14 já existe na tabela; este card liga a compilação live.

### Modified Capabilities

- `process-fsm-event`: live `integrar_develop` deixa de reject permanente; mede `checks_green`, executa squash+restart atômicos e só então move Done.
- `process-fsm`: I8 deixa de ser invariante só no yaml — o runtime T14 MUST honrar falha ⇒ permanece QA.
- `cursor-harness`: closeout Done do Agent é `process_event integrar_develop` (não `item-edit` nem `./restart` solto no worktree).

## Impact

- Altera `scripts/process-fsm/process_event.py` e `test_process_event.py` (e helpers de medição/ações injetáveis no mesmo pacote).
- Pode alterar `scripts/process-fsm/fsm.py` só se o evaluate de T14 precisar de predicado extra; yaml T14/I8 já estão corretos.
- Consome `scripts/post-card-evidence-comment.sh --transition done` para `comment_done`.
- Restart **somente** `/srv/apps/dev/criptofarol/source/restart` (o `restart` no worktree recusa path não canônico). Não toca PROD, `backend/` de produto, `frontend/src/`, nem o Guard de `git commit`/`./restart`.
- Job CI `process-fsm` existente. `UI impact: none`. Prototype N/A.
- Origem: kaizen #632 (release 2026-08-20 lote 612 F-2) + pedido Alan 2026-08-21 (restart automático nos cards novos).
