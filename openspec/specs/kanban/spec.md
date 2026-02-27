# kanban Specification

## Purpose
TBD - created by archiving change kanban-visual-coordination. Update Purpose after archive.
## Requirements
### Requirement: System MUST provide a Kanban board for active + archived changes
The system MUST provide a Kanban UI page that lists **active** OpenSpec changes and **archived** changes and shows them in workflow columns:
- PO
- Alan approval
- DEV
- QA
- Alan homologation
- Archived

#### Scenario: Active changes appear
- **WHEN** there are active changes under `openspec/changes/*` containing `.openspec.yaml` (excluding `archive/`)
- **THEN** the Kanban MUST display one card per active change

#### Scenario: Archived changes appear
- **WHEN** there are archived changes under `openspec/changes/archive/*` containing `.openspec.yaml`
- **THEN** the Kanban MUST display one card per archived change in the Archived column

### Requirement: Kanban MUST derive status from coordination files
The system MUST derive each card's workflow state from `docs/coordination/<change>.md`.

#### Scenario: Missing coordination file
- **WHEN** `docs/coordination/<change>.md` does not exist
- **THEN** the system MUST automatically create `docs/coordination/<change>.md` using the coordination template
- **AND THEN** the Kanban MUST display the card with the newly created coordination state

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
The Kanban board MUST include a DESIGN column between PO and Alan approval.

#### Scenario: Column ordering
- **WHEN** the user opens `/kanban`
- **THEN** the columns MUST be ordered:
  1) PO
  2) DESIGN
  3) Alan approval
  4) DEV
  5) QA
  6) Alan homologation
  7) Archived

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
The backend derivation logic MUST include DESIGN in the gate order.

#### Scenario: Change awaiting design
- **GIVEN** `PO: done`
- **AND** `DESIGN != done` and `DESIGN != skipped`
- **THEN** the derived column MUST be `DESIGN`

#### Scenario: Change after design
- **GIVEN** `PO: done`
- **AND** `DESIGN: done` (or `skipped`)
- **AND** `Alan approval != approved`
- **THEN** the derived column MUST be `Alan approval`

