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
The Monitor API and UI MUST hide implementation-only strategy secrets from non-admin users while preserving trading decisions and exposing canonical functional transparency.

#### Scenario: Non-admin views monitor opportunity
- **WHEN** a non-admin user opens Monitor
- **THEN** each opportunity MUST show its specific public identity, relevant effective parameters, used indicators and functional explanation
- **AND** MUST omit source code, credentials, raw diagnostics and internal mutation controls.

#### Scenario: Admin views monitor opportunity
- **WHEN** an admin user opens Monitor
- **THEN** each opportunity MUST show the same public manifest
- **AND** MAY additionally show authorized original identifiers and analyzer context.

#### Scenario: Non-admin exports opportunity summary
- **WHEN** a non-admin user exports or copies an opportunity summary
- **THEN** the export MUST include the canonical public identity and functional manifest summary
- **AND** MUST exclude source code, credentials, raw diagnostics and internal-only fields.

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
Monitor SHALL display the canonical public name, description and functional explanation wherever the user needs to understand a strategy.

#### Scenario: Opportunity row and detail show identity
- **WHEN** Monitor renders an opportunity with strategy metadata
- **THEN** row and detail SHALL use the same name and description as Favorites
- **AND** detail SHALL show indicator functions and participation without implementation-only secrets.

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
The Monitor chart modal SHALL present a readable strategy-detail surface while preserving existing signal resolution and rendering canonical public indicators.

#### Scenario: User opens Monitor chart
- **WHEN** the user opens an opportunity chart
- **THEN** the main chart SHALL remain dominant with symbol, public identity, signal, timeframe and candle context
- **AND** SHALL render manifest-defined indicator panels, legend and logic blocks when available.

#### Scenario: Common user opens protected strategy chart
- **WHEN** a common user opens a protected strategy chart
- **THEN** the modal SHALL show public effective parameters and functional indicator metadata
- **AND** SHALL NOT expose source code, raw diagnostics or internal implementation payloads.

#### Scenario: Modal is used on mobile
- **WHEN** the viewport is mobile-sized
- **THEN** chart, legend and context panels SHALL remain keyboard/touch usable without horizontal page scrolling.

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

### Requirement: Monitor chart opens with stable operational timeframe
Monitor opportunity cards SHALL open charts using the validated `1d` operational timeframe from the saved WIP.

#### Scenario: User opens a Monitor chart
- **WHEN** the user opens chart analysis from a Monitor opportunity card
- **THEN** the chart request uses timeframe `1d` and does not expose stale intraday timeframe controls

### Requirement: Monitor Labels Are Direction-Aware

The Monitor SHALL render public signal/status labels according to strategy direction.

#### Scenario: Short active position renders as sell/short

- **GIVEN** an opportunity belongs to a strategy with direction `short`
- **AND** the latest resolved phase is active/in-position
- **WHEN** the Monitor displays the opportunity
- **THEN** the public action label SHALL communicate sell/short semantics, not buy/long semantics

#### Scenario: Short exit renders as cover/buy

- **GIVEN** an opportunity belongs to a strategy with direction `short`
- **AND** the latest resolved phase is exit/flat
- **WHEN** the Monitor displays the opportunity
- **THEN** the public action label SHALL communicate buy/cover semantics, not sell/long-exit semantics

### Requirement: Monitor uses favorite transparency series when available
Monitor SHALL use the saved favorite transparency payload as the canonical series source when an opportunity maps to a favorite.

#### Scenario: Saved favorite analysis is available
- **WHEN** Monitor opens a chart for an opportunity with usable favorite analysis
- **THEN** it SHALL use the same candle timestamps, indicator series and manifest as Favorites
- **AND** SHALL preserve Compra/Venda markers, entry/stop lines, zoom, `Abrir Gráfico` and `Ver Trades`.

#### Scenario: Matching timeframe series is unavailable
- **WHEN** Monitor cannot load public series matching the visible timeframe
- **THEN** it SHALL clear indicator panels and show an explicit unavailable state
- **AND** SHALL keep chart and signal actions usable.

### Requirement: Monitor ignores temporally invalid favorite trade events
The Monitor MUST use a cached favorite entry or exit as authoritative position evidence only when the event is temporally compatible with the candle coverage used by the analysis.

