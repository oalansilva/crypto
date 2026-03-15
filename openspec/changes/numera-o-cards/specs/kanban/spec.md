## ADDED Requirements

### Requirement: Stable human-friendly card number
The Kanban runtime MUST assign each card a stable human-friendly sequential number that can be used for communication and lookup.

#### Scenario: Existing card keeps its assigned number
- **WHEN** a previously created card is returned by the runtime
- **THEN** the payload includes its assigned card number
- **AND** the number remains stable across reloads and later workflow transitions

#### Scenario: New card receives next available number
- **WHEN** a new card/change is created in the runtime
- **THEN** it receives the next available sequential card number
- **AND** the assigned number does not duplicate another existing card number

### Requirement: Card number is visible in Kanban UI
The Kanban UI MUST display the card number in both the board card and the card detail view.

#### Scenario: Board card shows the number
- **WHEN** the board renders a card
- **THEN** the card visibly shows its human-friendly number near the title or metadata
- **AND** the title and technical slug remain available

#### Scenario: Detail drawer shows the same number
- **WHEN** the user opens card details
- **THEN** the same card number is shown in the drawer/detail view

### Requirement: Card number does not change with reordering or editing
The card number MUST be an identifier, not an ordering mechanism.

#### Scenario: Reorder preserves number
- **WHEN** a card is moved up or down within a column
- **THEN** its visible card number stays the same

#### Scenario: Edit preserves number
- **WHEN** a card title or description is edited
- **THEN** the card number stays the same
