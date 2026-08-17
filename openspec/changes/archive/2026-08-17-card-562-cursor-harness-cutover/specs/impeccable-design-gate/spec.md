## MODIFIED Requirements

### Requirement: Impeccable installation is project-local and harness-agnostic
The project MUST provide a versioned project-local Impeccable installation under `.agents/skills/impeccable/` plus a Cursor hook adapter in `.cursor/hooks.json` that invokes the canonical detector script.

#### Scenario: Fresh checkout loads the detector
- **WHEN** a Cursor Agent session edits UI files
- **THEN** `.agents/skills/impeccable/` MUST be available from the repository
- **AND** `.cursor/hooks.json` MUST invoke `.agents/skills/impeccable/scripts/hook.mjs`
- **AND** the flow MUST NOT require `.codex/hooks.json` or `.opencode/plugin/impeccable-hook.ts`

### Requirement: Independent critics MUST inherit the chat model
Assessment A and Assessment B MUST run in isolated Tasks using the same LLM/model as the Cursor chat session (`inherit`).

#### Scenario: Same-model dual critique
- **WHEN** the Impeccable critique is executed with Task support available
- **THEN** Assessment A and Assessment B MUST run in separate Tasks instructed not to edit files
- **AND** both MUST inherit the chat-selected model

#### Scenario: Model equality cannot be proven
- **WHEN** the orchestrator cannot spawn an isolated critique Task
- **THEN** the Design verdict MUST be `BLOCKED`
- **AND** no silent degraded `PASS` MAY be used

#### Scenario: Sol is not required
- **WHEN** Design runs in Cursor
- **THEN** critics MUST NOT require `openai/gpt-5.6-sol` or `design-planner`
- **AND** they MUST inherit the chat model
