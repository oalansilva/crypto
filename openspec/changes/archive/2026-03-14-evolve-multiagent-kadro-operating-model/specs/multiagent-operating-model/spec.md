## ADDED Requirements

### Requirement: The operating model MUST preserve the current Kadro and persistent role agents
The system and process changes for this initiative MUST preserve the current operational structure built around the existing Kadro/Kanban flow and the persistent role agents `main`, `PO`, `DESIGN`, `DEV`, and `QA`.

#### Scenario: Preserve the current operating structure
- **WHEN** this change is implemented
- **THEN** the project MUST continue to use the current Kanban stage flow and the existing persistent role agents
- **AND** the change MUST improve operation without requiring a replacement of the current structure

### Requirement: Phase 1 MUST standardize the role contract and stage handoffs
Phase 1 of this change MUST define explicit role responsibilities, a standard handoff contract, and Definition of Done rules for each stage.

#### Scenario: Stage completion requires explicit contract
- **WHEN** an agent claims a stage is complete
- **THEN** the project MUST have a documented responsibility model for that role
- **AND** a standard handoff/comment contract MUST exist for that stage
- **AND** a stage-specific Definition of Done MUST exist

### Requirement: A stage MUST NOT be considered complete without runtime state and handoff update
The operating model MUST require both runtime/Kanban state update and handoff/comment publication before a stage is considered complete.

#### Scenario: Stage completion validation
- **WHEN** PO, DESIGN, DEV, or QA finishes a stage
- **THEN** the stage MUST NOT count as complete unless runtime state reflects the transition
- **AND** the relevant handoff/comment has been published in the operational surface

### Requirement: Legacy coordination markdown MUST be treated as mirror/audit only
The operating model MUST treat `docs/coordination/*.md` as mirror/audit artifacts instead of the primary active operational surface.

#### Scenario: Runtime and legacy coordination differ
- **WHEN** runtime/Kanban and legacy coordination differ
- **THEN** the runtime/Kanban state MUST be treated as authoritative for active operation
- **AND** legacy coordination MUST be reconciled as a mirror rather than used as the deciding execution surface

### Requirement: Phase 2 MUST improve execution discipline without replacing the current stage model
Phase 2 of this change MUST improve instruction alignment, work-item discipline, and closure consistency while preserving the current stage model.

#### Scenario: Harden execution on top of the current flow
- **WHEN** Phase 2 is implemented
- **THEN** the project MUST retain the existing stage flow
- **AND** it MUST improve disciplined use of work-item types, ownership, locks, dependencies, and closure behavior
- **AND** it MUST reduce manual reconciliation overhead compared with the pre-change operating model
