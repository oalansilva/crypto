## MODIFIED Requirements

### Requirement: Backtest Configuration Parameters
The system SHALL accept the following backtest configuration parameters:
- `symbol`: Trading symbol (e.g., "BTC/USDT" for crypto or "AAPL" for US stocks)
- `timeframe`: Signal generation timeframe (e.g., "1d", "4h")
- `since`: Start date (ISO 8601)
- `until`: End date (ISO 8601)
- `strategy`: Strategy template name
- `parameters`: Strategy-specific parameters (e.g., MA lengths, stop loss)
- `precision_mode`: Execution validation mode (`"fast"` | `"precise"`)
- `intraday_timeframe`: Timeframe for intraday validation (e.g., `"1h"`, `"15m"`) - required when `precision_mode="precise"`
- `data_source`: Optional market data source/provider identifier (e.g., `"ccxt"` for crypto, `"stooq"` for US stocks EOD)

#### Scenario: US stock backtest configuration with free EOD data
- **WHEN** user configures backtest with `{ "symbol": "AAPL", "timeframe": "1d", "data_source": "stooq" }`
- **THEN** the system validates the symbol and fetches EOD candles from Stooq

#### Scenario: Crypto backtest configuration remains supported
- **WHEN** user configures backtest with `{ "symbol": "BTC/USDT", "timeframe": "1d" }`
- **THEN** the system continues to fetch candles from the existing crypto data source

#### Scenario: Invalid intraday request for EOD-only source
- **WHEN** user configures backtest with `{ "symbol": "AAPL", "timeframe": "1h", "data_source": "stooq" }`
- **THEN** the system returns a validation error indicating the provider supports EOD (1D) only
