## Why

QA verde (unit, `openspec validate`, até filho QA com `qa-gate` SUCCESS) não fecha Done: T11 (`aceitar_sha`) entra em QA sem PR `q_git`→develop; `integrar_develop` devolve `guard:checks_green` / `I8` sem causa; `sync_dev_source` aborta se o source canónico estiver sujo e o pai trata o primeiro reject como fim de turno. Evidência 2026-08-29 (#792 sem PR; #798 com PR+qa-gate verde e canónico dirty) — ambos já Pronto; este card não os reabre.

## What Changes

- T11 (`aceitar_sha`): sem PR `q_git` contra develop, **rejeita** `no_pr` e o Status permanece Code Review. Não cria PR. O cliente abre o PR no mesmo turno e volta a chamar `aceitar_sha`. **Q1=A.**
- Reject de `integrar_develop` com causa estruturada no payload (`reason`, não só `guard:checks_green` / `I8` mudo): `no_pr` | `qa-gate pending` | `qa-gate failed` | `sync: dirty` (path + porcelain em `message`). Sem flag `--checks-green` na CLI.
- Depois de `qa-gate pending`: o pai (ou script no mesmo turno) espera o check e repete `integrar_develop`. Filho QA continua sem `process_event` / T14. `process_event` em si é one-shot (não faz poll).
- Guard: deny `git checkout -b card-*` (e equivalente `git switch -c card-*`) em `environments.dev.source`. Cards só em worktree `card-<id>-*`.
- T14 `sync_dev_source`: dirty⇒I8 permanece (#632). O reject devolve `sync: dirty` + path do canónico + porcelain. Sem throwaway, sem checkout/merge/reset em árvore suja. **Q2=A.**
- Moore/`context_file[QA]`: pai fecha T14 no mesmo turno em que o filho devolver verde; primeiro reject não é fim de turno.
- dsh: o cliente não spawna filho QA; o mesmo turno abre PR **antes** de T11, espera qa-gate, chama T14 (plugin/moore, não só skill).
- Spec viva `process-fsm-event` deixa o leftover «T14 stays reject live» (#612) e alinha com o archive #632 + causas visíveis. **Não** reabre #632 nem #729.
- `reviewers_ok` continua EVENT_GUARDS pelo nome do evento. Medir de verdade é card irmão. **Q3=A.**

## Capabilities

### New Capabilities

- (nenhuma) — T11/T14, Guard e Moore já existem; este card fecha o closeout e torna as causas visíveis.

### Modified Capabilities

- `process-fsm-event`: T11 rejeita `no_pr` sem criar PR; live T14 classifica causas (`no_pr` | `qa-gate pending` | `qa-gate failed` | `sync: dirty`) no payload; leftover «T14 stays reject live» sai da spec viva (drift #612, sem reabrir #632).
- `process-fsm`: `context_file[QA]` manda o pai chamar T14 no mesmo turno do verde e não tratar o primeiro reject como fim; I8 permanece (dirty/falha ⇒ QA).
- `process-fsm-guard`: deny `git checkout -b card-*` / `git switch -c card-*` no source canónico (`environments.dev.source`).
- `cursor-harness`: T11 exige PR; pai Cursor chama T14 no mesmo turno do filho QA verde; pending ⇒ espera e repete.
- `covenant-flow`: runbook QA/dsh — Cursor: filho QA lê checks, pai T14; dsh: sem filho QA, PR antes de T11 + wait qa-gate + T14 no mesmo turno.
- `process-harness`: closeout dsh chega via Moore (`context_file[QA]`) + plugin que já injeta a página; não dual-write da lei.

## Impact

- Altera `scripts/process-fsm/process_event.py`, `t14.py`, `guard.py` e testes focados (`test_process_event.py`, `test_t14.py`, `test_guard.py`; paging se o stub QA for needle).
- Altera `.cursor/process-fsm.yaml` só em `context_file[QA]` (T11/T14 yaml, Σ, I8 texto, `enabled_events` intactos).
- Altera `.cursor/skills/covenant-flow/SKILL.md` (closeout QA/dsh). Stubs Grok/dsh permanecem thin.
- Guard bash fallback (`.cursor/hooks/process-fsm-guard.sh`) MUST deny o mesmo `checkout -b card-*` no canónico se o Python falhar.
- Não toca `backend/` / `frontend/src/`, `--checks-green`, T7/T15, `item-edit` de Status, #632/#729, medição real de `reviewers_ok`.
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A.
- Origem: issue [#801](https://github.com/oalansilva/crypto/issues/801). Q1=A, Q2=A, Q3=A congeladas.
