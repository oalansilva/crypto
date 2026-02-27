## ADDED Requirements

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
