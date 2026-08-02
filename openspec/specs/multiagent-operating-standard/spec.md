# multiagent-operating-standard Specification

## Purpose
TBD - created by archiving change standardize-multiagent-kadro-operating-model. Update Purpose after archive.
## Requirements
### Requirement: The operating model MUST preserve the current Kadro and persistent role agents
The project MUST preserve the current Kadro/Kanban flow and the persistent role agents `main`, `PO`, `DESIGN`, `DEV`, and `QA` while standardizing operation.

#### Scenario: Preserve the current operating structure
- **WHEN** this change is implemented
- **THEN** the current Kanban stage flow and persistent role agents MUST remain in place
- **AND** the change MUST improve operation without replacing that structure

### Requirement: The operating model MUST define explicit responsibilities for the current role agents
The operating model MUST explicitly define the responsibilities and completion expectations for the current persistent role agents.

#### Scenario: Role responsibilities are explicit
- **WHEN** a role participates in a stage transition
- **THEN** its operational responsibilities MUST be documented
- **AND** its completion expectations MUST be explicit

### Requirement: A stage MUST NOT count as complete without runtime state and handoff update
A stage MUST only count as complete when both the runtime/Kanban state and the operational handoff/comment have been updated.

#### Scenario: Validate a stage transition
- **WHEN** PO, DESIGN, DEV, or QA claims a stage is complete
- **THEN** the stage MUST NOT count as complete unless runtime reflects the transition
- **AND** the relevant handoff/comment has been published

### Requirement: Legacy coordination markdown MUST be treated as mirror/audit only
`docs/coordination/*.md` MUST be treated as mirror/audit support rather than the active operational source.

#### Scenario: Runtime differs from legacy coordination
- **WHEN** runtime/Kanban and legacy coordination differ
- **THEN** runtime/Kanban MUST remain the authoritative operational source
- **AND** legacy coordination MUST be treated as a mirror to reconcile, not the deciding execution surface

### Requirement: Persistent workflow stages MUST use fixed Codex execution profiles after activation
After the routing profiles are versioned and loaded, the operating model MUST bind development, Code Review, QA, and release to the exact project-scoped profiles defined by the stage-model-routing contract while preserving the current Kanban sequence and human gates. The bootstrap change itself follows the static-acceptance exception defined by `stage-model-routing`.

#### Scenario: Stage responsibility is resolved
- **WHEN** the orchestrator reads the card's current Status or begins an authorized release
- **THEN** it selects the one exact executor assigned to that stage and records safe agent type, model, effort, sandbox, and permission-profile evidence in the handoff

#### Scenario: Generic subagent could perform the work
- **WHEN** a built-in or differently configured agent is available but the required project-scoped profile is not
- **THEN** the stage remains blocked because generic availability is not a valid substitute

### Requirement: The primary session MUST retain orchestration ownership
The Sol High primary session MUST retain ownership of user intent, card status, OpenSpec coherence, delegation, evidence consolidation, QA acceptance, and final reporting even while Luna profiles execute bounded stages.

#### Scenario: Luna reports stage completion
- **WHEN** a Luna implementer, reviewer, or release manager returns a report
- **THEN** the primary session treats the report as a claim and verifies the actual diff, state, and required evidence before advancing the card
