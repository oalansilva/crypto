---
id: os-codex-wrapper-include-change-context
name: "OS+Codex wrapper: include full change context"
status: draft
owner: Alan
created_at: 2026-02-09
updated_at: 2026-02-09
---

## Purpose
Garantir que o Codex implemente tarefas seguindo o contrato do Change Proposal, sempre recebendo no prompt o contexto completo (proposal/design/specs/tasks).

## Requirements

## ADDED Requirements

### Requirement: Wrapper MUST include proposal/design/specs/tasks in Codex prompt
O wrapper MUST incluir no prompt do Codex, para o `change_id` informado:
- `proposal.md`
- `design.md`
- todos os arquivos `specs/**/*.md`
- `tasks.md`

#### Scenario: Change com múltiplas specs
- **WHEN** um change contém vários arquivos em `specs/**/*.md`
- **THEN** o wrapper inclui todos esses arquivos no prompt do Codex

### Requirement: Wrapper MUST cap file size to avoid runaway prompts
O wrapper MUST aplicar um limite por arquivo ao anexar conteúdo no prompt (ex.: 12k chars), preservando o início do arquivo.

#### Scenario: Spec grande
- **WHEN** algum arquivo excede o limite
- **THEN** o wrapper inclui apenas o início do conteúdo e uma nota indicando truncamento
