## ADDED Requirements

### Requirement: Monitor chart hides technical indicators
The Monitor chart modal SHALL render user-facing charts without visible technical indicator overlays, indicator toggle controls, or indicator legend entries. The chart MUST continue showing candlesticks and Compra/Venda signal markers.

#### Scenario: User opens Monitor chart
- **WHEN** the user opens a chart from `/monitor`
- **THEN** the chart SHALL NOT display EMA, SMA, or other technical indicator overlay lines
- **AND** the chart toolbar SHALL NOT expose indicator toggle controls
- **AND** the footer legend SHALL NOT list indicator names
- **AND** Compra/Venda markers SHALL remain visible when signal data is available

#### Scenario: Chart context remains available
- **WHEN** the user opens a chart from `/monitor`
- **THEN** timeframe controls, zoom controls, candle values, risk context, and signal history SHALL remain available where applicable
