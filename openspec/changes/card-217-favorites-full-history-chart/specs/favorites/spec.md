## MODIFIED Requirements

### Requirement: Favorites analysis uses current market candles for chart rendering
The Favorites analysis flow SHALL choose the most complete available candle source when opening a favorite analysis. Saved favorite trades and metrics SHALL remain the source for summary and trade evidence. The `/api/market/candles?full_history=true` data for the favorite symbol/timeframe SHALL be requested so the chart can use all persisted historical candles for the asset, independent of strategy. Saved `metrics.analysis_candles` SHALL remain a fallback and SHALL still be used when it contains a longer recoverable chart history.

#### Scenario: Stale saved candles are replaced by full market history
- **WHEN** a favorite has saved `metrics.analysis_candles` ending before the current market candle window
- **AND** the full market candle series has at least as many candles as the saved chart context
- **AND** the user opens full analysis from Favorites
- **THEN** the result chart receives candles from `/api/market/candles`
- **AND** the newest chart candle matches the newest candle returned by `/api/market/candles`
- **AND** saved trades and metrics remain available in the result view

#### Scenario: Saved full-history candles are longer than market history response
- **WHEN** a favorite has saved `metrics.analysis_candles` covering a longer backtest history than the market candle response
- **AND** the user opens full analysis from Favorites
- **THEN** the result chart receives the saved full-history candle series
- **AND** saved trades and metrics remain available in the result view

#### Scenario: Current candle request fails
- **WHEN** current market candles cannot be loaded for the favorite
- **AND** saved `metrics.analysis_candles` exist
- **THEN** Favorites analysis can still render the saved candles as fallback
- **AND** the failure does not trigger favorite metric regeneration by itself

#### Scenario: Protected common user opens favorite analysis
- **WHEN** a common user opens a protected favorite analysis
- **THEN** the result chart uses the most complete allowed candle source
- **AND** the view does not show moving average overlays, moving average values, indicators, or protected parameters
