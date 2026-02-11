---
id: os-codex-wrapper-change-driven
name: "OS+Codex wrapper: change-driven apply"
status: draft
owner: Alan
created_at: 2026-02-09
updated_at: 2026-02-09
---

## Purpose
Tornar o wrapper `scripts/openspec_codex_task.sh` compatível com o workflow oficial de Change Proposal do OpenSpec, usando `change_id` e as tasks do change como fonte de verdade.

## Requirements

## ADDED Requirements

### Requirement: Wrapper MUST operar em cima de change_id
O wrapper MUST receber um `change_id` e validar que existe um diretório `openspec/changes/<change_id>/`.

#### Scenario: Change não existe
- **WHEN** o usuário executa `./scripts/openspec_codex_task.sh <change_id>` com um id inexistente
- **THEN** o wrapper falha
- **AND** imprime uma mensagem acionável indicando `openspec new change <change_id>`

### Requirement: Wrapper MUST consumir tasks via openspec instructions apply
O wrapper MUST executar `openspec instructions apply --change <change_id> --json`, extrair o JSON e usar:
- `instruction`
- `tasks`
como guia obrigatório para o Codex.

#### Scenario: tasks vazias (blocked)
- **WHEN** o change não possui tasks trackeáveis
- **THEN** o wrapper falha
- **AND** orienta editar `openspec/changes/<change_id>/tasks.md`

### Requirement: Wrapper MUST injetar tasks/instruction no prompt do Codex
O wrapper MUST construir o prompt do Codex incluindo:
- `change_id`
- `APPLY_INSTRUCTION` (do OpenSpec)
- lista de tasks (ou conteúdo de tasks.md)

#### Scenario: Prompt contém tarefas
- **WHEN** o wrapper inicia o Codex
- **THEN** o prompt inclui explicitamente as tasks
- **AND** ordena implementar somente o que está nas tasks
