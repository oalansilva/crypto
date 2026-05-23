## Context

Card 241 established `market_ohlcv` as the canonical candle store and added a one-shot writer command. Card 242 makes that runtime model operable: the API and UI remain the lightweight default stack, while candle writing, backfill, realtime prices, generic runtime routines, and Celery are explicit optional services with status evidence.

Current constraints:

- `start.sh` already defaults heavy workers off, but the FastAPI lifespan still calls non-critical startup helpers and relies on each helper to no-op.
- `backend/scripts/run_canonical_candle_writer_once.py` runs the canonical writer path but has no cross-process lock or persisted last-run status.
- `ops/systemd/crypto-stack.service` installs only the stack bootstrap.
- `/api/health` is too shallow to prove runtime topology, worker defaults, writer state, or candle freshness.

## Goals / Non-Goals

**Goals:**

- Keep default `./start.sh` economical: Redis, migrations, backend API, frontend UI, and no heavy workers unless flags opt in.
- Promote the canonical candle writer to a named systemd user service/timer template without making it part of default stack boot.
- Add a single lock around the candle writer command so manual runs and timer runs cannot fetch Binance candles concurrently.
- Persist the latest candle writer run summary in a safe local JSON state file.
- Expose a runtime status endpoint showing safe flag state, candle writer lock/state, and canonical candle metrics.
- Document startup order, flags, service ownership, logs, and runbook commands.

**Non-Goals:**

- Archive card 241 OpenSpec artifacts.
- Rebuild all candle consumers or strategy calculations.
- Enable Celery, runtime worker, realtime prices, backfill, or candle writer by default.
- Install or enable systemd units during tests or implementation.

## Decisions

- Add `backend/app/services/runtime_status.py` as the read-only runtime status boundary. It centralizes safe boolean flag parsing, candle writer paths, lock inspection, last-run state reading, and payload creation for `/api/runtime/status`.
- Keep `/api/health` unchanged and add `/api/runtime/status` for deeper operational evidence. This avoids changing existing health checks while giving operators a richer proof endpoint.
- Make `_start_noncritical_services()` explicitly check `MARKET_OHLCV_INGESTION_ENABLED`, `CRYPTO_CANDLES_WRITER_ENABLED`, `BINANCE_REALTIME_ENABLED`, and `BACKFILL_SCHEDULER_ENABLED` before calling heavy helpers. This reduces conceptual coupling in FastAPI startup even when helper defaults are safe.
- Use POSIX `fcntl.flock` in `run_canonical_candle_writer_once.py` with `CRYPTO_CANDLES_WRITER_LOCK_FILE` defaulting to `/tmp/crypto-candle-writer.lock`. The writer exits successfully when another writer is active, prints a clear skip message, and does not start a second Binance fetch path.
- Persist writer state to `CRYPTO_CANDLES_WRITER_STATE_FILE`, default `/tmp/crypto-candle-writer-state.json`, with timestamps, status, pid, run count, duration, and error summary. The state file is operational evidence, not a source of secrets.
- Add `ops/systemd/crypto-candle-writer.service` and `ops/systemd/crypto-candle-writer.timer` templates plus an installer script. The timer is opt-in and separate from `crypto-stack.service`.
- Document the current VPS runtime model in `docs/runtime-architecture.md` and link it from `docs/project-hub.md`.

## Risks / Trade-offs

- [Risk] `/api/runtime/status` may expose internal paths. -> Mitigation: only expose local file paths and booleans, not secrets, DSNs, tokens, process command lines, or raw env values.
- [Risk] A stale lock file may look concerning. -> Mitigation: `flock` checks the actual advisory lock; a stale file without a held lock reports `lock_held=false`.
- [Risk] Systemd templates can drift from `start.sh`. -> Mitigation: templates call repo scripts directly and docs list the same flags used by `start.sh`.
- [Risk] Disabling FastAPI non-critical helper calls unless flags opt in may surprise an operator relying on implicit `.env` behavior. -> Mitigation: card 241 already made safe defaults explicit; card 242 documents exact opt-in flags and keeps helper functions available.

## Migration Plan

1. Deploy code and docs with default flags unchanged.
2. Run `./restart` to prove API/UI still start without heavy workers.
3. Validate `/api/runtime/status` shows heavy workers disabled and canonical mode enabled.
4. Install the candle writer timer only when the operator wants scheduled catch-up:
   `./install-candle-writer-systemd-user-timer.sh`.
5. Roll back by disabling the timer and reverting to manual one-shot writer runs.

## Open Questions

- The final timer cadence can be tuned after observing Binance rate limits and symbol universe size on the VPS. The initial template uses a conservative interval and remains opt-in.
