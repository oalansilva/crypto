# Why

The system currently relies on ad-hoc pricing calls and periodic polling for market data, which introduces stale values and inconsistent coverage across data providers. A dedicated Binance real-time connector is required to provide continuously updated prices for the top trading pairs and enable latency-sensitive monitoring/decisioning features.

# What Changes

- Add a market-data connector service for Binance that combines:
  - REST ingestion to continuously discover top pairs.
  - WebSocket streams for real-time price updates.
- Add operational resilience:
  - automatic reconnection
  - heartbeat/keepalive recovery
  - REST/WebSocket synchronization after reconnect
- Add transport control and governance:
  - exchange rate-limit enforcement
  - request budget tracking
  - bounded retry policy and fallback behavior
- Add monitoring and validation:
  - end-to-end ingestion latency tracking
  - stream health and pair refresh status

# Capabilities

## New Capabilities
- `binance-market-discovery`: discover and periodically refresh the top 100 USDT pairs from Binance exchange metadata.
- `binance-websocket-realtime-prices`: subscribe to Binance live price channels for those pairs and emit latest ticks with low-latency processing.
- `binance-connector-resilience`: auto-recover WebSocket connections and reconcile state from REST after failure or desync.
- `binance-rate-limit-control`: respect Binance REST/WebSocket public limits through token-bucket and adaptive backoff.

## Modified Capabilities
- `market-data-api`: add endpoints to read latest real-time price cache by symbol and connector health metadata.

# Impact

- Affected code: new backend service module for Binance connector, optional background scheduler integration, and market data API routes.
- Data model impact: in-memory latest-price cache and optional short-lived snapshots table/file for diagnostics.
- Operational impact: new runtime task and background worker requiring secrets/config for Binance base URLs, timeout/retry parameters, and rate budget.
- Security impact: protect connector endpoints (if exposed publicly) with existing service-level auth policy and safe handling of network failures.
