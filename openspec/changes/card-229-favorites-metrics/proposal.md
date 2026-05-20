## Why

Alan identified that percentage metrics in Favorites may be too high. The likely failure mode is duplicate conversion between fraction and percentage values before a strategy is saved and later displayed in Favorites.

## What Changes

- Normalize Favorites performance metrics by field semantics, not by loose magnitude only.
- Treat backend `total_return_pct` and `total_pnl_pct` as percentage-point values when saving optimized results.
- Keep ratio fields such as `total_return`, `win_rate`, `max_drawdown`, and stop-loss values converted to percent only at display time.
- Add focused evidence that Favorites displays a backend percentage payload without multiplying it by 100 again.

## Capabilities

### New Capabilities

### Modified Capabilities
- `favorites`: Favorites metric display and persisted favorite metrics must avoid duplicate percentage conversion.

## Impact

- Frontend optimization result metric normalization.
- Favorites table/card/export/compare display semantics.
- Playwright coverage for Favorites percentage rendering.
