## MODIFIED Requirements

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
