## MODIFIED Requirements

### Requirement: Favorites screen is available to authenticated users
The Favorites page MUST be directly accessible to any authenticated user while preserving protected strategy redaction for non-admin users, and its list layout MUST fit common desktop and mobile viewports without horizontal scrolling as the normal workflow.

#### Scenario: Non-admin opens favorites route
- **WHEN** a non-admin user opens `/favorites`
- **THEN** the frontend MUST render the Favorites page
- **AND** the page MUST list the admin-generated favorite strategy catalog
- **AND** the page MUST avoid exposing original strategy names, parameter values, or admin-only strategy actions for protected favorites
- **AND** the page MUST provide a star control to choose monitoring priority

#### Scenario: Admin opens favorites route
- **WHEN** an admin user opens `/favorites`
- **THEN** the frontend MUST render the existing favorites workflow
- **AND** the admin user MAY still see strategy internals and admin actions allowed by existing permissions

#### Scenario: Desktop favorites list avoids horizontal scrolling
- **WHEN** an authenticated user opens `/favorites` on a common desktop viewport
- **THEN** the Favorites list MUST fit within the viewport without requiring horizontal page or table scrolling
- **AND** tier, symbol, strategy, direction, timeframe, sharpe, trades, return, and analysis actions MUST remain visible

#### Scenario: Mobile favorites list avoids horizontal scrolling
- **WHEN** an authenticated user opens `/favorites` on a mobile viewport
- **THEN** the Favorites list MUST use the card layout
- **AND** the page MUST fit within the viewport without horizontal scrolling

#### Scenario: Advanced metrics remain accessible
- **WHEN** the desktop viewport cannot fit all advanced metric columns
- **THEN** the grid MAY hide lower-priority advanced metric columns
- **AND** those metrics MUST remain accessible through the existing wide-screen table, export, or analysis flows
