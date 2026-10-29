## MODIFIED Requirements

### Requirement: Canonical Binance candle reads

The market candles API SHALL use `market_ohlcv` as the canonical read source for Binance OHLCV candles when canonical candle mode is enabled, through the same history service used by backtest, combo, optimization and discovery. For the same series, version and period, the chart SHALL return the same candles the analyses receive, and the response SHALL carry the series coverage (period covered, gaps, last update and version).

#### Scenario: fresh persisted candles exist

- **GIVEN** canonical candle mode is enabled
- **AND** `market_ohlcv` has fresh candles for the requested symbol and timeframe
- **WHEN** a client requests market candles
- **THEN** the response returns the persisted candles
- **AND** the response marks the source as canonical storage
- **AND** the response includes the series version and coverage.

#### Scenario: direct fetch fallback is disabled

- **GIVEN** canonical candle mode is enabled
- **AND** direct Binance candle fallback is disabled
- **AND** canonical storage has no fresh candles for the requested symbol and timeframe
- **WHEN** a client requests market candles
- **THEN** the API SHALL NOT fetch Binance directly from the request path
- **AND** the response SHALL either return persisted stale candles or an empty canonical payload
- **AND** the coverage SHALL say the history is stale or missing instead of complete.

#### Scenario: same candles as the analyses

- **GIVEN** a backtest of BTC/USDT 4h read version V for a period
- **WHEN** the chart requests BTC/USDT 4h for the same period and version V
- **THEN** both receive identical candles.