#### Scenario: Exit occurs after the latest available candle
- **WHEN** the latest cached trade contains an exit timestamp after the latest analysis candle
- **THEN** the system MUST ignore that exit when resolving the current position
- **AND** MUST NOT force `EXIT`, `Venda`, or a closed position from that event

#### Scenario: Active entry has no valid later exit
- **WHEN** a valid entry is covered by the analysis candles and no valid later exit exists
- **THEN** the Monitor MUST resolve the long position as `HOLD`/`Compra`

#### Scenario: Cached exit predates a newer calculated entry
- **WHEN** a cached exit is within the candle range but a newer entry is present in the current calculated signal history
- **THEN** the cached exit MUST NOT overwrite the newer active entry
- **AND** the Monitor MUST remain `HOLD`/`Compra`

#### Scenario: Confirmed exit is covered by candles
- **WHEN** a valid exit occurs after the active entry and within the analysis candle coverage
- **THEN** the Monitor MUST resolve the position as `EXIT`/`Venda`
- **AND** badge, message and position state MUST reference that same exit

### Requirement: Monitor chart markers follow the resolved position evidence
The Monitor chart MUST keep its visible markers consistent with the temporally valid position evidence returned for the opportunity.

#### Scenario: Invalid future exit exists in cached history
- **WHEN** cached history contains a future exit outside the displayed candle range
- **THEN** the chart MUST NOT render or synthesize a sale marker from that exit
- **AND** an active visible entry MUST remain represented as `Compra`

#### Scenario: Valid exit is visible
- **WHEN** the resolved opportunity is exited and the corresponding exit is covered by displayed candles
- **THEN** the chart MUST render `Venda` on the correct candle
- **AND** the card badge and chart marker MUST agree

### Requirement: Favorite refresh rejects future trade evidence
The favorite refresh process MUST NOT replace previously valid metrics with a result whose trade events extend beyond the returned analysis candle coverage.

#### Scenario: Refreshed result contains a future trade event
- **WHEN** a refresh result contains an entry or exit later than its latest returned candle
- **THEN** the refresh MUST fail or remove the invalid event before persistence according to execution semantics
- **AND** MUST NOT publish that event as current Monitor state

#### Scenario: Position remains open at end of deep-backtest period
- **WHEN** a deep backtest reaches the end of available candles without exit logic or stop being triggered
- **THEN** the system MUST NOT synthesize an exit on the following day
- **AND** MUST NOT record `end_of_period` as a realized `signal_15m` trade

#### Scenario: Real intraday stop closes the final position
- **WHEN** a stop is reached in covered intraday candles before the backtest period ends
- **THEN** the system MUST preserve the stop exit and its covered timestamp

### Requirement: Cached result history is safe on read
The system MUST validate saved favorite trades against their saved candle coverage before returning or rendering them, including caches created before this change.

#### Scenario: Legacy cache contains future exit
- **WHEN** saved metrics contain an exit outside the saved analysis candle coverage
- **THEN** the read model MUST remove the invalid exit while preserving its valid entry
- **AND** MUST expose the final operation as open rather than sold

#### Scenario: Results table receives open operation
- **WHEN** a trade has a valid entry and no valid exit
- **THEN** the results table MUST display the entry as an open position
- **AND** MUST NOT render a fabricated exit row, exit price or realized profit

### Requirement: Partial candle caches preserve valid trade history
The favorite read model MUST treat saved candles as a potentially partial window and MUST NOT discard a historical trade only because its entry predates the first saved candle.

#### Scenario: Saved candles contain only recent context
- **WHEN** a cached trade entry predates the first saved analysis candle and its exit is not beyond the known coverage end
- **THEN** the read model MUST preserve that trade

#### Scenario: Trades were never generated
- **WHEN** saved metrics do not contain a `trades` list
- **THEN** the read model MUST preserve that absence so the regeneration path can execute


### Requirement: Monitor explains every trade
The Monitor trades view SHALL provide an “Entenda este trade” explanation for every open or closed trade returned by the favorite analysis contract.

#### Scenario: User expands a closed trade explanation
- **WHEN** the user activates “Entenda este trade” for a closed trade
- **THEN** the UI SHALL show why the entry was confirmed and why the exit occurred
- **AND** SHALL show decision candle, execution time, prices and allowlisted historical evidence
- **AND** SHALL label the exit as strategy rule, stop or real objective as applicable.

