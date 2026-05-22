## Why

Crypto runtime currently has multiple Binance candle fetch paths. Backend startup can trigger OHLCV ingestion/backfill, runtime workers can build signal snapshots and refresh favorites, and API consumers can call market data providers directly. That creates duplicate Binance traffic, CPU spikes, cache divergence, and unclear rate-limit ownership.

## What Changes

- Introduce a canonical Binance candle boundary backed by `market_ohlcv`.
- Scope the default canonical candle writer/backfill to `15m` and `1d` candles for the current operating need.
- Make the canonical writer incremental: first population can fetch a larger lookback, then subsequent runs fetch from the last saved candle to the current moment and accumulate.
- Add a one-shot canonical writer command so operators can populate/catch up `15m` and `1d` without enabling the old worker stack.
- Make normal backend startup safe by disabling OHLCV ingestion/backfill unless explicitly enabled.
- Gate runtime worker routines so they do not all start by default.
- Route primary API candle reads through the canonical store and block direct Binance fetches in strict canonical mode.
- Keep explicit ingestion/backfill workers as the only runtime path allowed to fetch Binance candles.

## Capabilities

### Modified Capabilities

- `market-candles`: candle consumers must read persisted Binance candles from the canonical store by default and only request/fallback to direct fetch when explicitly allowed.
- `crypto-runtime`: normal service boot must not start multiple Binance candle fetch loops.

## Impact

- `backend/app/services/canonical_candle_service.py`
- `backend/app/main.py`
- `backend/app/workers/runtime_worker.py`
- `backend/app/api.py`
- `backend/app/services/ohlcv_storage.py`
- `backend/app/services/ohlcv_backfill_service.py`
- `backend/scripts/run_canonical_candle_writer_once.py`
- `start.sh`
- focused backend tests
