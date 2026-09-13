## MODIFIED Requirements

### Requirement: Incremental canonical candle writer
The canonical candle writer SHALL fetch incrementally after the first population by starting from the last saved candle, with a small idempotent overlap, and persisting into `market_ohlcv`. The default timeframe scope for this product surface SHALL be `15m`, `1h`, `4h` and `1d`. The default symbol scope SHALL be all Binance spot `*/USDT` market pairs available from the symbol cache/API, excluding symbols blocked by the existing excluded-symbol rules. A configured symbol cap MUST NOT shrink that universe for the analysis and Monitor candle contract.

#### Scenario: default writer symbol scope
- **GIVEN** no explicit candle writer symbol env is set
- **WHEN** the canonical writer resolves its symbol scope
- **THEN** it uses all Binance spot `*/USDT` symbols available from the symbol cache/API
- **AND** it excludes symbols blocked by the existing excluded-symbol rules
- **AND** it MUST NOT drop market pairs only because a DEV cap of 40 is configured

#### Scenario: default writer timeframe scope
- **GIVEN** no explicit candle writer timeframe env is set
- **WHEN** the canonical writer resolves its timeframe scope
- **THEN** it uses `15m`, `1h`, `4h` and `1d`
- **AND** it MUST NOT omit `1h` or `4h` because the previous default was only `15m` and `1d`

#### Scenario: one-shot writer catch-up
- **GIVEN** the operator runs the one-shot canonical writer command
- **WHEN** the command resolves the default symbol and timeframe scope
- **THEN** it runs the same incremental writer path for each market pair across `15m`, `1h`, `4h` and `1d`
- **AND** it exits without starting runtime worker, Celery worker, or Binance realtime worker processes

#### Scenario: symbol timeframe already has stored candles
- **GIVEN** `market_ohlcv` contains a latest candle for a symbol and timeframe
- **WHEN** the canonical writer runs for that symbol and timeframe
- **THEN** it fetches from the latest saved candle minus the configured overlap through the current moment
- **AND** it upserts the returned candles into `market_ohlcv`

#### Scenario: symbol timeframe has no stored candles
- **GIVEN** `market_ohlcv` has no candles for a symbol and timeframe
- **WHEN** the canonical writer runs for that symbol and timeframe
- **THEN** it uses the existing first-run lookback for that timeframe
- **AND** it persists the fetched candles into `market_ohlcv`

#### Scenario: stalled series catch up and stay current
- **GIVEN** a market pair/interval last candle is weeks or months behind (ex.: DOGE 1d in May)
- **WHEN** catch-up ingestion runs
- **THEN** the stored series reaches the present
- **AND** later incremental runs keep that series current instead of letting it stall months behind again

#### Scenario: screen-first fill does not shrink the universe
- **WHEN** the operator is looking at one pair/interval on Monitor or analysis
- **THEN** that pair/interval MAY be ingested first
- **AND** every other market pair still reaches the present on `15m`, `1h`, `4h` and `1d`
