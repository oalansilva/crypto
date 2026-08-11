## ADDED Requirements

### Requirement: Monitor displays tier as stars
The Monitor UI SHALL display strategy tier classification as a star rating.

#### Scenario: Tier 1 strategy
- **WHEN** a Monitor opportunity has `tier=1`
- **THEN** the UI displays a 3-star classification for that strategy

#### Scenario: Tier 2 strategy
- **WHEN** a Monitor opportunity has `tier=2`
- **THEN** the UI displays a 2-star classification for that strategy

#### Scenario: Tier 3 strategy
- **WHEN** a Monitor opportunity has `tier=3`
- **THEN** the UI displays a 1-star classification for that strategy
