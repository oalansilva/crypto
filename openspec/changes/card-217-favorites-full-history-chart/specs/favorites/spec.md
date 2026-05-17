## MODIFIED Requirements

### Requirement: Favorites analysis uses current market candles for chart rendering
The Favorites analysis flow SHALL merge available candle sources when opening a favorite analysis. Saved favorite trades and metrics SHALL remain the source for summary and trade evidence. The `/api/market/candles?full_history=true` data for the favorite symbol/timeframe SHALL be requested so the chart can use all persisted historical candles for the asset, independent of strategy. Saved `metrics.analysis_candles` SHALL be merged with market candles by timestamp so older backtest history and recent market candles both remain visible.

#### Scenario: Stale saved candles are replaced by full market history
- **WHEN** a favorite has saved `metrics.analysis_candles` ending before the current market candle window
- **AND** the full market candle series has at least as many candles as the saved chart context
- **AND** the user opens full analysis from Favorites
- **THEN** the result chart receives the merged saved and market candle series
- **AND** the newest chart candle matches the newest candle returned by `/api/market/candles`
- **AND** saved trades and metrics remain available in the result view

#### Scenario: Saved full-history candles are longer than market history response but older
- **WHEN** a favorite has saved `metrics.analysis_candles` covering a longer backtest history than the market candle response
- **AND** `/api/market/candles?full_history=true` returns newer candles after the saved chart context
- **AND** the user opens full analysis from Favorites
- **THEN** the result chart includes the saved older candles and the newer market candles
- **AND** saved trades and metrics remain available in the result view

#### Scenario: Current candle request fails
- **WHEN** current market candles cannot be loaded for the favorite
- **AND** saved `metrics.analysis_candles` exist
- **THEN** Favorites analysis can still render the saved candles as fallback
- **AND** the failure does not trigger favorite metric regeneration by itself

#### Scenario: Full persisted market history is incomplete
- **WHEN** Favorites analysis requests `/api/market/candles?full_history=true`
- **AND** the persisted OHLCV table does not cover the configured historical window or is stale
- **THEN** the backend schedules an OHLCV backfill job for the favorite symbol/timeframe
- **AND** the current request still returns the best available candle series
- **AND** future requests can use the backfilled candles after the job writes them

#### Scenario: Protected common user opens favorite analysis
- **WHEN** a common user opens a protected favorite analysis
- **THEN** the result chart uses the most complete allowed candle source
- **AND** the view does not show moving average overlays, moving average values, indicators, or protected parameters
