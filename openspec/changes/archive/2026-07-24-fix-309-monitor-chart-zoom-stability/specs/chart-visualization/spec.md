## ADDED Requirements

### Requirement: Strategy chart viewport stays stable across async candle updates
Shared strategy chart surfaces SHALL apply the default visible range only on initial data for a given viewport reset key (symbol + timeframe, or equivalent). Subsequent candle/volume data updates for the same key MUST NOT reapply `fitContent` or the default 180-candle logical range.

#### Scenario: Monitor chart receives staged candle payloads after open
- **WHEN** the Monitor chart modal opens and candles update asynchronously (initial cache, market fetch, then analysis merge)
- **THEN** the visible logical range set on the first non-empty render for that symbol/timeframe SHALL remain unchanged by those later data updates
- **AND** the chart SHALL NOT appear to zoom in or out by itself.

#### Scenario: User changes timeframe or symbol
- **WHEN** the viewport reset key changes (symbol or timeframe)
- **THEN** the chart SHALL apply the default visible range again for the new key
- **AND** explicit zoom/reset controls SHALL continue to work.

### Requirement: Strategy chart wheel zoom applies a single scaling step
Wheel/trackpad zoom on shared strategy chart surfaces SHALL be handled by a single application path so one user gesture does not stack multiple zoom steps.

#### Scenario: User scrolls once over the chart shell
- **WHEN** the user performs one mouse-wheel or trackpad scroll gesture over the chart
- **THEN** the visible bar count changes by one intentional zoom step
- **AND** the chart library native mouse-wheel scale/scroll MUST be disabled to avoid double application
- **AND** explicit zoom-in/zoom-out/reset controls remain available.

## MODIFIED Requirements

### Requirement: Strategy chart default visible range
Strategy chart surfaces SHALL open focused on the latest 180 candles when enough candle history is available. That default SHALL apply on first render for a viewport reset key and on explicit zoom reset, not on every candle data refresh.

#### Scenario: Chart has more than 180 candles
- **WHEN** a shared strategy chart renders with more than 180 candles for a new viewport reset key
- **THEN** the initial visible range SHALL focus on the latest 180 candles
- **AND** zoom controls SHALL continue to adjust the visible range without fetching new candle data.

#### Scenario: Chart has 180 candles or fewer
- **WHEN** a shared strategy chart renders with 180 or fewer candles for a new viewport reset key
- **THEN** the chart SHALL show the available history without forcing an empty padded 180-candle range.

#### Scenario: Explicit zoom reset
- **WHEN** the user activates zoom reset
- **THEN** the chart SHALL restore the default visible range rules above for the current candle set.
