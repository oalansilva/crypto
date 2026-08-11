## MODIFIED Requirements

### Requirement: Public Strategy Descriptions
The system SHALL expose a short, trader-friendly, non-promissory public identity for each visible strategy/template. Public identity SHALL include a distinguishable display name and high-level description, and MUST NOT expose parameter values, thresholds, formulas, exact indicator combinations, full entry/exit rules, or implementation details that allow recreation outside the platform.

#### Scenario: Combo template list includes description
- **WHEN** an admin opens the Combo template selection flow
- **THEN** each listed template SHALL include a high-level description beside the template name
- **AND** the description SHALL avoid parameter dumps and profit promises.

#### Scenario: Favorites shows strategy and description
- **WHEN** a common user opens Favorites
- **THEN** each favorite row/card SHALL show the public strategy display name
- **AND** SHALL show a high-level description when available
- **AND** SHALL NOT show parameters, thresholds, formulas, exact indicator combinations, or complete entry/exit logic.

#### Scenario: Monitor shows strategy description
- **WHEN** a common user opens Monitor opportunities
- **THEN** the visible strategy identity SHALL include a public display name and high-level description when available
- **AND** the public copy SHALL explain the market-reading purpose without exposing a replicable technical recipe.

#### Scenario: Admin keeps technical audit identity
- **WHEN** an admin views strategy metadata in an authorized surface
- **THEN** the system MAY show the original template name, parameters, raw description, and technical implementation details needed for audit.
