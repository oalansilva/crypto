## ADDED Requirements

### Requirement: Strategy chart applies default viewport once after data settles
Shared strategy charts SHALL apply the default visible range at most once per viewport reset key after the host signals that candle loading has settled. Intermediate candle-count changes for the same key MUST NOT reapply `fitContent` or the default 180-bar range.

#### Scenario: Monitor chart stages market then analysis candles
- **WHEN** the Monitor chart modal opens and candle payloads arrive in stages for the same symbol/timeframe
- **THEN** analysis loading SHALL be pending from the first render until the analysis request settles
- **AND** the default visible range SHALL be applied once after loading settles
- **AND** later merges with a different candle count SHALL preserve the current viewport unless the user changes timeframe/symbol or resets zoom

#### Scenario: Monitor panels resize while loading
- **WHEN** asynchronous chart and strategy panels render on a desktop viewport
- **THEN** the chart canvas SHALL keep a bounded viewport-relative height
- **AND** content reflow MUST NOT cause an apparent zoom or viewport reset

#### Scenario: Analysis request does not settle
- **WHEN** the analysis request exceeds its bounded timeout
- **THEN** the Monitor SHALL release the pending viewport state
- **AND** it SHALL render the available fallback candles/trades without leaving the chart permanently unready

### Requirement: Wheel zoom is limited to the chart canvas
Mouse-wheel zoom SHALL only activate when the pointer is over the candlestick chart canvas, not when scrolling adjacent strategy detail panels inside the same shell.

#### Scenario: User scrolls strategy transparency under the chart
- **WHEN** the user scrolls over the strategy transparency/details section
- **THEN** the chart visible range MUST NOT change due to that wheel gesture
