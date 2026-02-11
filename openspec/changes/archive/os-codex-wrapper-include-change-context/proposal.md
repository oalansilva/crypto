## Why

O wrapper OS+Codex já é change-driven e injeta `tasks.md` + `openspec instructions apply`. Porém, para reduzir drift e garantir que o Codex siga o contrato do change, precisamos incluir sempre no prompt o contexto completo do change: `proposal.md`, `design.md` e `specs/**/*.md`.

## What Changes

- Atualizar `scripts/openspec_codex_task.sh` para incluir no prompt do Codex:
  - `proposal.md`
  - `design.md`
  - todos os arquivos em `specs/**/*.md`
  - `tasks.md`
- Usar os paths fornecidos por `openspec instructions apply --change <id> --json` (`contextFiles`) como fonte de verdade.
- Adotar um limite de tamanho por arquivo (truncate) para evitar prompts gigantes, preservando o início do arquivo.

## Capabilities

### New Capabilities
- `os-codex-wrapper-include-change-context`: Wrapper sempre injeta contexto completo do change no prompt.

### Modified Capabilities
- (nenhuma)

## Impact

- Script: `scripts/openspec_codex_task.sh`
- Docs: `docs/os_codex_workflow.md`
