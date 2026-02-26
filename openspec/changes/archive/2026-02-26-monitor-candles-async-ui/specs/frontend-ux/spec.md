## ADDED Requirements

### Requirement: Monitor candles UX remains responsive on mobile
The UI MUST remain responsive on mobile when fetching candles after timeframe changes.

#### Scenario: No full-screen blocking overlay
- **WHEN** the user changes timeframe on a Monitor card
- **THEN** the UI does not show a full-screen blocking overlay; only the chart area indicates loading

#### Scenario: Scroll remains possible
- **WHEN** candle data is loading
- **THEN** the user can still scroll the Monitor list
