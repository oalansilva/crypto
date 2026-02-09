## 1. Prompt com contexto completo

- [ ] 1.1 Atualizar `scripts/openspec_codex_task.sh` para anexar proposal/design/specs/tasks ao prompt do Codex usando `contextFiles` do apply JSON.
- [ ] 1.2 Implementar limite por arquivo (truncate) com indicação no prompt.

## 2. Docs e verificação

- [ ] 2.1 Atualizar `docs/os_codex_workflow.md` descrevendo que o wrapper injeta proposal/design/specs/tasks.
- [ ] 2.2 Validar change via `openspec validate os-codex-wrapper-include-change-context`.
- [ ] 2.3 Rodar `./backend/.venv/bin/python -m pytest -q`.
