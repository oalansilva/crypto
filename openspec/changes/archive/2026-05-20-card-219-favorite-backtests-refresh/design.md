## Context

Favorites already store strategy parameters, metrics, trades, chart context, and period metadata. Missing trade/chart history can be regenerated through the combo optimizer, and `AutoBacktestRun` already exists as a durable execution log.

Card 219 adds a product-internal daily refresh. The refresh must not block users and must make stale state visible.

## Design

### Refresh service

Add `FavoriteBacktestRefreshService` with two levels:

- `refresh_favorite(favorite_id)` refreshes one favorite and records success/failure.
- `run_due_refreshes()` selects due favorites and refreshes them sequentially.

A favorite is due when it has never completed a refresh or its last completed refresh is older than `FAVORITE_BACKTEST_REFRESH_INTERVAL_SECONDS` (default 86400 seconds). A recent `RUNNING` refresh is skipped to avoid duplicate work. A stale `RUNNING` row can be retried after the interval.

The service reuses the same `ComboOptimizer.run_optimization` pathway used by favorite trade regeneration. It fixes custom ranges from saved parameters so the daily job validates the saved strategy instead of searching new parameters. The job uses the favorite start date and current date as the end date so the result includes the latest available candles.

### Persistence

Add status fields to `favorite_strategies`:

- `auto_refresh_status`
- `auto_refresh_error`
- `auto_refresh_started_at`
- `auto_refresh_completed_at`
- `auto_refresh_run_id`

Each attempt also creates an `AutoBacktestRun` linked to the favorite. Success writes refreshed metrics/trades/chart data to `FavoriteStrategy.metrics`; failure records the error and leaves previous metrics available.

### Runtime worker

`runtime_worker` starts the refresh loop when `RUN_FAVORITE_BACKTEST_REFRESH` is enabled (default enabled). The loop runs once at startup, then waits the configured interval. Shutdown cancels the loop cleanly.

### API/UI

Favorites API includes the refresh fields in `FavoriteStrategyResponse`. The Favorites screen shows a compact refresh status line on desktop and mobile. Protected strategy redaction remains unchanged; refresh metadata is not secret.

## Risks

- Long-running favorite catalogs can take time. The first implementation runs sequentially and caps nothing by default; `FAVORITE_BACKTEST_REFRESH_MAX_FAVORITES` can limit a run operationally.
- Combo optimizer failures must not break the whole loop. Each favorite is isolated and failure state is persisted.
