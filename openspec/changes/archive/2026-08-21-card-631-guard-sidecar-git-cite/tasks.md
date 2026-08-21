# Tasks: card-631-guard-sidecar-git-cite

## 1. Classificação path-aware do sidecar

- [x] 1.1 Em `scripts/process-fsm/board_status.py`, substituir `sidecar_in_command` por detecção de **mutação** do sidecar
- [x] 1.2 Em `scripts/process-fsm/guard.py`, usar a nova classificação (alias `sidecar_in_command` → mutation)
- [x] 1.3 Em `.cursor/hooks/process-fsm-guard.sh`, remover deny por substring; espelhar mutação via `board_status`

## 2. Fixtures e pytest

- [x] 2.1 Fixtures falso positivo: `git add` / `commit` / `status` / `reset` que citam o sidecar → allow
- [x] 2.2 True deny: Write tools + `python -c` open-write + redirect `>` no sidecar
- [x] 2.3 `pytest scripts/process-fsm -q` → 151 passed

## 3. Verificação de contrato

- [x] 3.1 Status item-edit e product-write denies existentes não regressam (suite verde)
- [x] 3.2 `UI impact: none` — nenhum ficheiro frontend/produto de UI tocado
