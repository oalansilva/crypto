## ADDED Requirements

### Requirement: Monitor details start collapsed
The Monitor UI SHALL render strategy detail rows collapsed by default.

#### Scenario: Monitor loads opportunities
- **WHEN** Monitor opportunities are displayed
- **THEN** each strategy summary row is visible
- **AND** each strategy detail card is hidden until the user expands the row

#### Scenario: User expands a strategy
- **WHEN** the user clicks a strategy row expansion control
- **THEN** the detail card for that strategy becomes visible

#### Scenario: User collapses an expanded strategy
- **WHEN** the user clicks an expanded strategy row expansion control
- **THEN** the detail card for that strategy becomes hidden again
