## Why

`Write`/`StrReplace` de produto estão sempre ligados. A sessão `b6a71170` alterou `backend/` com `q_git=develop` porque o Auto não consulta a EFSM. O yaml (#609) e o resolver (#610) já estão em `develop`; falta o Guard que **compila** a tabela e deny antes do side-effect. Absorve o hook do #606 Cancelado: não é um `if` avulso.

## What Changes

- Registrar `preToolUse` (Write/StrReplace/Delete/EditNotebook) em `.cursor/hooks.json` apontando para um script que classifica glob **antes** de `evaluate(write_produto)` (yaml + resolver). OpenSpec/protótipo em Design não passa por `write_produto`.
- Ligar `beforeShellExecution` **somente** para o mesmo deny cobrir writes via shell (redirect/`tee`/`sed -i` em `product_globs`); não vira gate de `git commit`/`process_event` (#612).
- Compôr com o Impeccable já em `afterFileEdit`/`stop` — **não** substituir `.cursor/hooks/impeccable.sh`.
- Fail-closed assimétrico: deny produto se Status ilegível; allow `design_globs` se a branch do path já é `card-<id>-*` (Design não morre com `gh` down).
- I3: em `Pronto para Dev`, Write produto = deny até o Status **já ser** Em desenvolvimento.
- Fixtures no envelope Cursor (`tool_name`/`tool_input`/`cwd` ou `command`/`cwd`) sem GitHub; matriz do filho A só depois do glob-first. Write OpenSpec em Design = allow. Replay `b6a71170` = deny.
- Não alterar código de produto (`backend/`, `frontend/src/` além do glob que o Guard observa). Não `process_event` (#612). Não paging `sessionStart` (#613).

## Capabilities

### New Capabilities

- `process-fsm-guard`: runtime Cursor que compila a EFSM + resolver e deny/allow Write de produto antes do side-effect.

### Modified Capabilities

- `cursor-harness`: `.cursor/hooks.json` passa a registrar o Guard Write **além** do Impeccable (composição, não substituição).

## Impact

- Novos paths: `.cursor/hooks/process-fsm-guard.sh` (adapter) + `scripts/process-fsm/guard.py` (+ `test_guard.py`).
- Altera `.cursor/hooks.json` (acrescenta `preToolUse` / `beforeShellExecution`; preserva Impeccable).
- Consome yaml #609 e resolver #610 já em `develop` (`d9dd3706`). Job CI `process-fsm` existente cobre os novos testes.
- Sem API, banco, UI de produto.
- `UI impact: none`. Prototype N/A.
- Fecha o lote 1 P0 (#609 → #610 → #611). Desbloqueia #612 (T8 duas fases precisa deste Guard).
