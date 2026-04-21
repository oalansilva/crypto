# monitor-chart-zoom-controls Specification

## Purpose
TBD - created by archiving change monitor-chart-zoom-controls. Update Purpose after archive.
## Requirements
### Requirement: Explicit zoom controls are available in the Monitor strategy chart
The system SHALL provide visible zoom-in and zoom-out controls when the user opens a strategy chart from the Monitor screen.

#### Scenario: User sees zoom controls in chart modal
- **WHEN** the user opens a strategy chart from `/monitor`
- **THEN** the chart toolbar shows dedicated zoom-in and zoom-out controls

#### Scenario: Controls are only shown where zoom is supported
- **WHEN** the user is viewing the expanded strategy chart surface
- **THEN** the zoom controls are available on that chart surface without requiring mouse wheel or trackpad gestures

### Requirement: Zoom controls adjust the visible candle range predictably
The system SHALL change the visible logical range of the strategy chart in consistent steps when the user activates zoom-in or zoom-out.

#### Scenario: Zoom in reduces the visible window
- **WHEN** the user activates zoom-in once
- **THEN** the chart shows fewer candles than before while keeping the current focal region visible

#### Scenario: Zoom out expands the visible window
- **WHEN** the user activates zoom-out once
- **THEN** the chart shows more candles than before without losing chronological ordering

### Requirement: Zoom controls preserve chart context
The system MUST keep the selected timeframe, loaded candles, and visible overlays intact when zoom controls are used.

#### Scenario: Indicators remain visible after zoom
- **WHEN** the user zooms the chart after enabling or disabling indicators
- **THEN** the active indicators remain in their current visible state

#### Scenario: Timeframe selection is preserved after zoom
- **WHEN** the user changes timeframe and then uses zoom controls
- **THEN** the chart remains on the selected timeframe and does not reload solely because of the zoom action

