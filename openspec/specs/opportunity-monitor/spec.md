# opportunity-monitor Specification

## Purpose
TBD - created by syncing delta from change improve-opportunity-monitor. Dashboard for favorite strategies with hold status and distance to next signal.
## Requirements
### Requirement: Simplified Hold Status Display
**Description:** The system SHALL display clear actionable Monitor decisions: HOLD (confirmed active position) or EXIT (position closed/exit state). `HOLD` MUST require an active entry confirmation from strategy signal history; bullish trend state alone MUST NOT create `HOLD`. Non-actionable states such as missing entry confirmation, neutral strategy state, stale context, timeframe mismatch, candle mismatch, unknown status, or internal wait fallback MUST be treated as not visible in the main Monitor board rather than as a third user-facing status. When holding, show distance to exit.
When the resolved state is EXIT, the monitor SHALL hide entry/stop operational lines from both card and chart views, because those values are no longer actionable.

#### Scenario: Opportunity in HOLD state
- **WHEN** the strategy has a confirmed active entry
- **AND** no later exit invalidates that entry
- **THEN** the UI displays distance to exit

#### Scenario: Opportunity has no actionable state
- **WHEN** the strategy has no confirmed active entry
- **AND** no actionable exit state exists
- **THEN** the main Monitor board does not display the opportunity as a visible decision
- **AND** the UI does not display `WAIT` as a user-facing status

#### Scenario: Bullish trend without entry confirmation
- **WHEN** the strategy indicators are bullish
- **AND** there is no confirmed active entry in signal history
- **THEN** the main Monitor board does not display the opportunity as `HOLD`
- **AND** the UI does not display `WAIT` as a user-facing status

#### Scenario: Opportunity in EXIT state
- **WHEN** an opportunity resolves to EXIT
- **THEN** card and chart entries for Entry/Stop are hidden and no new entry/stop price guidance is shown.

### Requirement: Distance to Next Status
**Description:** The system SHALL display percentage distance to the next relevant status change only for actionable Monitor rows. When the opportunity is in HOLD, the system SHALL display distance to exit. When the opportunity is non-actionable, the system MAY compute internal distance to entry for sorting, diagnostics, or future confirmation, but the main Monitor board MUST NOT display that result as a `WAIT` opportunity.

#### Scenario: HOLD distance
- **WHEN** the strategy is in active HOLD status
- **THEN** the visible distance reflects the next exit decision

#### Scenario: Non-actionable distance is internal
- **WHEN** the strategy has no actionable HOLD or EXIT state
- **THEN** any computed distance to entry remains internal to the resolver or diagnostics
- **AND** the main Monitor board does not display the strategy as a `WAIT` row

### Requirement: Simplified Opportunity Monitor Dashboard
**Description:** The system SHALL provide a dashboard at /monitor showing actionable favorite strategies. Each visible row/card shows: symbol, strategy name, actionable decision state (HOLD or EXIT), distance to next relevant status, and current price. Strategies are sorted by distance (closest first). Auto-refresh every 60 seconds.

The system MUST support non-crypto symbols (e.g., `AAPL`, `SPY`) in addition to crypto pairs (e.g., `BTC/USDT`) without changing existing crypto behavior.

#### Scenario: Dashboard shows favorite strategies for US stocks
- **WHEN** the user opens /monitor and has a favorite strategy configured for symbol `AAPL`
- **AND** that strategy resolves to an actionable HOLD or EXIT decision
- **THEN** the dashboard lists that strategy card with symbol `AAPL` and its computed fields

#### Scenario: Existing crypto favorites are unaffected
- **WHEN** the user opens /monitor and has a favorite strategy configured for symbol `BTC/USDT`
- **AND** that strategy resolves to an actionable HOLD or EXIT decision
- **THEN** the dashboard continues to list crypto strategies as before

#### Scenario: Non-actionable favorite strategy
- **WHEN** the user opens /monitor and a favorite strategy resolves to an internal wait, neutral, or uncertain state
- **THEN** the dashboard does not list that strategy as a visible opportunity

### Requirement: Monitor chart modal exposes direct zoom actions
The opportunity monitor SHALL expose direct zoom-in and zoom-out actions when a trader opens the detailed chart for a strategy.

#### Scenario: Direct zoom is available after opening chart
- **WHEN** the trader opens a strategy chart from a Monitor card
- **THEN** the modal includes direct zoom actions in the chart controls area

#### Scenario: Zoom works alongside existing chart actions
- **WHEN** the trader uses zoom controls in the Monitor chart modal
- **THEN** the existing close action, timeframe selector, and indicator toggles remain available

### Requirement: Monitor zoom controls are accessible through click and keyboard focus
The opportunity monitor MUST expose zoom controls as standard interactive UI controls that can receive focus and activation without pointer gestures.

#### Scenario: Zoom button can receive focus
- **WHEN** the trader navigates through the chart modal controls with keyboard focus
- **THEN** the zoom-in and zoom-out controls are reachable as focusable elements

