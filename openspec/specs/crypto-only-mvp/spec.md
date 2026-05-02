# crypto-only-mvp Specification

## Purpose
TBD - created by archiving change issue-107-remover-acoes. Update Purpose after archive.
## Requirements
### Requirement: MVP operational flows are crypto-only
The system SHALL expose only crypto assets in MVP user-facing trading flows.

#### Scenario: User configures a combo
- **WHEN** the user opens Combo Configure
- **THEN** the market selection MUST only offer Crypto symbols
- **AND** the request payload MUST NOT send stock data-source overrides

#### Scenario: User views favorites
- **WHEN** the user opens Favorites
- **THEN** the list MUST only include favorites whose symbol is a crypto pair containing `/`

#### Scenario: User views monitor
- **WHEN** the user opens Monitor
- **THEN** opportunities and dashboard symbols MUST only include crypto pairs containing `/`

### Requirement: MVP market APIs reject stocks
The system SHALL reject stock market operations while the MVP is crypto-only.

#### Scenario: Request stock candle data
- **WHEN** a client requests `/api/market/candles` with a stock ticker
- **THEN** the API MUST return a 400 response explaining that the MVP supports only crypto pairs

#### Scenario: Request stock universe
- **WHEN** a client requests `/api/markets/us/nasdaq100`
- **THEN** the API MUST return an unavailable response explaining that stocks are disabled for the MVP

