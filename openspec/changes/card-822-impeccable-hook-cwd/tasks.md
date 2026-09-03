Ponto de partida Apply (após Pronto para Dev): rascunho **não** commitado na worktree canónica `develop` (HEAD `9f2bfe97`, 7 ficheiros `M`). Copiar esses deltas **para esta worktree** (`card-822-impeccable-hook-cwd`, hoje limpa em `origin/develop`); **não** commitá-los na `develop` daqui. Ficheiros do rascunho: `.grok/hooks/process-fsm.json`, `.cursor/hooks.json`, `.dsh/plugin/impeccable-hook.js`, `scripts/process-fsm/dsh_plugin_lib.js`, `scripts/process-fsm/test_guard.py`, `test_paging.py`, `test_dsh_adapter.py`. OpenCode **não** está no rascunho — tasks 4.x. Skills: `.cursor/skills/openspec-apply-change`, `covenant-flow`. Zero produto UI. Sem `process_event` neste ficheiro.

## 1. Copiar rascunho (7 ficheiros) para a worktree do card

- [x] 1.1 Ler o diff em `/srv/apps/dev/criptofarol/source` (canónica `develop` suja) e aplicar o **mesmo** delta na worktree `card-822-impeccable-hook-cwd` nos 7 paths listados acima. MUST NOT `git commit` na canónica. MUST NOT deixar a canónica como único sítio do patch
- [x] 1.2 Confirmar que esta worktree **não** recebe `backend/` / `frontend/src/` / `hook.mjs` / `guard.py` / `.dsh/plugin/process-fsm-guard.js` / Guard Cursor nesse copy

## 2. Grok: locator nos quatro eventos

- [x] 2.1 `.grok/hooks/process-fsm.json`: `PostToolUse` e `Stop` usam a cadeia D1 (`test -f .grok/hooks/impeccable.sh` → `./impeccable.sh` → `git rev-parse --show-toplevel` + `.grok/hooks/impeccable.sh`; `exec`; último `exit 127`)
- [x] 2.2 Mesma cadeia em `PreToolUse` (`process-fsm-guard.sh`) e `SessionStart` (`process-fsm-session-start.sh`). Timeout ≥ 30 inalterado. Sem tabela T0–T17 no JSON
- [x] 2.3 **Não** alterar o corpo de `.grok/hooks/impeccable.sh` / `process-fsm-guard.sh` / `process-fsm-session-start.sh` salvo se o locator exigir (não deve: `ROOT` já é `dirname`)

## 3. Cursor: locator só Impeccable

- [x] 3.1 `.cursor/hooks.json`: `afterFileEdit` e `stop` usam a cadeia D2 (`.cursor/hooks/impeccable.sh` → `./hooks/impeccable.sh` → `./impeccable.sh` → git toplevel)
- [x] 3.2 `preToolUse` permanece `.cursor/hooks/process-fsm-guard.sh` com `failClosed: true`; `beforeShellExecution` o mesmo script sem `failClosed` true; `sessionStart` permanece `.cursor/hooks/process-fsm-session-start.sh`

## 4. dsh Impeccable: `resolveRepoCwd`

- [x] 4.1 `scripts/process-fsm/dsh_plugin_lib.js`: exportar `resolveRepoCwd(cwd)` = `git -C start rev-parse --show-toplevel` ou `REPO_ROOT` (D3)
- [x] 4.2 `.dsh/plugin/impeccable-hook.js`: `const cwd = resolveRepoCwd(process.cwd())`; MUST NOT `process.cwd() || REPO_ROOT`. Fail-open (`next()` / sem throw) intacto. **Não** editar `.dsh/plugin/process-fsm-guard.js`

## 5. OpenCode: endurecer directory (ausente do rascunho)

- [x] 5.1 `scripts/process-fsm/opencode_plugin_lib.js`: exportar o mesmo contrato que `resolveRepoCwd` (espelho; MUST NOT `import` de `dsh_plugin_lib.js`)
- [x] 5.2 `.opencode/plugin/impeccable-hook.js`: cwd do detector = resolve(`input.directory || input.worktree`) → git toplevel ou `REPO_ROOT`; `$HOME` não vira cwd de `runHookMjs`. Fail-open intacto
- [x] 5.3 **Não** alterar `.opencode/plugin/process-fsm-guard.js` neste card (Q2 = miss `hook.mjs`, não write-block OpenCode)

## 6. Testes (C1–C12)

- [x] 6.1 `test_guard.py`: C1–C6 (`sh -c` Grok três cwd + Cursor três cwd, stdin `{}`, exit 0); C3/C4 Guard e SessionStart Grok; C10 asserts de string (`test -f`, path repo-relative, sibling, toplevel). Actualizar `test_grok_hooks_json_registers_guard` e `test_hooks_json_composes_impeccable` (deixar de exigir igualdade exacta `./impeccable.sh PostToolUse`)
- [x] 6.2 `test_paging.py`: C7 — `afterFileEdit`/`stop` contêm `.cursor/hooks/impeccable.sh`; Guard/`sessionStart` Cursor inalterados
- [x] 6.3 `test_dsh_adapter.py`: C8 — plugin contém `resolveRepoCwd`; não contém `process.cwd() || REPO_ROOT`; `resolveRepoCwd(homedir()) == REPO_ROOT` com cwd Node = `$HOME`
- [x] 6.4 `test_opencode_adapter.py`: C9 — `input.directory` = homedir → cwd de `runHookMjs` é toplevel/`REPO_ROOT`; `hook.mjs` encontrado
- [x] 6.5 C11/C12: wrappers Impeccable continuam fail-open; JSON/plugins sem T0–T17. `pytest scripts/process-fsm -q` sem GitHub. Python: `/srv/apps/dev/criptofarol/source/backend/.venv/bin/python` se a worktree não tiver venv

## 7. Verificação

- [x] 7.1 `openspec validate --change "card-822-impeccable-hook-cwd"` verde (ou equivalente do schema)
- [x] 7.2 Zero diff de produto `backend/` / `frontend/src/`; `hook.mjs` / `guard.py` / Guard dsh / Guard Cursor / `process-fsm.yaml` / `AGENTS.md` inalterados; `UI impact: none`
- [x] 7.3 Não dual-write T0–T17; não pin `covenant-flow`; não Auto; não T16
