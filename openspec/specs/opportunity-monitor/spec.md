# opportunity-monitor Specification

## Purpose
TBD - created by syncing delta from change improve-opportunity-monitor. Dashboard for favorite strategies with hold status and distance to next signal.
## Requirements
### Requirement: Simplified Hold Status Display
**Description:** The system SHALL display a clear indicator: HOLD (confirmed active position), WAIT (no confirmed active position), or EXIT (position closed/exit state). `HOLD` MUST require an active entry confirmation from strategy signal history; bullish trend state alone MUST NOT create `HOLD`. When holding, show distance to exit; when not holding, show distance to entry.
When the resolved state is EXIT, the monitor SHALL hide entry/stop operational lines from both card and chart views, because those values are no longer actionable.

#### Scenario: Opportunity in HOLD state
- **WHEN** the strategy has a confirmed active entry
- **AND** no later exit invalidates that entry
- **THEN** the UI displays distance to exit

#### Scenario: Opportunity in WAIT state
- **WHEN** the strategy has no confirmed active entry
- **THEN** the UI displays distance to entry

#### Scenario: Bullish trend without entry confirmation
- **WHEN** the strategy indicators are bullish
- **AND** there is no confirmed active entry in signal history
- **THEN** the UI displays WAIT instead of HOLD

#### Scenario: Opportunity in EXIT state
- **WHEN** an opportunity resolves to EXIT
- **THEN** card and chart entries for Entry/Stop are hidden and no new entry/stop price guidance is shown.

### Requirement: Distance to Next Status
**Description:** The system SHALL always display percentage distance to the next relevant status change, with progress bar and color coding (Green < 0.5%, Yellow 0.5–1%, Gray > 1%). When the status is WAIT (no position), the system SHALL compute the distance to entry using the entry rule: entry is valid only when (crossover(short, long) OR crossover(short, medium)) AND trend up (short > long). If trend up is false, the system SHALL measure distance using the short-to-long pair (red → blue). If trend up is true, the system SHALL measure distance using the short-to-medium pair (red → orange).

#### Scenario: WAIT with trend up false
- **WHEN** the strategy is in WAIT status and short <= long
- **THEN** the distance to entry is computed from the short-to-long pair (red → blue)

#### Scenario: WAIT with trend up true
- **WHEN** the strategy is in WAIT status and short > long
- **THEN** the distance to entry is computed from the short-to-medium pair (red → orange)

### Requirement: Simplified Opportunity Monitor Dashboard
**Description:** The system SHALL provide a dashboard at /monitor showing all favorite strategies. Each card shows: symbol, strategy name, hold status (HOLD/WAIT), distance to next status, current price. Strategies sorted by distance (closest first). Auto-refresh every 60 seconds.

The system MUST support non-crypto symbols (e.g., `AAPL`, `SPY`) in addition to crypto pairs (e.g., `BTC/USDT`) without changing existing crypto behavior.

#### Scenario: Dashboard shows favorite strategies for US stocks
- **WHEN** the user opens /monitor and has a favorite strategy configured for symbol `AAPL`
- **THEN** the dashboard lists that strategy card with symbol `AAPL` and its computed fields

#### Scenario: Existing crypto favorites are unaffected
- **WHEN** the user opens /monitor and has a favorite strategy configured for symbol `BTC/USDT`
- **THEN** the dashboard continues to list crypto strategies as before

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

