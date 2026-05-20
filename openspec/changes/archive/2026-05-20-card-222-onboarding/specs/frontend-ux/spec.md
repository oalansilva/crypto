## ADDED Requirements

### Requirement: Navigation exposes Help entrypoint
The authenticated app navigation SHALL expose a persistent Help entrypoint for common and admin users.

#### Scenario: User views app navigation
- **WHEN** an authenticated user opens the app navigation
- **THEN** the navigation SHALL include an `Ajuda` link to `/help`
- **AND** the link SHALL be available to common and admin users

### Requirement: Core screens provide contextual guidance
Monitor and Favorites SHALL provide concise contextual guidance explaining the purpose of each screen.

#### Scenario: User opens Monitor
- **WHEN** the user opens `/monitor`
- **THEN** the page SHALL explain that Monitor is used to acompanhar sinais e contexto
- **AND** the guidance SHALL preserve responsible support-to-decision language

#### Scenario: User opens Favorites
- **WHEN** the user opens `/favorites`
- **THEN** the page SHALL explain that Favorites is used to curate strategies and stars before Monitor
- **AND** the guidance SHALL avoid technical jargon and excessive reading
