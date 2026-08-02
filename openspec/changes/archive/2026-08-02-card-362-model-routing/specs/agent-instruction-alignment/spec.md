## ADDED Requirements

### Requirement: Agent instructions MUST declare the fixed stage-model contract
Global and project-scoped instructions MUST consistently declare Sol High for Design/OpenSpec and QA, Luna Max for development, fresh read-only Luna Max for Code Review, and Luna Max for authorized release.

#### Scenario: An agent loads workflow instructions
- **WHEN** an agent prepares or executes a card stage
- **THEN** the applicable instructions expose the exact stage executor, model, effort, permissions, entry gate, and handoff expectation

### Requirement: Generated adapters MUST remain unmodified
Model-routing policy MUST live in the Codex workflow skill, project instructions, and agent profiles rather than isolated edits to generated OpenSpec or Cursor adapters.

#### Scenario: OpenSpec command ownership changes by operation
- **WHEN** `/opsx:apply`, `/opsx:verify`, sync, or archive is routed to a stage executor
- **THEN** the canonical routing skill assigns the executor without modifying an individual generated OpenSpec skill copy

### Requirement: Automatic model routing MUST be Codex-only
The project MUST claim and validate automatic stage-model routing only in Codex. Cursor and other clients MUST remain outside the implementation and test scope of this capability.

#### Scenario: Workflow documentation names supported clients
- **WHEN** the routing contract is loaded or reported
- **THEN** it identifies Codex as the sole supported execution client and does not claim unimplemented parity elsewhere

### Requirement: Instruction drift MUST be validated automatically
The repository MUST provide a reproducible contract check for exact profile models, reasoning efforts, reviewer sandbox, stage boundaries, and fail-closed language.

#### Scenario: Workflow configuration is validated
- **WHEN** focused validation runs for the routing change or a later workflow edit
- **THEN** inconsistent TOML or missing normative stage rules fail the check before delivery
