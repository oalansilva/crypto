## ADDED Requirements

### Requirement: Shared BTCUSDT bookTicker and aggTrade stream per process

The Farol process SHALL keep one shared WebSocket stream of Binance `bookTicker` and `aggTrade` for BTCUSDT, not one stream per user. Every user with the directional scalp ligado SHALL read the same in-process memory. The stream SHALL reuse `binance_realtime_connector` (reconnect, backoff) and SHALL NOT replace the existing top-pairs `@ticker` connector used by the rest of the Farol.

#### Scenario: Two users share one stream

- **WHEN** two authenticated users have the scalp ligado in the same Farol process
- **THEN** the process SHALL hold a single BTCUSDT `bookTicker` + `aggTrade` stream
- **AND** SHALL NOT open a second stream for the second user

#### Scenario: Existing Farol ticker connector stays

- **WHEN** this scalp stream is running
- **THEN** the rest of the Farol SHALL keep using the existing `@ticker` connector
- **AND** this change SHALL NOT swap that connector out

### Requirement: Cycle reads touch and a short trade window from memory

With the scalp ligado, each cycle SHALL read the touch (bid, ask, bid_qty, ask_qty) and a short sliding window of recent trades from in-process memory, not from REST. The draft window SHALL be about the last 5 seconds. The window SHALL NOT be fixed at 2 seconds (that figure is the #1001 horizon). The window SHALL NOT store 1–5 minute aggregates (that is #1006). Signed REST balances MAY continue per user but SHALL stay off the cycle critical path (short cache, refresh every N seconds or after a fill).

#### Scenario: No bookTicker REST on a live cycle

- **WHEN** at least one user has the scalp ligado
- **AND** a cycle runs
- **THEN** that cycle SHALL NOT call REST `/api/v3/ticker/bookTicker`
- **AND** the Jev-facing touch SHALL come from the in-memory `bookTicker`

#### Scenario: Trades come from the short window

- **WHEN** a cycle reads recent BTCUSDT trades for the Jev state
- **THEN** it SHALL read the in-memory sliding window (about the last 5 seconds)
- **AND** SHALL NOT fetch those trades from REST on that cycle

### Requirement: Stale or down stream fails closed and cancels this bot's resting

The cycle SHALL compute `age_ms` as wall-clock time since the last in-memory `bookTicker` event. If `age_ms` is greater than 500, or the stream is down, the cycle SHALL NOT send an order. There SHALL be no silent fallback to a stale REST book. While the book is unavailable the loop SHALL cancel this bot's resting orders (`cfscalp_`) so a drop cannot leave an order off the touch, and SHALL try to reconnect. Other users' Operar orders SHALL NOT be cancelled.

#### Scenario: age_ms above 500 blocks send

- **WHEN** the scalp is ligado
- **AND** `age_ms` of the in-memory touch is greater than 500
- **THEN** the cycle SHALL NOT send an order
- **AND** SHALL NOT fill the touch from REST `/api/v3/ticker/bookTicker`

#### Scenario: WebSocket drop does not leave a resting order off-touch

- **WHEN** the shared BTCUSDT stream drops
- **THEN** the cycle SHALL NOT send
- **AND** SHALL cancel this bot's resting orders
- **AND** SHALL attempt to reconnect
- **AND** SHALL NOT silently resume from a REST bookTicker snapshot

#### Scenario: Order only leaves with fresh touch

- **WHEN** the scalp is ligado and the cycle posts a post-only order
- **THEN** `age_ms` SHALL be less than or equal to 500
- **AND** the touch SHALL be the in-memory `bookTicker`
