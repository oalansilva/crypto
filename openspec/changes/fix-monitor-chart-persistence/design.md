## Context

The Monitor chart modal uses `StrategyChartSurface`, a shared lightweight-charts wrapper. The current chart effect creates the chart and also applies candles, markers, price lines, visible-range subscriptions, and tooltip handlers. Because that effect depends on arrays derived from async state, routine updates can remove and recreate the chart after the modal has already opened.

## Goals / Non-Goals

**Goals:**
- Keep the chart instance mounted while candles, markers, price lines, and tooltip maps update.
- Preserve current zoom controls, wheel zoom, marker rendering, volume series, and side-panel tooltip behavior.
- Validate with a real browser against `/monitor`.

**Non-Goals:**
- Change Monitor opportunity classification, backend candle APIs, favorite logic, or TradingView export behavior.
- Add new chart modes or visual redesign.

## Decisions

- Split chart lifecycle from data updates. Create chart, series, subscriptions, and cleanup in a mount-time effect keyed only by DOM readiness and callbacks that are stable enough for lifecycle ownership.
- Store the candle and volume series refs so later effects can call `setData`, `setMarkers`, and recreate price lines without removing the chart container.
- Preserve default visible range when candle count changes, but avoid resetting the chart just because marker/trade context arrives.
- Keep the DOM/test IDs unchanged so existing E2E checks and public Monitor validation remain compatible.

## Risks / Trade-offs

- Price line APIs require explicit cleanup. Mitigation: store created price line refs and remove them before applying the next set.
- Updating data separately from chart creation can leave stale tooltip handlers if not synchronized. Mitigation: read latest tooltip map from a ref inside the crosshair handler.
- A large candle-set change may still reset visible range intentionally. Mitigation: only reset through the data update effect when the candle series changes.
