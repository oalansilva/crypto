## ADDED Requirements

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
