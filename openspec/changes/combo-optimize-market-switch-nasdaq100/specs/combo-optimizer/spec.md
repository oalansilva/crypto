## ADDED Requirements

### Requirement: Combo Optimize supports market selection (Crypto vs US Stocks)
The Combo Optimize UI MUST allow the user to switch between **Crypto** and **US Stocks (NASDAQ-100)** markets.

#### Scenario: User selects Crypto market
- **WHEN** the user selects market `crypto`
- **THEN** the Symbol picker behaves as it does today (crypto pairs), and requests omit `data_source` (defaulting to crypto)

#### Scenario: User selects US Stocks market
- **WHEN** the user selects market `us-stocks`
- **THEN** the Symbol picker lists NASDAQ-100 tickers and requests include `data_source=stooq`

### Requirement: US Stocks market enforces EOD timeframe
When market `us-stocks` is selected, the system MUST enforce timeframe `1d` for Stooq EOD backtests.

#### Scenario: User attempts intraday timeframe for US Stocks
- **WHEN** the user selects market `us-stocks` and selects timeframe other than `1d`
- **THEN** the UI prevents the run and indicates that US Stocks via Stooq supports EOD (1D) only