#### Scenario: Zoom action can be triggered without mouse wheel
- **WHEN** the trader activates a zoom control using keyboard or click
- **THEN** the visible chart range changes in the same way as the corresponding direct zoom action

### Requirement: Monitor Telegram scan tracks observed status
The Monitor Telegram scan SHALL persist the latest observed status for each catalog `symbol + timeframe` independently from sent alert history.

#### Scenario: First observed sendable status can alert
- **WHEN** no observed status exists for a catalog `symbol + timeframe`
- **AND** the current Monitor status is sendable
- **THEN** the scan SHALL treat it as a new alert candidate
- **AND** persist the current status as the latest observed status

#### Scenario: Unchanged observed status does not alert
- **WHEN** the latest observed status for a `symbol + timeframe` equals the current Monitor status
- **THEN** the scan SHALL NOT send another alert for that unchanged status
- **AND** SHALL update the observed timestamp

#### Scenario: Silent status transition into sendable status alerts
- **WHEN** the latest observed status for a `symbol + timeframe` is not sendable
- **AND** the current Monitor status changes to a sendable status
- **THEN** the scan SHALL send an alert candidate using the observed previous status
- **AND** persist the current status as latest observed status

#### Scenario: Non-sendable status still updates observation
- **WHEN** the current Monitor status is not sendable
- **THEN** the scan SHALL persist that status as latest observed status
- **AND** SHALL NOT create an alert candidate

### Requirement: Monitor chart modal exposes resolved signal context
The opportunity monitor SHALL show explicit resolved signal context when a trader opens a strategy chart from the visible Monitor row.

#### Scenario: Mismatched exit signal opens with resolved state context
- **WHEN** a raw exit signal is downgraded to WAIT because the strategy timeframe or candle context does not match the displayed chart
- **THEN** the chart modal shows the resolved state, strategy timeframe, displayed timeframe, and explanatory context.

#### Scenario: Visible Monitor row opens strategy chart
- **WHEN** the trader activates the chart action on a visible Monitor row
- **THEN** the chart modal opens for that strategy without requiring the hidden expanded detail card.

### Requirement: Monitor chart modal exposes signal history
The opportunity monitor SHALL show recent entry and exit history in the chart modal when the strategy payload includes `signal_history`.

#### Scenario: Strategy payload includes recent signal history
- **WHEN** the trader opens a strategy chart from a visible Monitor row and the payload includes `signal_history`
- **THEN** the chart modal shows `Signal History` with recent `ENTRY` and `EXIT` entries.

#### Scenario: Signal history markers match chart timeframe
- **WHEN** signal history timestamps align with the displayed chart timeframe
- **THEN** the chart modal states that markers are aligned with the chart timeframe.

### Requirement: Monitor opportunity source falls back to curated favorites
The opportunity monitor SHALL use a configured admin-curated favorite set as a fallback source when the requesting user has no own Monitor-ready favorites for the requested Monitor filter.

#### Scenario: Fallback source is used only for empty user source
- **WHEN** the opportunity monitor loads favorites for a requesting user
- **AND** the requesting user's filtered favorite set has no crypto Monitor candidates
- **THEN** the monitor uses the first configured admin favorite set with matching Monitor-ready rows as the source for opportunity computation

#### Scenario: User source remains authoritative
- **WHEN** the opportunity monitor loads favorites for a requesting user
- **AND** the requesting user's filtered favorite set has at least one crypto Monitor candidate
- **THEN** the monitor computes opportunities only from the requesting user's favorites

### Requirement: Active entry state remains consistent with fresh market candles
The opportunity monitor SHALL classify a strategy with a confirmed active entry as HOLD or exit-tracking HOLD when fresh candles show no later exit invalidating that entry.

#### Scenario: Fresh ADA-like daily candles include active entry
- **WHEN** the strategy signal history contains an entry after the latest exit
- **AND** fresh daily candles confirm the active trend gate
- **THEN** the opportunity payload MUST set `is_holding=true`
- **AND** the Monitor UI MUST not display the opportunity as WAIT in the list.

### Requirement: Opportunity Monitor chart and history use Compra and Venda labels
The opportunity monitor SHALL use `Compra` and `Venda` in card badges, chart current markers, and visible signal history labels while preserving raw signal types for computation.

#### Scenario: Opportunity card renders public label
- **WHEN** a visible Monitor opportunity resolves to an active position state
- **THEN** the card badge SHALL show `Compra`
- **AND** when the opportunity resolves to exit/sell state the card badge SHALL show `Venda`.

#### Scenario: Chart modal renders public signal labels
- **WHEN** the trader opens a Monitor chart modal for a visible opportunity
- **THEN** the current signal badge and signal history labels SHALL use `Compra` for entry/buy events
- **AND** SHALL use `Venda` for exit/sell events.

#### Scenario: Non-actionable state remains hidden
- **WHEN** an opportunity resolves to an internal wait or uncertain state
- **THEN** the main Monitor board SHALL keep excluding it from visible actionable rows
- **AND** SHALL NOT expose `WAIT` as a public third signal label.

