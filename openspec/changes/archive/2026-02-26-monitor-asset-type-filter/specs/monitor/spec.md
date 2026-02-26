## ADDED Requirements

### Requirement: Monitor MUST provide an Asset Type filter
The Monitor page (`/monitor`) MUST provide an Asset Type filter with the options:
- `all`
- `crypto`
- `stocks`

#### Scenario: Default option
- **WHEN** the user opens `/monitor`
- **THEN** the Asset Type filter MUST default to `all`

#### Scenario: Filter to crypto
- **WHEN** the user selects `crypto`
- **THEN** the Monitor list MUST display only items whose symbol represents a crypto pair (contains `/`, e.g., `BTC/USDT`)

#### Scenario: Filter to stocks
- **WHEN** the user selects `stocks`
- **THEN** the Monitor list MUST display only items whose symbol represents a stock ticker (does not contain `/`, e.g., `AAPL`)

### Requirement: Asset Type filter MUST not require persistence
The Asset Type filter selection MUST be applied only to the current view state and MUST NOT require saving preferences to the backend.

#### Scenario: No persistence
- **WHEN** the user refreshes the page
- **THEN** the filter MUST reset to the default (`all`)
