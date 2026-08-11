## Why

Favorite backtests can remain stale even when canonical candles are current because the automatic refresh worker is optional and currently starts disabled by default. This card needs a durable daily refresh strategy that protects the VPS from sustained CPU pressure while keeping saved favorites fresh.

## What Changes

- Persist and expose a daily favorite backtest refresh routine that can run after restarts.
- Add configurable CPU guardrails so refresh work pauses instead of exceeding a 60% sustained CPU ceiling.
- Add batch sizing and pause controls so all due favorites can be spread across a daily cycle.
- Record operational state for refresh cycles, including skipped or paused work, without blocking other favorites.
- Extend runtime status so operators can verify whether the refresh worker is enabled and when it last ran.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `favorite-backtest-refresh`: add daily scheduling, CPU guardrails, batched execution, and runtime observability requirements.

## Impact

- Backend runtime worker and favorite refresh service.
- Runtime status payload and startup environment defaults.
- Tests around favorite refresh selection, CPU throttling, and worker enablement.
