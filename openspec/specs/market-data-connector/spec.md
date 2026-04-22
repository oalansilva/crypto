# market-data-connector Specification

## Purpose
TBD - created by archiving change 2026-04-22-binance-realtime-price-connector. Update Purpose after archive.
## Requirements
### Requirement: Discover top 100 Binance pairs with REST
The system SHALL determine and maintain a top-100 list of Binance pairs using REST data, and update it on a schedule without operator input.

#### Scenario: Initial discovery
- **WHEN** the connector starts
- **THEN** the system SHALL fetch exchange statistics from Binance REST endpoint(s)
- **AND** derive the top 100 liquid pairs by `quoteVolume` on `USDT`
- **AND** persist this list for stream subscription
- **AND** expose the active list through an internal API or status structure

#### Scenario: Periodic refresh
- **WHEN** the refresh timer elapses
- **THEN** the system SHALL recompute the top-100 list
- **AND** if the list changes
- **THEN** update subscribed streams to match the new set

### Requirement: Real-time WebSocket price ingestion
The system SHALL consume WebSocket streams for all active top-100 pairs and process the latest price fields in near real-time.

#### Scenario: Stream bootstrap
- **WHEN** the connector has a valid top-100 list
- **THEN** it SHALL establish a combined Binance stream subscription for all pairs
- **AND** the stream SHALL include bid, ask, close, event time, and exchange event time where available

#### Scenario: Price update publication
- **WHEN** a tick/message arrives for a subscribed pair
- **THEN** the system SHALL update an internal cache entry for that pair with the latest values
- **AND** emit the updated record via service API/state query path used by downstream modules

### Requirement: Automatic reconnection and resync
The system SHALL recover from WebSocket interruptions automatically, with state reconciliation after reconnect.

#### Scenario: Automatic reconnect on network failure
- **WHEN** the WebSocket closes unexpectedly or heartbeat is missed
- **THEN** the connector SHALL attempt reconnect with exponential backoff and jitter
- **AND** continue retrying with bounded delay until reconnected or manually stopped

#### Scenario: Recovery consistency
- **WHEN** a reconnect succeeds
- **THEN** the connector SHALL refresh top pairs from REST and resubscribe when needed
- **AND** reconcile the cached prices by requesting a REST snapshot/last-trade or ticker endpoints before resuming incremental updates

### Requirement: Respect Binance rate limiting
The system SHALL enforce request budgets for all REST calls and avoid hitting exchange rate caps.

#### Scenario: Budget control
- **WHEN** the service schedules REST calls
- **THEN** it SHALL check local token budget before executing each call
- **AND** defer/delay calls until budget recovery when needed

#### Scenario: Rate-limit response handling
- **WHEN** Binance returns rate-limit related HTTP errors or headers
- **THEN** the system SHALL honor retry hints / server guidance
- **AND** reduce request frequency according to policy

### Requirement: Latency budget target (< 200ms)
The system SHALL keep message ingestion low-latency for real-time prices.

#### Scenario: Ingestion latency
- **WHEN** a WebSocket price event is received
- **THEN** the system SHALL process the event and update in-memory state within 200ms for the rolling `p95` at normal load
- **AND** this metric SHALL be tracked via logging/metrics counters.

### Requirement: Observability and health
The system SHALL expose operational health for monitoring and debugging.

#### Scenario: Health report
- **WHEN** internal health is queried
- **THEN** it SHALL return last successful REST sync time, WS uptime, reconnect attempts, active subscribed count, and current rate-limit status

### Requirement: API for latest prices
The system SHALL expose an endpoint for downstream readers to retrieve the latest cached prices for subscribed pairs.

#### Scenario: Fetch latest prices
- **WHEN** a client calls the latest-price endpoint
- **THEN** it SHALL return a list or map with one record per subscribed pair and the last seen timestamp

