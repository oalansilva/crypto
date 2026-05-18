## Why

Favorites analysis can have full saved candle history, but the chart currently prefers the current market-candles response limited to a recent window. Long-running favorites therefore open with only partial history even when the saved favorite contains the full backtest chart context.

## What Changes

- Update Favorites analysis candle selection to use the most complete available candle series.
- Keep current market candles as the freshness source when they are at least as complete as saved chart context.
- Preserve saved trades and metrics as the evidence source for the analysis view.
- Add focused Playwright coverage for a long-history favorite.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `favorites`: Favorites analysis chart must preserve full saved candle history when it is longer than the current market-candles window.

## Impact

- `frontend/src/pages/FavoritesDashboard.tsx`
- `frontend/tests/e2e/favorites-view-results.spec.ts`
- OpenSpec delta for `favorites`
