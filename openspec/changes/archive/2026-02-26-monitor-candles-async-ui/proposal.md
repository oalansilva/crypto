## Why

The Monitor card candlestick chart timeframe switch can feel like it freezes the UI, especially on mobile, because the chart fetch can take time.

We want a more responsive UX: timeframe changes should be optimistic, non-blocking, and provide clear loading feedback while data loads asynchronously.

## What Changes

- Make timeframe switching on Monitor cards non-blocking and optimistic.
- Show a small loading indicator only on the chart area (not the entire card).
- Cancel in-flight candle fetch requests when a new timeframe is selected (last-click wins).
- Add an in-memory client-side cache by `symbol+timeframe` to instantly render recently fetched candles.

## Capabilities

### New Capabilities
- `monitor-candles-async-ui`: Responsive, non-blocking candles UX for Monitor cards.

### Modified Capabilities
- `frontend-ux`: Improve mobile UX for the Monitor price chart interactions.

## Impact

- Frontend: `OpportunityCard` candle loading state, request cancellation, and cache.
- No backend changes expected.
- Tests: Update Playwright E2E to assert that switching timeframe does not block interactions and that loading indicators appear.