#### Scenario: User expands an open trade explanation
- **WHEN** the user activates “Entenda este trade” for an open trade
- **THEN** the UI SHALL show why the entry was confirmed
- **AND** SHALL state why no exit is confirmed
- **AND** SHALL present pending strategy-exit and stop conditions separately.

#### Scenario: Legacy trade has no trustworthy evidence
- **WHEN** an explanation is unavailable for a trade
- **THEN** the UI SHALL state that decision details are unavailable for that historical trade
- **AND** SHALL NOT generate an explanation from current values.

### Requirement: Monitor trade explanation is accessible and responsive
The Monitor SHALL expose trade explanations through a keyboard-operable disclosure that remains readable on desktop and mobile.

#### Scenario: Keyboard user opens explanation
- **WHEN** focus is on the “Entenda este trade” control and the user activates it
- **THEN** the control SHALL expose `aria-expanded` and `aria-controls`
- **AND** the labelled explanation panel SHALL become available in logical reading order
- **AND** focus SHALL remain visibly indicated.

#### Scenario: Mobile user opens explanation
- **WHEN** the viewport is narrower than 768px
- **THEN** the explanation SHALL use stacked content without horizontal page scrolling
- **AND** interactive targets SHALL provide at least a 44px effective target.

### Requirement: Monitor names the measured next trigger
The Monitor SHALL identify what each displayed distance measures instead of using an ambiguous generic “distance to exit” label.

#### Scenario: Strategy exit proximity is displayed
- **WHEN** the distance represents a technical exit rule
- **THEN** the UI SHALL label it as proximity to the strategy exit rule.

#### Scenario: Stop or objective distance is displayed
- **WHEN** a stop or supported objective distance is displayed
- **THEN** the UI SHALL label the specific stop or objective independently
- **AND** SHALL NOT present those distances as the same trigger.

### Requirement: Expanded trade always shows buy and sell rules
The Monitor trade disclosure SHALL show the strategy's permanent buy and sell rules simultaneously, independently of the current position or event explanation.

#### Scenario: User expands an open trade
- **WHEN** the user expands a trade whose position remains open
- **THEN** the panel SHALL show “Quando compra” and “Quando vende” before the current-position explanation
- **AND** SHALL keep stop/risk context separate from the permanent exit rule.

#### Scenario: User expands a closed or out-of-position trade
- **WHEN** the user expands a closed trade or a strategy that is currently out of position
- **THEN** the panel SHALL show both permanent rules
- **AND** SHALL show the actual entry/exit event explanations separately when available.

#### Scenario: User expands a short trade
- **WHEN** the trade direction is `short`
- **THEN** the two permanent rule cards SHALL retain the headings “Quando compra” and “Quando vende”
- **AND** SHALL clarify that entry opens by selling (short) and exit closes by buying (cobertura)
- **AND** SHALL show the canonical condition summaries under those clarifications.

#### Scenario: Long strategy avoids tautological action copy
- **WHEN** the trade direction is `long`
- **THEN** the permanent rule cards SHALL show “Quando compra” and “Quando vende” with the condition summaries
- **AND** SHALL NOT show redundant lines such as “Compra para entrar” or “Venda para sair”.

#### Scenario: Legacy payload has no permanent rule pair
- **WHEN** the expanded trade does not include the new permanent rule contract
- **THEN** both rule cards SHALL remain visible with a safe unavailable message
- **AND** SHALL NOT infer rules from the current event.

### Requirement: Permanent rule overview remains accessible and responsive
The permanent rule overview SHALL preserve the existing disclosure's keyboard semantics and remain readable without horizontal page scrolling.

#### Scenario: Keyboard user expands the rule overview
- **WHEN** the user activates the disclosure using the keyboard
- **THEN** the labelled strategy overview SHALL appear in logical reading order before event details
- **AND** the disclosure SHALL preserve `aria-expanded`, `aria-controls` and visible focus.

#### Scenario: Mobile user reads both rules
- **WHEN** the viewport is narrower than 768px
- **THEN** the buy and sell rule cards SHALL stack within the available width
- **AND** SHALL NOT introduce a new table column or horizontal page overflow.
