## ADDED Requirements

### Requirement: Favorites owns strategy curation for Monitor
The Favorites screen SHALL be the canonical UI for choosing, removing, and ranking strategies that feed the Monitor. The Monitor SHALL consume Favorites ranking as read-only tier/star classification and SHALL NOT duplicate favorite curation controls.

#### Scenario: User changes strategy ranking
- **WHEN** the user wants to change a strategy star/tier ranking
- **THEN** the user MUST do that on the Favorites screen
- **AND** the Monitor reflects that ranking as read-only classification

#### Scenario: User removes a strategy from curation
- **WHEN** the user wants to remove a strategy from the monitored favorite catalog
- **THEN** the user MUST do that on the Favorites screen
- **AND** the Monitor MUST NOT expose a separate remove-favorite action
