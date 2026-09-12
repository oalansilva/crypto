# discovery-promotion Specification

## Purpose
TBD - created by archiving change card-469-varredura-backtest. Update Purpose after archive.
## Requirements
### Requirement: Promote an eligible candidate only to tier 3

The system SHALL require explicit administrator confirmation to promote an eligible `unique` discovery result. This capability SHALL create **exactly tier 3** favorites. The request, UI and server contract SHALL expose no tier selector or tier override; any payload that supplies a tier other than `3` SHALL be rejected. Confirmation SHALL show candidate identity, `sweep_id`, `result_id` and fixed destination `Tier 3 · observação`.

#### Scenario: Promote a unique candidate

- **WHEN** the administrator confirms promotion of an eligible unique result
- **THEN** exactly one tier 3 favorite is created
- **AND** the result becomes `already_promoted`
- **AND** the leaderboard confirms success without removing the result

#### Scenario: Reject another tier

- **WHEN** a client sends tier `2`, omits the fixed contract version, or attempts any non-3 tier
- **THEN** promotion is rejected and no favorite/result state changes

#### Scenario: Attempt to promote a duplicate or low-sample candidate

- **WHEN** a candidate is equivalent to a template/favorite or fails ranking eligibility
- **THEN** promotion is unavailable
- **AND** the UI explains the matched reference or eligibility reason

### Requirement: Record immutable discovery provenance and evidence

The created favorite SHALL store `origin_type=discovery_sweep`, `sweep_id`, `result_id`, source template/version, symbol, timeframe, direction, `strategy_identity_key`, `evidence_fingerprint`, effective start/end, candle source/version, fees/slippage assumptions, benchmark convention, effective parameters, metrics snapshot and promotion timestamp. The server SHALL copy these values from the persisted result; the client SHALL NOT supply or recompute them. `evidence_fingerprint` is provenance and SHALL NOT replace or relax uniqueness by `strategy_identity_key`.

#### Scenario: Inspect a promoted short candidate

- **WHEN** a promoted short result is retrieved
- **THEN** provenance identifies its exact sweep/result and effective evidence window
- **AND** the stored Buy & Hold benchmark is the asset's long-only market benchmark over the identical candles, displayed as context rather than a synthetic short benchmark

### Requirement: Make promotion transactional, locked and idempotent

Promotion SHALL derive `actor` from the authenticated principal, never trust a client-supplied actor, and return HTTP `403` when that principal lacks administrative authorization. It SHALL revalidate authorization, result eligibility and current dedup state while holding the strategy-identity lock defined by discovery-deduplication. Favorite creation and result transition SHALL commit in one transaction. The persistence layer SHALL enforce a unique idempotency record for `(actor, idempotency_key)` and store its normalized `payload_hash`, favorite identity and response. A matching retry SHALL return the same favorite; key reuse with a divergent hash SHALL return HTTP `409` without mutation.

#### Scenario: Double confirmation or matching retry

- **WHEN** the same actor retries an identical promotion payload with the same idempotency key
- **THEN** every successful response identifies the same favorite
- **AND** only one tier 3 favorite exists

#### Scenario: Concurrent equivalent promotions

- **WHEN** two structurally equivalent candidates are promoted concurrently
- **THEN** the canonical-key advisory/row lock serializes equivalence revalidation
- **AND** at most one favorite is created and the loser receives HTTP `409` with the matching favorite reference

#### Scenario: Payload mismatch retry

- **WHEN** an idempotency key used for one `result_id` is retried with another result or payload hash
- **THEN** the system returns an idempotency mismatch conflict and performs no mutation

#### Scenario: Concurrent promotion requests reuse one key with divergent hashes

- **WHEN** the same actor concurrently promotes different results using one `idempotency_key` and divergent normalized hashes
- **THEN** exactly one request may persist the unique idempotency record and favorite transaction
- **AND** the loser reads the stored hash, returns HTTP `409`, and performs no result or favorite mutation

#### Scenario: Roll back partial promotion

- **WHEN** result-state update fails after favorite insertion is attempted
- **THEN** the whole transaction rolls back
- **AND** neither an orphan favorite nor an `already_promoted` result remains

### Requirement: Reject promotion of a discarded result

The system SHALL reject promotion when the result `dedup_state` is `discarded`. Discarded rows are omitted from the default leaderboard.

#### Scenario: Promote discarded result via API

- **WHEN** a client posts promotion for a `discarded` `result_id`
- **THEN** the server rejects the request
- **AND** no favorite is created

### Requirement: Promote from Acompanhar parciais with the same tier-3 dialog

The system SHALL allow an authenticated administrator to promote an eligible `unique` discovery result from Acompanhar locked top-5 parciais using the **same** confirmation dialog as Decidir (fixed destination **Promover a favorito tier 3**; no tier selector). The dialog SHALL open from the parciais Promover control. Cancel, Voltar, or overlay dismiss SHALL leave the candidate and the sweep unchanged. A `NO-GO` seal with sufficient sample SHALL NOT disable Promover (the seal is an alert only, same as Decidir). After confirmed promotion the parciais row SHALL show **Favorito tier 3**, SHALL keep its place in the top-5, and the active sweep SHALL continue (pause/cancel of the sweep are not implied). The same `result_id` on Decidir SHALL show the promoted state.

#### Scenario: Promote a NO-GO eligible partial while the sweep runs

- **GIVEN** a NO-GO eligible unique row in Acompanhar parciais and a non-terminal sweep
- **WHEN** the operator confirms Promover as tier 3
- **THEN** exactly one tier 3 favorite is created
- **AND** the row shows Favorito tier 3 and keeps its top-5 slot
- **AND** the sweep does not stop
- **AND** the NO-GO seal remains visible and did not block the click

#### Scenario: Cancel leaves the partial and the sweep untouched

- **GIVEN** the promotion dialog opened from a parciais Promover
- **WHEN** the operator cancels, goes Voltar, or dismisses the overlay
- **THEN** no favorite is created
- **AND** the candidate and the sweep stay as they were

