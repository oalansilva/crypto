## MODIFIED Requirements

### Requirement: Favorites can be filtered by asset type
The system MUST keep the Favorites screen crypto-only while the MVP excludes stocks.

#### Scenario: Favorites default to crypto-only
- **WHEN** the user opens the Favorites screen
- **THEN** the Favorites list MUST show only items whose symbol contains `/`

#### Scenario: Stocks option is unavailable
- **WHEN** the Favorites filter controls are rendered
- **THEN** the screen MUST NOT show a Stocks asset-type option

### Requirement: Asset type filter applies to both desktop and mobile layouts
The system MUST apply the crypto-only Favorites collection consistently across all responsive layouts.

#### Scenario: Mobile cards are crypto-only
- **WHEN** the Favorites screen is rendered in mobile layout
- **THEN** the mobile card list MUST include only crypto pairs whose symbol contains `/`

#### Scenario: Desktop table is crypto-only
- **WHEN** the Favorites screen is rendered in desktop layout
- **THEN** the desktop table MUST include only crypto pairs whose symbol contains `/`
