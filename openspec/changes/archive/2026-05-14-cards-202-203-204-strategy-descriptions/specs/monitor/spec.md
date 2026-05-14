## MODIFIED Requirements

### Requirement: Monitor Strategy Description

Monitor SHALL display a high-level strategy description wherever the user needs to understand what a strategy is trying to capture.

#### Scenario: Opportunity row and detail show description

- **WHEN** Monitor renders an opportunity with strategy metadata
- **THEN** the row/detail SHALL show the public strategy description when available
- **AND** SHALL not expose technical parameters to common users.
