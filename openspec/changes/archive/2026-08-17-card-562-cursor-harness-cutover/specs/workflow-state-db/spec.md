## MODIFIED Requirements

### Requirement: One harness MUST consume the workflow contract
Repository instructions MUST define a single harness (Cursor Agent) for OpenSpec stages, design gate, status names and evidence requirements.

#### Scenario: Cursor starts a UI change
- **WHEN** Cursor follows `/opsx-*` command adapters for a UI-impact card
- **THEN** it MUST prepare and publish design evidence before implementation
- **AND** it MUST wait for `Pronto para Dev` before applying product code tasks

#### Scenario: No parallel official harness
- **WHEN** an agent reads `AGENTS.md` / `rules.md`
- **THEN** OpenCode, Codex and dual-harness routing MUST NOT be described as active
- **AND** the workflow definition MUST NOT diverge between clients
