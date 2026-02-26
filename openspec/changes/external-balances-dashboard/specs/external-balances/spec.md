## ADDED Requirements

### Requirement: System MUST provide a Binance Spot balances snapshot endpoint
The system MUST provide a backend endpoint that returns the current Binance Spot balances using a configured read-only API key.

#### Scenario: Successful snapshot
- **WHEN** the user requests the Binance Spot snapshot
- **THEN** the system MUST return a JSON payload containing balances with `asset`, `free`, `locked`, and `total`

#### Scenario: Secret missing
- **WHEN** Binance credentials are not configured on the server
- **THEN** the system MUST return an error that clearly indicates missing configuration

### Requirement: System MUST provide a UI page to display external balances
The system MUST provide a UI page that displays Binance Spot balances in a readable list.

#### Scenario: Display balances
- **WHEN** the user opens the external balances page
- **THEN** the UI MUST show the list of balances and highlight which assets have `locked` amounts

### Requirement: Integration MUST be read-only
The system MUST NOT place orders, withdraw, or modify the Binance account.

#### Scenario: Read-only enforcement
- **WHEN** the system is configured for Binance
- **THEN** it MUST only call read-only Binance endpoints
