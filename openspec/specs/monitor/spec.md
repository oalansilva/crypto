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
