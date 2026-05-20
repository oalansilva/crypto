## ADDED Requirements

### Requirement: First-use onboarding prompt
The authenticated app SHALL show new users a concise onboarding prompt that explains where to start and how to continue the core beta journey.

#### Scenario: New user opens the app
- **WHEN** an authenticated user opens a protected route without dismissing onboarding in the current browser
- **THEN** the app SHALL show a concise first-use guide with the recommended starting path
- **AND** the guide SHALL provide direct actions to open Help and Favorites

#### Scenario: User dismisses first-use guide
- **WHEN** the user dismisses the first-use guide
- **THEN** the guide SHALL stop appearing in that browser session/storage
- **AND** Help SHALL remain accessible from navigation

### Requirement: Help center explains the recommended beta journey
The app SHALL provide a Help route that explains the recommended order of the main screens in simple Portuguese.

#### Scenario: User opens Help
- **WHEN** an authenticated user opens `/help`
- **THEN** the app SHALL explain the recommended order: Favoritos, selecionar estrategias, Monitor, Carteira Binance opcional
- **AND** Favoritos SHALL be described as the place to inspect charts/trades and choose strategies before monitoring
- **AND** the page SHALL provide direct navigation actions for the core screens

#### Scenario: User reads responsible positioning
- **WHEN** the user reads onboarding or Help content
- **THEN** the content SHALL frame Cripto Farol as apoio a decisao
- **AND** the content SHALL NOT promise profit, present signals as guaranteed calls, encourage leverage, or use guru-style claims

### Requirement: Onboarding remains responsive
The onboarding prompt and Help route SHALL be usable on desktop and mobile without broken text, overlap, or horizontal scrolling.

#### Scenario: Mobile user opens Help
- **WHEN** the Help route is viewed on a mobile viewport
- **THEN** the guide content SHALL reflow into a single-column layout
- **AND** primary actions SHALL remain visible and tappable without horizontal scrolling
