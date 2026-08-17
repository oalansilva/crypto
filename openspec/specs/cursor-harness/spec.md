# cursor-harness Specification

## Purpose
Contrato do cliente de desenvolvimento ativo do Cripto Farol: Cursor Agent, com o modelo selecionado no chat em todos os papéis.

## Requirements
### Requirement: Cursor is the versioned development harness
The repository SHALL contain versioned Cursor Agent configuration under `.cursor/` (rules, skills, commands, hooks) and MUST NOT keep OpenCode (`opencode.json`, `.opencode/`) as an active contract.

#### Scenario: Fresh checkout loads Cursor config
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** project rules, OpenSpec skills/commands and the Impeccable hook are available from `.cursor/`
- **AND** no active instruction requires `.opencode/` or `opencode.json`

#### Scenario: No secrets in versioned harness files
- **WHEN** `.cursor/` is inspected
- **THEN** no token, key or credential is present in versioned files

### Requirement: OpenSpec flow is available in Cursor
Cursor SHALL load OpenSpec skills and `/opsx-*` commands that invoke the same `openspec` CLI used by the project.

#### Scenario: OPSX commands available
- **WHEN** the user invokes `/opsx-new`, `/opsx-ff`, `/opsx-apply`, `/opsx-verify` or `/opsx-archive`
- **THEN** the corresponding Cursor command runs the OpenSpec CLI flow
- **AND** it MUST NOT invent artifacts outside `openspec instructions`

### Requirement: Chat-selected model runs every role
The Cursor chat model SHALL be the source of truth for Design, implementation, review and vision. Subagents MUST inherit that model unless Alan explicitly selects another model in the chat or Task.

#### Scenario: Default inheritance
- **WHEN** the session spawns a Task for critique or review
- **THEN** the child uses `inherit` (same chat model)
- **AND** it MUST NOT require `openai/gpt-5.6-sol` or `opencode-go/*` models

### Requirement: Design gate is process-based
While `Status=Design`, the Cursor session SHALL author OpenSpec artifacts and a navigable prototype when UI-impacting, then spawn an isolated same-model critique Task. The agent MUST NOT implement product code until `Status=Pronto para Dev`.

#### Scenario: Isolated critique
- **WHEN** Design evidence is ready
- **THEN** Assessment uses a separate Task instructed not to edit files
- **AND** missing critique keeps the verdict `BLOCKED`

#### Scenario: No OpenCode lock machine
- **WHEN** Design runs in Cursor
- **THEN** the flow MUST NOT require `design_spawn_stage`, `design_artifact_write`, lease evidence or OpenCode 1.18.18 attestation
