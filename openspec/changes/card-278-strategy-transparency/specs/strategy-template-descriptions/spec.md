## MODIFIED Requirements

### Requirement: Public Strategy Descriptions
The system SHALL expose one unique, trader-friendly and non-promissory PT-BR identity for each visible strategy/template. The name and description MUST be faithful to the executed configuration and SHALL explain entry context, exit context, consulted indicators, each indicator's function and risk control without source code or performance promises.

#### Scenario: Combo template list includes description
- **WHEN** an authorized user opens the Combo template selection flow
- **THEN** each listed template SHALL include the same public display name and description used by Favorites and Monitor.

#### Scenario: Favorites shows strategy and description
- **WHEN** a user opens Favorites
- **THEN** each favorite row/card SHALL show the canonical public strategy display name and description
- **AND** SHALL NOT show a generic fallback or internal research name.

#### Scenario: Monitor shows strategy description
- **WHEN** a user opens Monitor opportunities
- **THEN** the visible strategy identity SHALL match Favorites for the same strategy
- **AND** SHALL describe only indicators and behavior actually executed.

#### Scenario: Identity does not promise performance
- **WHEN** a public strategy description is rendered
- **THEN** it SHALL frame the strategy as decision support
- **AND** SHALL NOT promise return or make a personalized financial recommendation.
