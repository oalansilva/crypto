## ADDED Requirements

### Requirement: Result charts follow Monitor chart style
Result chart surfaces used by Favorites analysis SHALL follow the Monitor chart visual and interaction pattern.

#### Scenario: Result chart renders operational surface
- **WHEN** a result chart renders candle history
- **THEN** it SHALL use a dark operational canvas with readable axes, grid, candle colors, and crosshair styling
- **AND** it SHALL include volume and moving average overlays where candle data is available

#### Scenario: Result chart supports explicit zoom
- **WHEN** a result chart renders candle history
- **THEN** it SHALL expose explicit zoom in, zoom out, and reset controls
- **AND** zoom actions SHALL update the visible candle range without fetching new candle data

#### Scenario: Result chart supports wheel zoom
- **WHEN** the user scrolls over the chart area
- **THEN** the chart SHALL zoom the visible candle range
- **AND** the page SHALL NOT scroll instead of zooming the chart
