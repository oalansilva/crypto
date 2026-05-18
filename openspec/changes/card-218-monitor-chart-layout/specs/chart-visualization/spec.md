## MODIFIED Requirements

### Requirement: Monitor chart preserves interaction controls in strategy layout
The Monitor chart surface SHALL preserve explicit zoom controls, wheel zoom, candle count, signal markers and chart rendering when the layout is restyled as a strategy-detail modal.

#### Scenario: User interacts with redesigned Monitor chart
- **WHEN** the user opens the redesigned Monitor chart modal
- **THEN** the chart SHALL expose zoom in, zoom out and reset controls
- **AND** wheel zoom SHALL keep working inside the chart shell
- **AND** visible candle count SHALL update from the chart logical range.

#### Scenario: Signal history exists
- **WHEN** the opportunity has signal history matching the displayed timeframe
- **THEN** the chart SHALL render aligned buy/sell markers
- **AND** the side context SHALL list recent signals without replacing marker behavior.
