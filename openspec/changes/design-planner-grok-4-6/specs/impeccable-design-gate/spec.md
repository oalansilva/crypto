## MODIFIED Requirements

### Requirement: Independent critics MUST inherit the primary Codex LLM
Assessment A and Assessment B MUST run in isolated read-only subagents using exactly the same LLM/model identifier and version as the designated design session: the `design-planner` session (`openai/gpt-5.6-sol`) when the Design gate runs through that subagent; otherwise the primary session.

#### Scenario: Same-model dual critique
- **WHEN** the Impeccable critique is executed with subagent support available
- **THEN** Assessment A MUST review product/UX/heuristics and Assessment B MUST review detector/browser evidence in separate contexts
- **AND** both subagents MUST report the same designated-design-session LLM/model and version before synthesis

#### Scenario: Critique inside design-planner
- **WHEN** the Design gate runs via `design-planner` (`openai/gpt-5.6-sol`)
- **THEN** Assessment A and Assessment B MUST inherit `openai/gpt-5.6-sol` from that session
- **AND** they MUST NOT fall back to the primary session model

#### Scenario: Model equality cannot be proven
- **WHEN** the orchestrator cannot enforce or observe model equality or cannot provide the required subagent contexts
- **THEN** the Design verdict MUST be `BLOCKED`
- **AND** no alternate model or silent degraded `PASS` MAY be used
