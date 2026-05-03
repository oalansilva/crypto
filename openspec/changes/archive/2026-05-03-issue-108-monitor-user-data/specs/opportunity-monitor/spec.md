## ADDED Requirements

### Requirement: Monitor opportunity source falls back to curated favorites
The opportunity monitor SHALL use a configured admin-curated favorite set as a fallback source when the requesting user has no own Monitor-ready favorites for the requested Monitor filter.

#### Scenario: Fallback source is used only for empty user source
- **WHEN** the opportunity monitor loads favorites for a requesting user
- **AND** the requesting user's filtered favorite set has no crypto Monitor candidates
- **THEN** the monitor uses the first configured admin favorite set with matching Monitor-ready rows as the source for opportunity computation

#### Scenario: User source remains authoritative
- **WHEN** the opportunity monitor loads favorites for a requesting user
- **AND** the requesting user's filtered favorite set has at least one crypto Monitor candidate
- **THEN** the monitor computes opportunities only from the requesting user's favorites
