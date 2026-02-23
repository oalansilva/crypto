## MODIFIED Requirements

### Requirement: Simplified Opportunity Monitor Dashboard
**Description:** The system SHALL provide a dashboard at /monitor showing all favorite strategies. Each card shows: symbol, strategy name, hold status (HOLD/WAIT), distance to next status, current price. Strategies sorted by distance (closest first). Auto-refresh every 60 seconds.

The system MUST support non-crypto symbols (e.g., `AAPL`, `SPY`) in addition to crypto pairs (e.g., `BTC/USDT`) without changing existing crypto behavior.

#### Scenario: Dashboard shows favorite strategies for US stocks
- **WHEN** the user opens /monitor and has a favorite strategy configured for symbol `AAPL`
- **THEN** the dashboard lists that strategy card with symbol `AAPL` and its computed fields

#### Scenario: Existing crypto favorites are unaffected
- **WHEN** the user opens /monitor and has a favorite strategy configured for symbol `BTC/USDT`
- **THEN** the dashboard continues to list crypto strategies as before
