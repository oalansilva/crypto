## MODIFIED Requirements

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

### Requirement: Column derivation MUST include DESIGN
The backend derivation logic MUST include Pending as the first runtime stage before PO.

#### Scenario: Card awaiting PO planning
- **GIVEN** a card is marked as pending backlog work
- **THEN** the derived Kanban column MUST be `Pending`

#### Scenario: Card leaves pending
- **WHEN** a pending card is moved to `PO`
- **THEN** the derived Kanban column MUST stop reporting `Pending`
- **AND** the card MUST continue through the normal workflow order after PO

