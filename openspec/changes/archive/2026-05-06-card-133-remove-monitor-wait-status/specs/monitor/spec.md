## MODIFIED Requirements

### Requirement: Common-user Monitor follows Favorites star tiers
The Monitor page MUST show only strategies marked with 1, 2, or 3 stars by default, and the main visible Monitor board MUST include only actionable resolved sections. Non-actionable results such as `WAIT`, `NEUTRAL`, `BUY_NEAR`, `BUY_SIGNAL`, stale context, timeframe mismatch, candle mismatch, unknown status, or missing active-entry confirmation MUST NOT be rendered as visible opportunities for common users.

#### Scenario: Common user opens Monitor
- **WHEN** a non-admin user opens `/monitor`
- **THEN** the Monitor request MUST ask the backend for `tier=1,2,3`
- **AND** visible opportunities MUST exclude unstarred strategies (`tier=null`)
- **AND** opportunities with `tier=1`, `tier=2`, or `tier=3` MUST remain visible only when they resolve to an actionable `HOLD` or `EXIT` section
- **AND** the UI MUST NOT require the strategy to be in portfolio or in local Monitor favorites to appear
- **AND** the UI MUST NOT render a main `WAIT` section, card, row, or KPI counter

#### Scenario: Backend returns unstarred opportunity defensively
- **WHEN** the backend response contains an unstarred opportunity
- **THEN** the Monitor UI MUST not render that opportunity by default

#### Scenario: Backend returns non-actionable opportunity defensively
- **WHEN** the backend response contains a rated opportunity whose resolved state is non-actionable
- **THEN** the Monitor UI MUST not render that opportunity in the main visible board
- **AND** the opportunity MUST NOT be coerced into `HOLD` or `EXIT`

#### Scenario: Admin opens Monitor
- **WHEN** an admin user opens `/monitor`
- **THEN** the existing operator filters and Monitor favorite preference controls MAY remain available
- **AND** the main visible board MUST still avoid exposing `WAIT` as a decision section

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
