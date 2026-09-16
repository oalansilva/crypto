# discovery-deduplication Specification

## Purpose
TBD - created by archiving change card-469-varredura-backtest. Update Purpose after archive.
## Requirements
### Requirement: Build a versioned structural and quantized equivalence key

The system SHALL canonicalize indicator types, explicit alias map, logical tree and effective parameters into a versioned structural document. Commutative children SHALL sort by canonical serialization; non-commutative order SHALL be preserved. Missing optional parameters SHALL first resolve to the versioned template default, while missing required parameters SHALL make the candidate invalid. Alias normalization SHALL occur before defaults and quantization.

Every numeric parameter SHALL use a documented class-specific quantum and boundary rule: `bucket = round_half_away_from_zero(value / quantum)` after unit normalization; a value exactly at a half-quantum SHALL enter the bucket away from zero. Enum, boolean and duration identifiers SHALL compare exactly after alias normalization. The persisted `strategy_identity_key` SHALL include canonical structure/version, quantized effective parameters, symbol, timeframe and direction. Effective window SHALL NOT be part of strategy identity. A separate `evidence_fingerprint` SHALL hash effective `[start_at, end_at)`, timezone/calendar version, candle source/version, gap/coverage facts, fees/slippage assumptions and metrics snapshot as provenance only. Neither key SHALL rely on vague SQL `UNIQUE` over approximate floats.

#### Scenario: Aliases, defaults and commutative order

- **WHEN** two candidates use documented indicator aliases, omit the same optional defaults and serialize commutative children in different orders
- **THEN** they produce the same canonical structural document and equivalence key

#### Scenario: Boundary and missing required parameter

- **WHEN** a numeric value lands exactly on a half-quantum boundary
- **THEN** round-half-away-from-zero determines one reproducible bucket
- **WHEN** a required parameter is absent
- **THEN** the candidate is invalid rather than silently treated as equivalent

### Requirement: Compare with explicit template and favorite dimensions

Template equivalence SHALL compare canonical structure plus effective quantized parameters and direction support against the current template version; symbol/timeframe/date evidence SHALL not distinguish a template default. Favorite/promotion equivalence SHALL compare `strategy_identity_key`; a different evidence window, candle version, cost assumption or metric snapshot SHALL be recorded as distinct `evidence_fingerprint` but SHALL NOT evade duplicate detection. Active favorites SHALL block promotion. Inactive/archived favorites SHALL be reported as historical matches but SHALL NOT block unless repository policy explicitly reactivates them in the same transaction.

#### Scenario: New evidence cannot evade strategy duplicate detection

- **WHEN** two results share structure, effective quantized parameters, symbol, timeframe and direction but use different windows or candle versions
- **THEN** they share one `strategy_identity_key` and are equivalent for promotion
- **AND** they retain different `evidence_fingerprint` values for audit provenance

#### Scenario: Inactive favorite match

- **WHEN** a result matches only an inactive favorite
- **THEN** the result records `historical_duplicate_favorite` with reference
- **AND** remains promotable unless current policy reactivates that favorite

#### Scenario: Active favorite match

- **WHEN** a result matches an active favorite on every full-key dimension
- **THEN** it becomes `duplicate_favorite`, identifies the favorite and blocks promotion

### Requirement: Serialize concurrent equivalence decisions with a lock

Promotion SHALL acquire a transaction-scoped advisory lock derived from a collision-resistant hash of the `strategy_identity_key` (or lock its registry row), then requery templates, active favorites and committed promotions before inserting. Database uniqueness SHALL protect exact strategy-identity/version identity as a final guard, not approximate equality or evidence fingerprint.

#### Scenario: Concurrent equivalent candidates

- **WHEN** two transactions promote different results with the same `strategy_identity_key`
- **THEN** only one transaction passes locked revalidation and inserts a favorite
- **AND** the other returns the committed equivalent reference

### Requirement: Preserve append-only classification history

Every classification SHALL append evidence containing classification timestamp, canonical/alias/default/quantization versions, compared dimensions, catalog/favorite version, status and matched reference. Reclassification SHALL create a new current record without mutating prior evidence. Leaderboard reads SHALL identify the current classification and MAY expose prior classifications for audit.

#### Scenario: Historical reclassification

- **WHEN** a template alias, quantum version or favorite activation changes and reclassification runs
- **THEN** a new evidence record becomes current
- **AND** the previous classification remains queryable with its original versions and reason

### Requirement: Deleted favorite is not an active match

When a favorite is removed from the list by real deletion (the product today deletes the row; it does not archive or inactivate it), the system SHALL stop treating that favorite as an active duplicate or promotion target. Results previously classified `duplicate_favorite` or `already_promoted` against that favorite SHALL become current `unique` (append-only reclassification; prior evidence remains queryable for audit). The leaderboard and promotion paths SHALL also re-read whether the referenced favorite still exists, so a stale stored classification cannot keep lying. The grid SHALL NOT show a historical-favorite note. Internal audit MAY record the reclassification; that trail SHALL NOT appear on the Discovery row.

#### Scenario: Duplicate of a deleted favorite becomes unique

- **GIVEN** a persisted result classified `duplicate_favorite` with reference N
- **AND** favorite N has been deleted from the list
- **WHEN** Discovery reads that result
- **THEN** the current classification is `unique`
- **AND** no historical-favorite note is attached for the grid

#### Scenario: Already-promoted origin of a deleted favorite becomes unique

- **GIVEN** a persisted result classified `already_promoted` because it created favorite N
- **AND** favorite N has been deleted from the list
- **WHEN** Discovery reads that result
- **THEN** the current classification is `unique`
- **AND** the row is not treated as still being that favorite

#### Scenario: Live favorite still blocks

- **GIVEN** a result equivalent to a favorite that still exists
- **WHEN** Discovery classifies or re-reads it
- **THEN** it remains `duplicate_favorite` with that favorite as reference

