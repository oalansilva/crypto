## Why

Favorite backtests can drift stale after market data changes. The product needs an internal daily routine that refreshes saved favorites so Favorites and Monitor consume recent metrics without requiring a user to reopen or regenerate each strategy manually.

## What Changes

- Add an internal favorite backtest refresh routine that runs from the backend worker.
- Refresh each due favorite by updating candles through the existing optimization path, rerunning the favorite's saved strategy configuration, recalculating metrics, and persisting trades/chart context.
- Persist last refresh status, timestamps, run id, and error per favorite.
- Record each refresh attempt in `auto_backtest_runs`.
- Expose refresh state in the Favorites API and show it on the Favorites screen.
- Do not add real-time per-candle refresh, alerts, full historical reruns for every strategy, or automatic parameter optimization.

## Capabilities

### New Capabilities
- `favorite-backtest-refresh`: Internal scheduled refresh for favorited strategy backtests.

### Modified Capabilities
- `favorites`: Favorites API and UI expose the last automatic refresh status for each strategy.

## Impact

- Backend models, runtime schema migration, Alembic migration, worker startup, and refresh service.
- Favorites API response schema and frontend Favorites dashboard display.
- Focused backend tests for refresh success/failure and worker startup wiring.
