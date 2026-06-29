## MODIFIED Requirements

### Requirement: Monitor Labels Are Direction-Aware

The Monitor SHALL render public signal/status labels according to strategy direction.

#### Scenario: Short active position renders as sell/short

- **GIVEN** an opportunity belongs to a strategy with direction `short`
- **AND** the latest resolved phase is active/in-position
- **WHEN** the Monitor displays the opportunity
- **THEN** the public action label SHALL communicate sell/short semantics, not buy/long semantics

#### Scenario: Short exit renders as cover/buy

- **GIVEN** an opportunity belongs to a strategy with direction `short`
- **AND** the latest resolved phase is exit/flat
- **WHEN** the Monitor displays the opportunity
- **THEN** the public action label SHALL communicate buy/cover semantics, not sell/long-exit semantics
