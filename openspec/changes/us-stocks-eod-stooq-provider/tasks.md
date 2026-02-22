## 1. Provider foundation

- [ ] 1.1 Create a market data provider abstraction (interface/protocol) used by backtest and monitor
- [ ] 1.2 Implement `StooqEodProvider` that fetches US stock/ETF EOD OHLCV and returns normalized columns
- [ ] 1.3 Implement symbol mapping `AAPL` → `aapl.us` and `SPY` → `spy.us` inside the provider
- [ ] 1.4 Enforce EOD-only timeframe support for Stooq (reject non-`1d`)

## 2. Caching and reliability

- [ ] 2.1 Add caching for `(source, symbol, timeframe)` with an EOD-appropriate TTL
- [ ] 2.2 Add retries/backoff and clear validation errors for provider failures

## 3. Backtest integration

- [ ] 3.1 Extend backtest request schema to accept optional `data_source` (default remains existing crypto source)
- [ ] 3.2 Route data loading through provider selection; keep crypto path unchanged
- [ ] 3.3 Add validation: `data_source=stooq` implies `timeframe=1d`

## 4. Opportunity monitor integration

- [ ] 4.1 Ensure favorites/opportunity computations accept US tickers (no `/` required)
- [ ] 4.2 Ensure monitor can refresh EOD-based opportunities without assuming 24/7 candles

## 5. Tests and documentation

- [ ] 5.1 Add unit tests for Stooq symbol mapping and EOD-only enforcement
- [ ] 5.2 Add a basic integration test (or smoke script) to fetch `AAPL` and compute indicators
- [ ] 5.3 Update docs/readme for enabling US stocks EOD with `data_source=stooq`

## 6. Notes

- [ ] 6.1 Use project skills under `.codex/skills` when applicable (architecture, tests, debugging, frontend)
