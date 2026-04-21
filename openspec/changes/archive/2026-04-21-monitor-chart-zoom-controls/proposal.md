## Why

The Monitor chart already helps the trader inspect a strategy, but the current view does not offer explicit zoom controls for focusing on shorter or longer candle windows. This makes detailed analysis slower, especially when the user wants a TradingView-like navigation pattern without leaving `/monitor`.

## What Changes

- Add explicit zoom-in and zoom-out controls to the strategy chart shown from `/monitor`.
- Define how zoom controls affect the visible candle range while preserving existing chart interactions and timeframe switching.
- Keep the scope limited to chart navigation in the Monitor flow; no new drawing tools, no full TradingView clone, and no backend data model changes are required by this proposal.

## Capabilities

### New Capabilities

- `monitor-chart-zoom-controls`: User-facing zoom controls for the strategy chart opened from the Monitor screen.

### Modified Capabilities

- `opportunity-monitor`: The Monitor experience now includes direct chart zoom actions when viewing a strategy chart.
- `chart-visualization`: Chart behavior requirements now include explicit zoom-in and zoom-out controls for supported chart surfaces.

## Impact

- Affected frontend code in the Monitor chart/modal components and chart toolbar behavior.
- Likely touches shared chart rendering logic if the Monitor chart reuses a common wrapper.
- No API contract or persistence changes are expected for the initial implementation.
