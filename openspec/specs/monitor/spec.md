# monitor Specification

## Purpose
TBD - created by archiving change monitor-asset-type-filter. Update Purpose after archive.
## Requirements
### Requirement: Monitor MUST provide an Asset Type filter
The Monitor page (`/monitor`) MUST NOT provide an Asset Type filter while the MVP is crypto-only.

#### Scenario: Open monitor
- **WHEN** the user opens `/monitor`
- **THEN** the Monitor MUST display only crypto opportunities whose symbol contains `/`
- **AND** the Monitor MUST NOT expose a stocks option

### Requirement: Monitor hides strategy secrets from non-admin users
The Monitor API and UI MUST hide strategy implementation details from non-admin users while preserving the current trading decision workflow.

#### Scenario: Non-admin views monitor opportunity
- **WHEN** a non-admin user opens the Monitor
- **THEN** each opportunity MUST avoid showing the original strategy/template name
- **AND** each opportunity MUST avoid showing parameter values and indicator values
- **AND** the UI MUST show a protected strategy label instead of empty or broken content

#### Scenario: Admin views monitor opportunity
- **WHEN** an admin user opens the Monitor
- **THEN** each opportunity MUST show the original strategy/template name, parameters, indicator values, and analyzer context as before

#### Scenario: Non-admin exports opportunity summary
- **WHEN** a non-admin user exports or copies an opportunity summary
- **THEN** the exported payload MUST NOT include original strategy/template names, parameter values, indicator values, or analyzer details

### Requirement: Common-user Monitor follows Favorites star tiers
The Monitor page MUST show common users only strategies that they marked with stars in Favorites.

#### Scenario: Common user opens Monitor
- **WHEN** a non-admin user opens `/monitor`
- **THEN** the Monitor request MUST use the backend common-user tier policy
- **AND** the visible list MUST be based on the current user's tier preferences for admin Favorites (`tier=1`, `tier=2`, or `tier=3`)
- **AND** unstarred favorites (`tier=null`) MUST NOT be shown
- **AND** the UI MUST NOT require the strategy to be in portfolio or in local Monitor favorites to appear

#### Scenario: Admin opens Monitor
- **WHEN** an admin user opens `/monitor`
- **THEN** the existing operator filters and Monitor favorite preference controls MAY remain available
