## ADDED Requirements

### Requirement: Sweep payload hash is canonical across axis order
The server SHALL compute `payload_hash` from a canonical serialization of templates, symbols, timeframes, and directions (stable sorted order, not client array order). Equivalent payloads with different list order SHALL produce the same hash.

#### Scenario: Retry with reordered axes is idempotent
- **WHEN** the same actor retries creation with the same `idempotency_key` and an equivalent payload whose templates/symbols/timeframes/directions are in a different order
- **THEN** the response returns the original `sweep_id` and HTTP success (idempotent retry)
- **AND** it SHALL NOT return HTTP `409`

### Requirement: Idempotency key is per draft, not snapshot_hash
The client SHALL send a draft-scoped `idempotency_key` (UUID generated for that draft). The server SHALL NOT treat `snapshot_hash` as the idempotency key. Starting a new draft SHALL generate a new key so a second start does not reuse the previous sweep's key.

#### Scenario: New draft gets a new key
- **WHEN** the user activates "Novo rascunho" after a sweep
- **THEN** the next start uses a new `idempotency_key`
- **AND** that start creates a distinct sweep instead of returning the previous `sweep_id`

#### Scenario: Same draft retry keeps the key
- **WHEN** the user retries start on the same draft without creating a new draft
- **THEN** the same `idempotency_key` is reused
- **AND** an equivalent payload returns the original sweep
