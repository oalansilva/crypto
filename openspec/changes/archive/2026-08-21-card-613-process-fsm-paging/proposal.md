## Why

`AGENTS.md` (~670 linhas) e a skill com prioridade “chat > coluna” entram always-on. Lost in the Middle: o Auto escolhe o atalho útil (`implemente` em Todo, playbook de release fora de Homologado). O lote 1/2 já compilou δ e o Guard; falta paginar só o frame `context_file[q]` no `sessionStart`.

## What Changes

- Hook Cursor `sessionStart` injeta **somente** a página Moore: tupla `(q, bound_card, q_git)` + stub `context_file[q]` do yaml #609. Sem playbook de release, sem 12 colunas, sem Drive.
- Encolher `.cursor/rules/harness.mdc` para 8–15 linhas de corpo: resolver a tupla; chat ≠ autorização; NLU ≠ δ; Todo ≠ código.
- Inverter prioridade em `.cursor/skills/alan-workflow/SKILL.md`: **δ e Guard > overlay > skill > wording**.
- `AGENTS.md` deixa de ser always-on. Cursor auto-injeta o `AGENTS.md` da raiz: o apply **encolhe** esse arquivo a um stub e move o overlay (portas, Drive, PostgreSQL, release-guard) para um path que o Cursor **não** auto-injeta; o agente `Read` on-demand.
- Testes de paging com status/provider injetados; **sem GitHub** no pytest. Aceite: página de `q=Todo` não contém o playbook de release.
- Não alterar código de produto. Não reabrir Guard Write (#611) nem `process_event` (#612), salvo reusar `resolve` + `github_status_provider`. Paging sozinho não substitui o lote 1.

## Capabilities

### New Capabilities

- `process-fsm-paging`: `sessionStart` resolve `(q, bound_card, q_git)` e emite `additional_context` = página `context_file[q]` (ou stub unbound); testes assertam ausência do playbook de release em Todo.

### Modified Capabilities

- `cursor-harness`: always-on ≤ harness curto + página do `sessionStart`; `AGENTS.md` da raiz não carrega o overlay longo; `hooks.json` registra `sessionStart`; skill com prioridade invertida.

## Impact

- Novos paths: `scripts/process-fsm/paging.py` + `test_paging.py`; adapter `.cursor/hooks/process-fsm-session-start.sh`.
- Altera `.cursor/hooks.json` (`sessionStart`), `.cursor/rules/harness.mdc`, `.cursor/skills/alan-workflow/SKILL.md`, `AGENTS.md` (stub) + arquivo de overlay on-demand.
- Consome yaml `context_file` (#609), resolver (#610), `github_status_provider` pontual (#611). Job CI `process-fsm` cobre os testes novos.
- Sem API, banco, UI de produto. `UI impact: none`. Prototype N/A.
- Lote 3 P2. Homologação: sessão em Todo não carrega playbook de release.
