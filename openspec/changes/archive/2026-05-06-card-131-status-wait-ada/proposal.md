## Why

ADA/USDT can appear as `WAIT` in the Monitor even when the strategy has an active entry, because the list resolution can mix the card display timeframe with the strategy timeframe. The chart candles endpoint can also serve persisted daily candles that are already behind the current crypto market bucket.

## What Changes

- Resolve Monitor list sections from the strategy decision timeframe, not from the card price timeframe preference.
- Keep timeframe mismatch review behavior for the chart modal when the displayed chart timeframe differs from the strategy timeframe.
- Tighten persisted candle freshness so the chart endpoint refreshes from the live crypto provider when stored candles lag behind the current expected bucket.
- Add regression coverage for ADA-like HOLD resolution and stale daily candles.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `monitor`: Monitor list section resolution must use the backend strategy decision state consistently.
- `monitor-chart-fresh-candles`: Persisted candle freshness must reject daily crypto candles that lag behind the current market bucket.
- `opportunity-monitor`: HOLD/WAIT status must remain consistent when a strategy has a confirmed active entry and fresh candles.

## Impact

- Backend `/api/market/candles` persisted freshness logic.
- Monitor list grouping in `MonitorStatusTab`.
- Backend integration tests and frontend Playwright tests for the affected Monitor behavior.
