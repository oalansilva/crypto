## MODIFIED Requirements

### Requirement: Favorites analysis uses current market candles for chart rendering
The Favorites analysis flow SHALL use the current market candles source as the primary chart candle source when opening a favorite analysis. Saved favorite trades and metrics SHALL remain the source for summary and trade evidence. Saved `metrics.analysis_candles` SHALL be used only as a fallback when current market candles cannot be loaded.

#### Scenario: Stale saved candles are replaced by current market candles
- **WHEN** a favorite has saved `metrics.analysis_candles` ending before the current market candle window
- **AND** the user opens full analysis from Favorites
- **THEN** the result chart receives candles from `/api/market/candles`
- **AND** the newest chart candle matches the newest candle returned by `/api/market/candles`
- **AND** saved trades and metrics remain available in the result view

#### Scenario: Current candle request fails
- **WHEN** current market candles cannot be loaded for the favorite
- **AND** saved `metrics.analysis_candles` exist
- **THEN** Favorites analysis can still render the saved candles as fallback
- **AND** the failure does not trigger favorite metric regeneration by itself

#### Scenario: Protected common user opens favorite analysis
- **WHEN** a common user opens a protected favorite analysis
- **THEN** the result chart uses current market candles when available
- **AND** the view does not show moving average overlays, moving average values, indicators, or protected parameters
