## 1. Wrapper change-driven

- [ ] 1.1 Atualizar `scripts/openspec_codex_task.sh` para tratar o argumento como `change_id` e verificar existência de `openspec/changes/<change_id>/`.
- [ ] 1.2 Fazer o wrapper extrair e parsear JSON de `openspec instructions apply --change <change_id> --json`.
- [ ] 1.3 Falhar com mensagem acionável quando `tasks.md` não existir ou `tasks` estiver vazio (`blocked`).
- [ ] 1.4 Injetar tasks + instrução enriquecida no prompt do Codex (source of truth da implementação).

## 2. Docs e verificação

- [ ] 2.1 Atualizar `docs/os_codex_workflow.md` descrevendo o wrapper como change-driven.
- [ ] 2.2 Validar change via `openspec validate os-codex-wrapper-change-driven`.
- [ ] 2.3 Rodar `./backend/.venv/bin/python -m pytest -q`.
