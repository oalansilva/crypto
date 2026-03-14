# kanban Specification

## Purpose
TBD - created by archiving change kanban-visual-coordination. Update Purpose after archive.
## Requirements
### Requirement: System MUST provide a Kanban board for active + archived changes
The system MUST provide a Kanban UI page that lists active OpenSpec/workflow changes and archived changes in workflow columns:
- Pending
- PO
- DESIGN
- Alan approval
- DEV
- QA
- Alan homologation
- Archived

#### Scenario: Pending cards appear
- **WHEN** there are runtime changes/cards marked as pending backlog items
- **THEN** the Kanban MUST display one card per pending item in the Pending column

### Requirement: Kanban MUST derive status from workflow runtime
The system MUST derive each card's workflow state from the workflow DB/runtime state that powers Kanban.
`docs/coordination/<change>.md` MAY mirror that state for audit/readability, but it MUST NOT be the deciding live operational source.

#### Scenario: Coordination markdown is missing
- **WHEN** `docs/coordination/<change>.md` does not exist
- **THEN** the Kanban MUST still display the card from workflow runtime state
- **AND** missing coordination markdown alone MUST NOT block the runtime card state from being shown

#### Scenario: Coordination markdown disagrees with runtime
- **WHEN** workflow runtime state and `docs/coordination/<change>.md` disagree
- **THEN** the Kanban MUST display the workflow runtime state
- **AND** the coordination markdown MUST be treated as a mirror to reconcile later

### Requirement: Card details MUST show tasks checklist
The system MUST render a checklist view of `openspec/changes/<change>/tasks.md`.

#### Scenario: Tasks displayed
- **WHEN** a user opens a Kanban card
- **THEN** the UI MUST show the tasks and their checked/unchecked state

### Requirement: Comments MUST be supported per change
The system MUST support a comments thread per change.

#### Scenario: Add comment
- **WHEN** a user posts a comment on a change
- **THEN** the comment MUST be stored and shown in the thread

### Requirement: Minimal auth assumptions
The Kanban UI MUST use the existing app session model (no new public exposure requirements).

#### Scenario: Access via existing app
- **WHEN** the user navigates to `/kanban`
- **THEN** the UI MUST load using the existing app frontend and backend routing
- **AND THEN** it MUST NOT require any new public-facing exposure beyond the existing app access

### Requirement: Kanban MUST include a DESIGN column (always visible)
The Kanban board MUST include **Pending** before **PO**, and **DESIGN** between **PO** and **Alan approval**.

#### Scenario: Column ordering
- **WHEN** the user opens `/kanban`
- **THEN** the columns MUST be ordered:
  1) Pending
  2) PO
  3) DESIGN
  4) Alan approval
  5) DEV
  6) QA
  7) Alan homologation
  8) Archived

### Requirement: Coordination MUST support DESIGN status
The coordination file `docs/coordination/<change>.md` MUST support a `DESIGN:` status in `## Status`.

Allowed values:
- `not started`
- `in progress`
- `blocked`
- `done`
- `skipped`

#### Scenario: Skipped design
- **WHEN** `DESIGN: skipped`
- **THEN** the column derivation MUST treat DESIGN as completed and proceed to the next gate

### Requirement: Column derivation MUST include DESIGN
The backend derivation logic MUST include Pending as the first runtime stage before PO.

#### Scenario: Card awaiting PO planning
- **GIVEN** a card is marked as pending backlog work
- **THEN** the derived Kanban column MUST be `Pending`

#### Scenario: Card leaves pending
- **WHEN** a pending card is moved to `PO`
- **THEN** the derived Kanban column MUST stop reporting `Pending`
- **AND** the card MUST continue through the normal workflow order after PO

