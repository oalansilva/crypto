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
The Monitor page MUST show only strategies marked with 1, 2, or 3 stars by default, regardless of whether the opportunity resolves to HOLD, WAIT, or EXIT. The Monitor MUST treat stars/tier as read-only classification from Favorites and MUST NOT provide its own favorite management, favorite filter, favorite counter, favorite toggle, local favorite storage, or Monitor-local favorite preferences.

#### Scenario: Common user opens Monitor
- **WHEN** a non-admin user opens `/monitor`
- **THEN** the Monitor request MUST ask the backend for `tier=1,2,3`
- **AND** visible opportunities MUST exclude unstarred strategies (`tier=null`)
- **AND** opportunities with `tier=1`, `tier=2`, or `tier=3` MUST remain visible in their resolved HOLD, WAIT, or EXIT section
- **AND** the UI MUST NOT require the strategy to be in portfolio or in local Monitor favorites to appear
- **AND** the UI MUST NOT expose a Monitor-local favorite action, filter, or count

#### Scenario: Backend returns unstarred opportunity defensively
- **WHEN** the backend response contains an unstarred opportunity
- **THEN** the Monitor UI MUST not render that opportunity by default

#### Scenario: Admin opens Monitor
- **WHEN** an admin user opens `/monitor`
- **THEN** the existing operator filters and Monitor preference controls MAY remain available except for favorite management controls
- **AND** the Monitor MUST NOT expose a favorite filter or favorite toggle

### Requirement: Monitor chart current marker matches active position state
The Monitor chart modal MUST represent an active `HOLD` opportunity as an open long position, not as an executed exit/sell marker. Non-actionable resolved states MUST remain excluded from the main Monitor board instead of being exposed through a visible `WAIT` decision.

#### Scenario: HOLD opportunity opens chart
- **WHEN** a Monitor opportunity is classified as active `HOLD`
- **AND** the chart has no historical signal markers to render
- **THEN** the chart current marker MUST use a long/entry-style visual
- **AND** the chart MUST NOT label the current marker as `EXIT`
- **AND** the distance panel MAY still label the next decision as `exit`

#### Scenario: Non-actionable opportunity exists
- **WHEN** a Monitor opportunity is not an active `HOLD` and has no actionable `EXIT`
- **THEN** the main Monitor board MUST exclude it instead of opening a visible `WAIT` chart flow

#### Scenario: Current EXIT signal exists after the active entry
- **WHEN** the generated signal history has an `exit` event after the latest `entry`
- **THEN** the Monitor payload MUST classify the opportunity as not holding
- **AND** the Monitor list MUST place the opportunity in `EXIT`, not `HOLD`
- **AND** the chart modal MUST resolve the same opportunity as `EXIT` when the latest visible signal is the current exit execution candle

### Requirement: Monitor list uses strategy decision timeframe
The Monitor list SHALL group opportunities into HOLD, WAIT, and EXIT using the backend opportunity decision state for the strategy timeframe. Card price timeframe preferences MUST NOT downgrade a list row from HOLD or EXIT to WAIT.

#### Scenario: Strategy timeframe differs from price card timeframe
- **WHEN** an opportunity has `is_holding=true` and a HOLD-compatible status such as `HOLDING` or `EXIT_NEAR`
- **AND** the saved card price timeframe differs from the opportunity strategy timeframe
- **THEN** the Monitor list MUST still place that opportunity in HOLD
- **AND** timeframe mismatch review MUST remain limited to the chart modal display context.

### Requirement: Monitor delegates favorite curation to Favorites
The Monitor MUST NOT provide controls for adding, removing, filtering, or locally storing favorite strategies. Favorites curation and star/tier ranking SHALL be managed on the Favorites screen.

#### Scenario: User views Monitor toolbar
- **WHEN** the user opens `/monitor`
- **THEN** the toolbar MUST NOT include a `Favoritos` filter
- **AND** the visible result summary MUST NOT include a favorites count

#### Scenario: User views Monitor row actions
- **WHEN** the user views a Monitor opportunity row
- **THEN** the row actions MUST NOT include `Favoritar` or `Remover favorito`
- **AND** the row MAY still show read-only star/tier classification

#### Scenario: Monitor loads
- **WHEN** the Monitor loads opportunities
- **THEN** it MUST NOT read or write Monitor-local favorite localStorage
- **AND** it MUST NOT call Monitor strategy preference endpoints for local favorite state

