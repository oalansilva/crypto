## ADDED Requirements

### Requirement: Kanban MUST support explicit intra-column card ordering
The system MUST let the user change the relative order of cards within the same Kanban column so the visible sequence represents pull priority.

#### Scenario: Move card upward within the same column
- **GIVEN** a column contains at least two active cards
- **WHEN** the user requests moving a card upward
- **THEN** the system MUST persist the new relative order inside that same column
- **AND** the board MUST refresh automatically showing the card in the new position

#### Scenario: Order persists after reload
- **WHEN** the board is reloaded after a successful reorder
- **THEN** the cards in that column MUST appear in the same persisted order

### Requirement: Reorder MUST not bypass workflow gates
Changing the order of cards MUST NOT act as a status transition between workflow columns.

#### Scenario: Reorder stays inside the current column
- **WHEN** the user reorders a card
- **THEN** the card MUST remain in its current workflow column
- **AND** no approval/gate state may be implicitly changed
