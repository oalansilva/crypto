## 1. Guard core

- [x] 1.1 Implementar `scripts/process-fsm/guard.py`: envelope Cursor stdin → path → `resolve` → classificar glob → só então `evaluate(write_produto)` se `product_globs` → `{permission, agent_message}`
- [x] 1.2 Glob-first: `product_globs` usa I1/I3; `design_globs` (OpenSpec/protótipo) em Design ⇒ allow **sem** `evaluate(write_produto)`; resto ⇒ allow
- [x] 1.3 I3: Pronto para Dev ⇒ deny produto
- [x] 1.4 Fail-closed assimétrico: `q` ilegível ⇒ deny produto; allow design_globs se `q_git` é `card-<id>-*`
- [x] 1.5 `status` injetado no JSON; `status_provider` live injetável e ausente dos unitários (sem GitHub no pytest)

## 2. Cursor hooks

- [x] 2.1 Adapter `.cursor/hooks/process-fsm-guard.sh` (stdin → python do repo/`python3` → JSON Cursor); se Python/PyYAML falhar, fallback bash assimétrico (deny produto / allow design em `card-<id>-*`)
- [x] 2.2 Registrar `preToolUse` matcher `Write|StrReplace|Delete|EditNotebook` com `failClosed: true`; preservar Impeccable em `afterFileEdit`/`stop`
- [x] 2.3 Registrar `beforeShellExecution` no mesmo adapter: mutation token + product path ⇒ mesmo deny; pytest/ruff/git status ⇒ allow

## 3. Testes

- [x] 3.1 `test_guard.py`: fixtures no envelope Cursor (`tool_name`+`tool_input`+`cwd` ou `command`+`cwd`); deny produto nas colunas + develop/main/unbound; allow Em desenvolvimento e Code Review com binding; Write OpenSpec em Design ⇒ allow
- [x] 3.2 Replay `b6a71170` (Write `backend/app/tasks/discovery_tasks.py`, `q_git=develop`) ⇒ deny
- [x] 3.3 Fail-closed produto vs design; shell redirect deny vs `pytest backend/` allow
- [x] 3.4 `pytest scripts/process-fsm -q` verde (job CI existente)

## 4. Fora de escopo

- [x] 4.1 Diff NÃO altera `backend/` nem `frontend/src/`
- [x] 4.2 Diff NÃO substitui `.cursor/hooks/impeccable.sh`
- [x] 4.3 Sem `process_event`, sem paging `sessionStart`, sem gate de `git commit`/`./restart`
