## Why

The Crypto stack now has canonical candle storage, but runtime ownership is still hard to operate because API, UI, candle writer, backfill, realtime prices, runtime worker, and Celery are controlled through mixed startup paths and scattered flags. Card 242 makes the runtime model explicit and economical so normal boot stays light and Binance candle collection has one named, observable owner.

## What Changes

- Define a clear runtime topology for the Crypto stack: Postgres, Redis, backend API, frontend UI, dedicated candle writer, optional historical backfill, optional realtime price worker, optional runtime routines, and optional Celery batch worker.
- Add a dedicated candle writer service/timer contract around the existing canonical writer path, including safe defaults, logs, anti-duplicate locking, and operator commands.
- Add machine-checkable runtime status/health evidence for worker enablement, writer lock state, canonical candle freshness, and optional service state.
- Document startup order, service responsibility, flags, logs, and operator runbook in local project docs.
- Preserve safe defaults: backend/UI start without worker autostart; heavy workers remain opt-in.

## Capabilities

### New Capabilities
- `crypto-runtime-architecture`: runtime service boundaries, startup policy, dedicated candle writer operation, health/status evidence, and operator runbook.

### Modified Capabilities

## Impact

- `start.sh`
- `backend/app/main.py`
- `backend/app/api.py`
- `backend/app/services/canonical_candle_service.py`
- `backend/app/services/ohlcv_storage.py`
- `backend/app/services/ohlcv_backfill_service.py`
- `backend/scripts/run_canonical_candle_writer_once.py`
- new runtime/status script or endpoint if needed
- `docs/`
- focused backend tests and script/startup checks
