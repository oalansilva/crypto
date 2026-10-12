## MODIFIED Requirements

### Requirement: Preflight a bounded swing discovery snapshot server-side

The system SHALL expose an admin-only dry-run endpoint `POST /combos/discovery/sweeps/preflight`. It SHALL accept one or more existing templates, one or more supported symbols, one or more swing timeframes from the Entra table (`15m`, `1h`, `4h`, `1d`), one or both directions (`long`, `short`) and a valid historical period. It SHALL return the normalized axes, raw cartesian total, valid combinations, excluded combinations with a reason keyed by `template × symbol × timeframe`, configured axis/total limits, actual valid total, expiry and a cryptographically bound `snapshot_token` plus `snapshot_hash`. Empty axes, inverted dates and unsupported values SHALL be reported against the responsible axis without discarding the draft. Timeframes outside that table (`1m`, `5m`, `30m`, or any other) SHALL be reported as unsupported on the timeframes axis and SHALL NOT enter the snapshot. `4h` and `1d` SHALL remain accepted.

Creation SHALL accept the preflight token, `idempotency_key`, normalized `payload_hash`, and no client-calculated total. `actor` SHALL be derived exclusively from the authenticated principal (never trusted from client input); if a compatibility layer still transmits an actor field, the server SHALL compare it to the authenticated principal and reject any mismatch. The persistence layer SHALL enforce one unique idempotency record per `(actor, idempotency_key)` and SHALL store its `payload_hash`, `sweep_id` and response identity. In one transaction it SHALL lock/revalidate token freshness, derived actor, normalized payload hash, catalog compatibility and limits, persist the immutable snapshot/combinations/outbox records, and reject a stale or mismatched token without enqueueing work. The server SHALL compute `payload_hash` from a canonical serialization of templates, symbols, timeframes and directions (stable sorted order, not client array order). The client SHALL send a draft-scoped UUID as `idempotency_key`; `snapshot_hash` SHALL NOT be used as that key. "Novo rascunho" SHALL generate a new key.

#### Scenario: Compatible and incompatible combinations

- **WHEN** preflight receives 3 templates, 4 symbols, 2 timeframes and 2 directions and one `template × symbol × timeframe` tuple is incompatible
- **THEN** the response reports raw total `48`, the tuple and reason, `2` excluded directional combinations and actual valid total `46`
- **AND** the UI reports the exclusion beside the affected axis and uses `46` everywhere as the planned total

#### Scenario: Revalidate snapshot atomically

- **WHEN** catalog compatibility or a limit changes after preflight but before creation
- **THEN** creation rejects the stale snapshot token in the same transaction that would persist the sweep
- **AND** no sweep, combination or enqueue side effect is committed
- **AND** the response instructs the client to run preflight again

#### Scenario: Idempotent create retry

- **WHEN** the same actor retries creation with the same `idempotency_key` and `payload_hash`
- **THEN** the response returns the original `sweep_id` and immutable snapshot
- **WHEN** the same actor retries with the same key and equivalent axes in a different list order
- **THEN** the canonical payload hash matches and the response is an idempotent retry, not HTTP `409`
- **WHEN** the same actor reuses that key with a different payload hash
- **THEN** the stored hash is compared under the unique `(actor, idempotency_key)` lock, the system returns HTTP `409` idempotency conflict, and creates nothing

#### Scenario: Concurrent create requests reuse one key with divergent hashes

- **WHEN** two requests for the same actor concurrently use one `idempotency_key` with different normalized payload hashes
- **THEN** exactly one request may persist the unique idempotency record and sweep
- **AND** the other observes the stored divergent hash, returns HTTP `409`, and creates no sweep, combinations or outbox intents

#### Scenario: Retry with reordered axes is idempotent

- **WHEN** the same actor retries creation with the same `idempotency_key` and an equivalent payload whose templates/symbols/timeframes/directions are in a different order
- **THEN** the response returns the original `sweep_id` and HTTP success (idempotent retry)
- **AND** it SHALL NOT return HTTP `409`

## ADDED Requirements

### Requirement: Discovery swing timeframes include 1h and 15m

Discovery preflight and sweep creation SHALL accept `15m` and `1h` in addition to `4h` and `1d`. A draft that selects only `1h`, only `15m`, or any combination of the four SHALL be valid when the other axes are valid. A daily-trend filter SHALL NOT be required for `4h`, `1h` or `15m`.

#### Scenario: 1h and 15m pass preflight with 4h and 1d still valid

- **WHEN** preflight receives timeframes `15m`, `1h`, `4h` and `1d` with at least one template and one symbol
- **THEN** those four values appear on the normalized timeframes axis
- **AND** `4h` and `1d` remain accepted

#### Scenario: 1m 5m 30m are not Discovery swing timeframes

- **WHEN** preflight receives timeframe `1m`, `5m` or `30m`
- **THEN** the timeframes axis reports an unsupported value
- **AND** no snapshot is created with that timeframe

#### Scenario: 4h 1h 15m run without daily trend filter

- **WHEN** a combination uses timeframe `4h`, `1h` or `15m`
- **THEN** the sweep does not require a daily-chart trend filter
- **AND** the combination is optimized on that timeframe alone
