## Why

The current system is crypto-centric and relies on 24/7 exchange data. We want a free way to backtest and monitor US stocks/ETFs using end-of-day (1D) candles, enabling diversification and strategy validation without paying for a market data subscription.

## What Changes

- Add a free US stocks/ETFs EOD (1D) market data provider using Stooq.
- Introduce a normalized asset representation that supports both crypto and US stocks without changing existing crypto behavior.
- Add symbol mapping rules for US equities/ETFs (e.g., `AAPL` → provider symbol `aapl.us`).
- Ensure backtest and opportunity monitor pipelines can request and consume US stock EOD candles.

## Capabilities

### New Capabilities
- `us-stocks-eod-data`: Fetch and normalize US stocks/ETFs end-of-day OHLCV data (1D) via Stooq, including symbol mapping and caching.

### Modified Capabilities
- `opportunity-monitor`: Opportunities must support non-crypto symbols and market hours semantics for EOD-only datasets.
- `backtest-config`: Backtests must accept an asset class/source and work with EOD-only stock data.

## Impact

- Backend data loading layer (new provider + normalization).
- Opportunity monitor service (support for stock symbols and EOD refresh cadence).
- Potential UI adjustments to accept US tickers without `/` pairs.
- New/updated documentation and configuration defaults.
