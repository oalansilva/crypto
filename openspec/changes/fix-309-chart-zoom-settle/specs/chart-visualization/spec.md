## ADDED Requirements

### Requirement: Strategy chart applies default viewport once after data settles
Shared strategy charts SHALL apply the default visible range at most once per viewport reset key after the host signals that candle loading has settled. Intermediate candle-count changes for the same key MUST NOT reapply `fitContent` or the default 180-bar range.

#### Scenario: Monitor chart stages market then analysis candles
- **WHEN** the Monitor chart modal opens and candle payloads arrive in stages for the same symbol/timeframe
- **THEN** the default visible range SHALL be applied once after loading settles
- **AND** later merges with a different candle count SHALL preserve the current viewport unless the user changes timeframe/symbol or resets zoom

### Requirement: Wheel zoom is limited to the chart canvas
Mouse-wheel zoom SHALL only activate when the pointer is over the candlestick chart canvas, not when scrolling adjacent strategy detail panels inside the same shell.

#### Scenario: User scrolls strategy transparency under the chart
- **WHEN** the user scrolls over the strategy transparency/details section
- **THEN** the chart visible range MUST NOT change due to that wheel gesture
