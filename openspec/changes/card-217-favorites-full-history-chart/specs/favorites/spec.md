## MODIFIED Requirements

### Requirement: Favorites analysis uses current market candles for chart rendering
The Favorites analysis flow SHALL choose the most complete available candle source when opening a favorite analysis. Saved favorite trades and metrics SHALL remain the source for summary and trade evidence. Current `/api/market/candles` data SHALL be used when it is at least as complete as saved `metrics.analysis_candles`; saved `metrics.analysis_candles` SHALL be used when it contains a longer recoverable chart history.

#### Scenario: Stale saved candles are replaced by current market candles
- **WHEN** a favorite has saved `metrics.analysis_candles` ending before the current market candle window
- **AND** the current market candle series has at least as many candles as the saved chart context
- **AND** the user opens full analysis from Favorites
- **THEN** the result chart receives candles from `/api/market/candles`
- **AND** the newest chart candle matches the newest candle returned by `/api/market/candles`
- **AND** saved trades and metrics remain available in the result view

#### Scenario: Saved full-history candles are longer than current market candles
- **WHEN** a favorite has saved `metrics.analysis_candles` covering a longer backtest history than the current market candle window
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
