# Tasks: Binance Real-Time Connector

## 1. Discovery and API configuration

- [ ] 1.1 Create `backend/app/services/market_data/binance/` package for connector implementation and configuration constants.
- [ ] 1.2 Add configuration entries for Binance REST/WS base URLs, refresh intervals, top-pairs window, and rate-budget parameters.
- [ ] 1.3 Implement typed settings + validation (`pydantic`/existing config system) for connector limits and timeout/retry behavior.

## 2. REST ingestion (top pairs)

- [ ] 2.1 Implement REST client with timeout, retry, and signed/unsigned request support for public endpoints.
- [ ] 2.2 Implement top-pairs selector:
  - fetch weighted symbols/tickers
  - filter to `USDT` pairs
  - sort by volume and keep top 100
  - persist snapshot in internal cache/state.
- [ ] 2.3 Add scheduled refresh job that re-evaluates top pairs every configured interval.
- [ ] 2.4 Add structured logs for pair-refresh latency, top-pair delta count, and refresh failures.

## 3. Rate limiting

- [ ] 3.1 Implement token-bucket budget manager for REST calls.
- [ ] 3.2 Honor rate-limit headers and `Retry-After`/429 responses by scheduling delayed retries.
- [ ] 3.3 Add alert log when budget usage reaches warning/critical thresholds.

## 4. WebSocket ingestion

- [ ] 4.1 Implement stream manager that subscribes to a combined stream for current top-100 pairs.
- [ ] 4.2 Add message parser for bid/ask/close + event times and map results into normalized internal price records.
- [ ] 4.3 Implement in-memory latest-price cache keyed by symbol with TTL and last-update timestamp.
- [ ] 4.4 Add `GET /api/market/binance/prices/latest` endpoint returning latest cache by symbol (or paged list).

## 5. Automatic reconnection and recovery

- [ ] 5.1 Add heartbeat/miss detection for stream inactivity and error handling for close frames.
- [ ] 5.2 Implement reconnect flow with exponential backoff + jitter and bounded max attempts.
- [ ] 5.3 On reconnect success, force REST re-sync and optional stream resubscription if top pairs changed.
- [ ] 5.4 Add reconnect history counters (attempts, success latency, last-reconnect reason).

## 6. Latency and quality gates

- [ ] 6.1 Record per-event receive and process timestamps to compute `event_to_cache_ms`.
- [ ] 6.2 Expose metrics for `p95(event_to_cache_ms)` and `p99(event_to_cache_ms)`.
- [ ] 6.3 Add monitoring endpoint or status payload with:
  - latest REST sync time
  - WS connection state
  - pair count
  - reconnect counters
  - current budget state.

## 7. Validation

- [ ] 7.1 Add integration tests for:
  - top-100 refresh
  - websocket cache update
  - reconnection workflow
  - rate-limit backoff behavior.
- [ ] 7.2 Add smoke test/protocol check that verifies API returns at least one subscribed pair and valid latest timestamp.
- [ ] 7.3 Run focused checks after implementation and document observed latency/latency percentile in change notes.
