# opportunity-monitor Specification

## Purpose
TBD - created by syncing delta from change improve-opportunity-monitor. Dashboard for favorite strategies with hold status and distance to next signal.
## Requirements
### Requirement: Simplified Hold Status Display
**Description:** The system SHALL display a clear binary indicator: HOLD (active position) or WAIT (no position). When holding, show distance to exit; when not holding, show distance to entry.

#### Scenario: HOLD distance shown
- **WHEN** the strategy is in HOLD status
- **THEN** the UI displays distance to exit

#### Scenario: WAIT distance shown
- **WHEN** the strategy is in WAIT status
- **THEN** the UI displays distance to entry

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

