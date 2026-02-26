# monitor-candles-async-ui Specification

## Purpose
TBD - created by archiving change monitor-candles-async-ui. Update Purpose after archive.
## Requirements
### Requirement: Timeframe switching is non-blocking and optimistic
The system MUST allow switching the candlestick timeframe without blocking the overall Monitor card UI.

#### Scenario: Selection updates immediately
- **WHEN** the user taps a timeframe button on a symbol card
- **THEN** the selected timeframe state updates immediately in the UI

#### Scenario: Card remains interactive while loading
- **WHEN** the candles request is in progress after a timeframe switch
- **THEN** non-chart controls on the card remain usable (e.g., toggles for Portfolio and Price/Strategy)

### Requirement: Chart shows localized loading feedback
The system MUST provide a loading indicator localized to the chart area when candle data is being fetched.

#### Scenario: Chart loading indicator appears
- **WHEN** the system starts fetching candles for a symbol/timeframe
- **THEN** the chart area shows a loading indicator

#### Scenario: Loading indicator disappears on completion
- **WHEN** candle data is successfully loaded or an error is shown
- **THEN** the chart loading indicator is removed

### Requirement: In-flight candle requests are cancelled on new selection
The system MUST cancel any in-flight candle fetch request for a symbol when the user selects a new timeframe.

#### Scenario: Last click wins
- **WHEN** the user rapidly selects multiple timeframes for the same symbol
- **THEN** only the last selected timeframe request is allowed to complete and render

### Requirement: Client-side candle cache reduces repeat latency
The system MUST cache candle results in memory by `symbol+timeframe` to improve responsiveness.

#### Scenario: Cached candles render instantly
- **WHEN** the user returns to a previously loaded timeframe for a symbol
- **THEN** the system renders cached candles immediately while optionally refreshing in the background

