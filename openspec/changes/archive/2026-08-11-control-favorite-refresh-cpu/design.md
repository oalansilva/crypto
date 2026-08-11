## Context

The favorite refresh service already knows how to rerun a saved favorite, persist metrics, and write `auto_backtest_runs`. The production issue is operational: the runtime worker starts disabled by default, all 184 favorites have never completed auto-refresh, and a naive enablement could run many deep backtests at once or for too long.

The implementation must preserve the current single-favorite refresh semantics while adding a daily, throttled scheduler around it.

## Goals / Non-Goals

**Goals:**

- Make favorite refresh enabled by default in the repo startup path.
- Bound each cycle with configurable batch size, per-favorite pause, and CPU ceiling.
- Pause/back off when sustained CPU is above 60% by default.
- Expose recent cycle state through runtime status without adding a new public management UI.
- Keep per-favorite failures isolated.

**Non-Goals:**

- Replace the optimizer or deep backtest algorithm.
- Guarantee all 184 current favorites finish in one process start if CPU/data provider limits require multiple cycles.
- Add a new user-facing control surface.
- Solve missing market data for symbols with no persisted candles.

## Decisions

- **Use the existing runtime worker loop.** It already owns background operational routines and is visible through `/api/runtime/status`. Alternative: system cron. Cron would be simpler, but it would bypass existing worker status and shutdown handling.
- **Throttle inside `FavoriteBacktestRefreshService.run_due_refreshes`.** This keeps selection, refresh, error isolation, and audit logic in one service. Alternative: wrap from `runtime_worker`; that would duplicate batching decisions outside the service.
- **Use host load samples from `psutil` when available, with `os.getloadavg` fallback.** `psutil.cpu_percent()` is the clearest process-independent CPU signal. The fallback keeps tests/runtime usable if the optional dependency is absent.
- **Persist cycle state in a small JSON runtime file.** Database schema changes are unnecessary for operational loop status, and runtime status can sanitize/read this file the same way candle writer state is handled.
- **Separate due age from loop cadence.** `FAVORITE_BACKTEST_REFRESH_INTERVAL_SECONDS=86400` keeps daily freshness semantics, while `FAVORITE_BACKTEST_REFRESH_LOOP_SECONDS=3600` lets small batches progress through all due favorites during the day. Operators can raise the batch or lower the loop interval after observing CPU.

## Risks / Trade-offs

- **[Risk] A small batch may not refresh every favorite in one day.** Mitigation: expose due/success/failed/skipped counts and allow env tuning for batch size and interval.
- **[Risk] CPU sampling is host-level and not exact per-process usage.** Mitigation: use it as a conservative throttle; keep limits configurable.
- **[Risk] Missing candles create repeated failed attempts.** Mitigation: preserve existing per-favorite failure isolation and clear error messages.
- **[Risk] Enabling the worker can increase backend workload after restart.** Mitigation: start with initial delay, CPU guard, one-at-a-time execution, and small batch defaults.
