## Why

O yaml T16 já descreve `fechar_release` com guarda `M_lote` e ações `release_guard`, `deploy_prod`, `set_status`. O live recusa o Agent (`actor=Alan`, `m_lote` default False, sessão unbound em `develop`). O closeout publica `main`+PROD e o board fica Homologado. Homologar (T15) é julgamento; Pronto depois de `release-guard post` PASS é o mesmo tipo de medição que T14/`qa-gate`.

## What Changes

- T16.actor passa a Agent. I2 / `ALAN_GATES` / `harness.mdc` deixam T16 de ser gate humano. T1, T7 e T15 continuam Alan.
- Live `process_event fechar_release` **mede** `M_lote` (`release-guard post` exit 0). Sem `--m-lote` na CLI. Predicado False/None/erro ⇒ reject `guard:M_lote`, sem closer e sem mover.
- Com guarda verdadeira, move os membros ainda Homologado → Pronto e posta o comentário Pronto canônico. Membro já Pronto = skip idempotente. Qualquer outro Status ou id ausente ⇒ reject `I9`, mover vazio.
- Evento de lote: válido em `q_git=develop` (ou `release-*`) sem worktree `card-<id>`. `--card` sozinho vale como pacote de um id.
- **Não** reexecuta deploy PROD nem merge em `main` dentro de `process_event`. `M_lote` prova que isso já ocorreu (post exige `PROD_DEPLOY_EVIDENCE`).
- `--dry-run` avalia δ (medição read-only) e não comenta nem move.
- pytest cobre: Agent+M_lote→Pronto; ¬M_lote→reject; unbound develop não bloqueia T16; card não Homologado→reject; T15 continua reject.

## Capabilities

### New Capabilities

- (nenhuma) — T16 já existe na tabela; este card liga a compilação live e troca o ator.

### Modified Capabilities

- `process-fsm`: T16.actor Agent; validator deixa de exigir Alan em `fechar_release`; I2 sem T16.
- `process-fsm-event`: `fechar_release` deixa de ser reject permanente do Agent; mede `M_lote`, fecha o pacote em Pronto; unbound de lote permitido.
- `cursor-harness`: closeout Pronto do Agent é `process_event fechar_release` após post PASS; Alan-only fica T1/T7/T15.

## Impact

- Altera `.cursor/process-fsm.yaml` (T16.actor, I2, `enabled_tools`/`context_file` Homologado), `scripts/process-fsm/process_event.py`, `fsm.py` (`ALAN_GATES`), testes, `.cursor/rules/harness.mdc`, skill `alan-workflow` (lista de gates).
- Consome `scripts/release-guard post` (medida) e `scripts/post-card-evidence-comment.sh --transition pronto`.
- Não toca `backend/`, `frontend/src/`, PROD systemd, nem o pipeline de archive/PR/deploy (continua o overlay no pedido `suba a release`).
- Job CI `process-fsm`. `UI impact: none`. Prototype N/A.
- Origem: #652 (lote 2026-08-21 F-closeout) + pedido Alan de Agent fechar Pronto após publicação.
