## MODIFIED Requirements

### Requirement: Monitor opportunity source falls back to curated favorites
The opportunity monitor SHALL use a configured admin-curated favorite set as a fallback source when the requesting user has no own Monitor-ready favorites for the requested Monitor filter. Non-admin Monitor opportunity payloads SHALL expose a safe public strategy display name while keeping raw strategy identifiers, parameters, indicator values, execution details, and fallback admin notes redacted. Non-admin Monitor opportunity results SHALL include only strategies classified as Tier 1, Tier 2, or Tier 3. Monitor opportunity detail rows SHALL be collapsed by default while keeping summary rows visible.

#### Scenario: Fallback source selected
- **WHEN** the opportunity monitor loads favorites for a requesting user
- **AND** the requesting user's filtered favorite set has no crypto Monitor candidates
- **THEN** the monitor uses the first configured admin favorite set with matching Monitor-ready rows as the source for opportunity computation

#### Scenario: Own favorites take precedence
- **WHEN** the opportunity monitor loads favorites for a requesting user
- **AND** the requesting user's filtered favorite set has at least one crypto Monitor candidate
- **THEN** the monitor computes opportunities only from the requesting user's favorites

#### Scenario: Details collapsed by default
- **WHEN** Monitor opportunities are rendered
- **THEN** opportunity summary rows are visible
- **AND** detail cards are hidden until expanded
