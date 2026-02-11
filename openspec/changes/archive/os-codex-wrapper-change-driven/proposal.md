## Why

Hoje o fluxo OS+Codex usa o wrapper `./scripts/openspec_codex_task.sh`, mas ele ainda opera de forma “spec-first” (pede um id e roda `openspec validate <id>` + Codex), sem consumir as **tasks** do workflow oficial de **Change Proposal**.

Isso abre margem para drift: o que foi planejado em `openspec/changes/<id>/tasks.md` não necessariamente guia a implementação.

## What Changes

- Atualizar o wrapper `./scripts/openspec_codex_task.sh` para operar em cima de **change_id** e exigir a presença de `openspec/changes/<change_id>/tasks.md`.
- Fazer o wrapper buscar e validar instruções/tarefas via `openspec instructions apply --change <change_id> --json`.
- Se não houver tasks (ou estado `blocked`), o wrapper deve falhar com mensagem acionável.
- Injetar no prompt do Codex as tasks (e/ou instruções enriquecidas) como “source of truth” do que deve ser implementado.

## Capabilities

### New Capabilities
- `os-codex-wrapper-change-driven`: Wrapper OS+Codex passa a ser change-driven (usa tasks do change como plano obrigatório).

### Modified Capabilities
- (nenhuma)

## Impact

- Script: `scripts/openspec_codex_task.sh`
- Documentação: `docs/os_codex_workflow.md` (atualizar para refletir o comportamento do wrapper)
- Experiência de uso: requer que changes tenham tasks antes de executar o apply.
