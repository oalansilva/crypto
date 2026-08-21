## Why

O Guard nega qualquer Shell cujo `command` contenha a substring `.design-digest` (`sidecar_in_command`). Isso bloqueia `git add`/`git commit`/`git status`/`git reset` que só citam o sidecar (arquivo no archive, mensagem de commit, path no index) sem mutar o ficheiro. O deny deve cobrir escrita real do sidecar, não citação.

## What Changes

- Substituir o deny por substring em Shell por detecção path-aware de **mutação** do sidecar `.design-digest`.
- Manter deny de `Write` / `StrReplace` / `Delete` (e path extraído que termina em `.design-digest`).
- Negar Shell que de facto escreve/apaga o sidecar (`python -c open(...,'w')`, redirect/`tee`, `rm`, `cp`/`mv` destino sidecar, `sed -i`/`perl -i`).
- Permitir `git add` / `git commit` / `git status` / `git reset` (e leituras) que apenas mencionam o nome.
- Alinhar o fallback bash em `.cursor/hooks/process-fsm-guard.sh`.
- Fixtures `beforeShellExecution`: falso positivo (git cite) + true deny (mutação); `pytest scripts/process-fsm` verde.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `process-fsm-guard`: requisito de sidecar deixa de ser “qualquer command com `.design-digest`” e passa a “Write tools no path do sidecar **ou** Shell classificado como mutação do sidecar”; citação em git/read-only MUST NOT deny.

## Impact

- `scripts/process-fsm/board_status.py` (`sidecar_in_command` → classificação de mutação)
- `scripts/process-fsm/guard.py` (`decide` / `_sidecar_deny`)
- `.cursor/hooks/process-fsm-guard.sh` (fallback substring)
- `scripts/process-fsm/test_*.py` (fixtures allow/deny)
- Sem UI; sem board; sem alteração de `process_event` T5 (único escritor legítimo do sidecar)
