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

### Requirement: Monitor Strategy Description
Monitor SHALL display a high-level strategy description wherever the user needs to understand what a strategy is trying to capture.

#### Scenario: Opportunity row and detail show description
- **WHEN** Monitor renders an opportunity with strategy metadata
- **THEN** the row/detail SHALL show the public strategy description when available
- **AND** SHALL not expose technical parameters to common users.

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

### Requirement: Monitor public signal language uses Compra and Venda
The Monitor SHALL present public decision labels as `Compra` and `Venda` instead of exposing `HOLD` and `EXIT` to end users. Internal raw statuses MAY remain unchanged for classification, API compatibility, logs, and tests.

#### Scenario: User views Monitor summary and sections
- **WHEN** the user opens `/monitor`
- **THEN** the visible summary tags and actionable section headers SHALL use `Compra` for active buy/position state
- **AND** the visible summary tags and actionable section headers SHALL use `Venda` for exit/sell state
- **AND** the user SHALL NOT see `HOLD` or `EXIT` as primary Monitor decision labels.

#### Scenario: Technical state remains internal
- **WHEN** Monitor receives raw status values such as `HOLDING`, `HOLD`, `EXIT_SIGNAL`, or `EXITED`
- **THEN** the resolver MAY continue using those values internally
- **AND** the user-facing badge text SHALL still render as `Compra` or `Venda`.

### Requirement: Monitor separates chart and trades actions
The Monitor UI SHALL expose two explicit Portuguese actions for each visible strategy opportunity: `Abrir Grafico` for chart-only inspection and `Ver Trades` for trade analysis.

#### Scenario: User opens chart-only view
- **WHEN** the user selects `Abrir Grafico` from a Monitor strategy
- **THEN** the system SHALL open the strategy chart
- **AND** the modal SHALL NOT render the strategy summary panel
- **AND** the modal SHALL NOT render the trades list

#### Scenario: User opens trades view
- **WHEN** the user selects `Ver Trades` from a Monitor strategy
- **THEN** the system SHALL open the strategy analysis view
- **AND** the modal SHALL render the strategy summary/context panel
- **AND** the modal SHALL render the trades list and trade metrics when available

### Requirement: Monitor chart modal uses strategy-detail layout
The Monitor chart modal SHALL present the selected opportunity as a readable strategy-detail surface inspired by the card #218 `Estrategia.html` reference, while preserving existing signal resolution and data behavior.

#### Scenario: User opens Monitor chart
- **WHEN** the user opens a Monitor opportunity chart
- **THEN** the modal SHALL show a compact strategy header with symbol, public strategy label, resolved signal and timeframe/candle context
- **AND** the main chart SHALL remain the dominant visible surface
- **AND** supporting context SHALL be organized in compact panels instead of a long technical stack.

#### Scenario: Common user opens protected strategy chart
- **WHEN** the chart belongs to a protected strategy and the viewer is not allowed to see parameters
- **THEN** the modal SHALL keep parameter values redacted
- **AND** the new layout SHALL NOT expose original protected implementation details.

#### Scenario: Modal is used on mobile
- **WHEN** the viewport is mobile-sized
- **THEN** the modal SHALL keep the chart and context panels usable without horizontal scrolling.

### Requirement: Monitor graph shares chart base
Monitor graph modal SHALL use the same chart base as Favorites while retaining Monitor-specific operational context.

#### Scenario: Monitor keeps signal context
- **WHEN** the Monitor graph modal opens
- **THEN** it SHALL show the shared candle/volume chart
- **AND** it SHALL keep signal badge, strategy summary, timeframe selector, signal context, signal history, risk/stop details, parameters and notes according to the opportunity visibility rules.

### Requirement: Monitor chart modal keeps saved favorite parity
The Monitor chart modal SHALL treat the saved favorite id as the identity for chart parity with Favorites and SHALL not render a divergent marker source when favorite analysis data is available.

#### Scenario: Monitor card shows Venda and Favorite chart has sell marker
- **WHEN** a Monitor opportunity for a saved favorite is classified as `Venda`
- **AND** the Favorite analysis payload includes a sell trade for the same favorite
- **THEN** opening `Abrir Gráfico` from Monitor SHALL show the sell marker from the favorite analysis trade set
- **AND** the chart marker source SHALL not be limited to the opportunity `signal_history`.

#### Scenario: Monitor and Favorites use same favorite id
- **WHEN** Monitor and Favorites refer to the same `favorite_id`
- **THEN** both chart paths SHALL resolve trades and candles from the same favorite analysis payload where permitted.

