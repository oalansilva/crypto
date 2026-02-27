## ADDED Requirements

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
