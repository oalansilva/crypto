## ADDED Requirements

### Requirement: Monitor includes tabs for Status and Dashboard
The UI MUST provide tabs on the Monitor screen for switching between Status and Dashboard.

#### Scenario: Tabs are visible
- **WHEN** the user opens the Monitor screen
- **THEN** the UI shows tabs labeled Status and Dashboard

#### Scenario: Switching tabs updates the view
- **WHEN** the user switches from Status to Dashboard (or vice versa)
- **THEN** the visible content changes to the selected tab

### Requirement: Favorites-only dataset is used
The UI MUST use only the Favorites dataset for the dashboard.

#### Scenario: No non-favorite symbols appear
- **WHEN** the dashboard renders
- **THEN** only favorites appear in the dashboard list

### Requirement: Candlestick chart uses a consistent visual language
The UI MUST render a candlestick chart with clear up/down candle colors and readable axes.

#### Scenario: Candle colors represent direction
- **WHEN** candles are rendered
- **THEN** bullish candles use one color and bearish candles use another color

#### Scenario: Chart remains usable on small screens
- **WHEN** the chart is rendered on a small viewport
- **THEN** labels do not overlap excessively and the user can still interpret the trend
