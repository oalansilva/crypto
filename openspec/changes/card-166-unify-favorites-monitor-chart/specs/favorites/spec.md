## ADDED Requirements

### Requirement: Favorites analysis uses Monitor-aligned chart
The Favorites analysis result view SHALL use the same operational chart presentation pattern as the Monitor when candle history is available.

#### Scenario: Favorite analysis opens with candles
- **WHEN** an admin user clicks `Ver análise completa` for a favorite whose analysis has candle history
- **THEN** the result view SHALL render a Monitor-aligned candlestick chart
- **AND** the chart SHALL show readable candles, volume, trade markers, and moving average overlays
- **AND** the chart SHALL expose explicit zoom controls

#### Scenario: Favorite analysis opens without candles
- **WHEN** an admin user opens favorite analysis and no candles are available
- **THEN** the result view SHALL keep an empty chart state
- **AND** the rest of the analysis summary and trades SHALL remain accessible
