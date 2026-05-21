## MODIFIED Requirements

### Requirement: Core screens provide contextual guidance
Monitor and Favorites SHALL provide concise contextual guidance explaining the purpose of each screen.

#### Scenario: User opens Monitor
- **WHEN** the user opens `/monitor`
- **THEN** the page SHALL explain that Monitor is used to acompanhar strategies selected in Favorites
- **AND** the guidance SHALL preserve responsible support-to-decision language

#### Scenario: User opens Favorites
- **WHEN** the user opens `/favorites`
- **THEN** the page SHALL explain that Favorites is the starting point to compare strategies, inspect charts/trades, and choose what to monitor
- **AND** the guidance SHALL avoid technical jargon and excessive reading
