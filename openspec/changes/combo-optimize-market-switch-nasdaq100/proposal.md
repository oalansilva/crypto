## Why

Combo Optimize is currently crypto-centric (Binance-style symbols). We want to evaluate the same strategies on US stocks for diversification, starting with a curated NASDAQ-100 universe, using free EOD data (Stooq) already supported by the backend.

## What Changes

- Add a Market selector to Combo Optimize: **Crypto (current behavior)** vs **US Stocks (NASDAQ-100)**.
- When US Stocks is selected, the Symbol picker lists NASDAQ-100 tickers and the backtest/optimization requests use `data_source=stooq` and enforce `timeframe=1d`.
- Keep all existing crypto workflows unchanged.

## Capabilities

### New Capabilities
- `us-stocks-universe-nasdaq100`: Maintain and expose the NASDAQ-100 ticker universe for selection in the UI.

### Modified Capabilities
- `combo-optimizer`: Combo Optimize UI must support a market switch and pass `data_source` appropriately when running.

## Impact

- Frontend Combo Optimize page: new selector + symbol list behavior.
- Backend: add an endpoint (or config file) to provide NASDAQ-100 symbols.
- Documentation: how to run US stock EOD backtests from Combo Optimize.
