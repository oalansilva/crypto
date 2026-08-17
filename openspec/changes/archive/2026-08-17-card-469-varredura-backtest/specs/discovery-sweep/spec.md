# Discovery Sweep Specification

## ADDED Requirements

### Requirement: Preflight a bounded swing discovery snapshot server-side

The system SHALL expose an admin-only dry-run endpoint `POST /combos/discovery/sweeps/preflight`. It SHALL accept one or more existing templates, one or more supported symbols, one or both swing timeframes (`4h`, `1d`), one or both directions (`long`, `short`) and a valid historical period. It SHALL return the normalized axes, raw cartesian total, valid combinations, excluded combinations with a reason keyed by `template × symbol × timeframe`, configured axis/total limits, actual valid total, expiry and a cryptographically bound `snapshot_token` plus `snapshot_hash`. Empty axes, inverted dates and unsupported values SHALL be reported against the responsible axis without discarding the draft.

Creation SHALL accept the preflight token, `idempotency_key`, normalized `payload_hash`, and no client-calculated total. `actor` SHALL be derived exclusively from the authenticated principal (never trusted from client input); if a compatibility layer still transmits an actor field, the server SHALL compare it to the authenticated principal and reject any mismatch. The persistence layer SHALL enforce one unique idempotency record per `(actor, idempotency_key)` and SHALL store its `payload_hash`, `sweep_id` and response identity. In one transaction it SHALL lock/revalidate token freshness, derived actor, normalized payload hash, catalog compatibility and limits, persist the immutable snapshot/combinations/outbox records, and reject a stale or mismatched token without enqueueing work.

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
- **WHEN** the same actor reuses that key with a different payload hash
- **THEN** the stored hash is compared under the unique `(actor, idempotency_key)` lock, the system returns HTTP `409` idempotency conflict, and creates nothing

#### Scenario: Concurrent create requests reuse one key with divergent hashes

- **WHEN** two requests for the same actor concurrently use one `idempotency_key` with different normalized payload hashes
- **THEN** exactly one request may persist the unique idempotency record and sweep
- **AND** the other observes the stored divergent hash, returns HTTP `409`, and creates no sweep, combinations or outbox intents

### Requirement: Persist an explicit sweep lifecycle and reconciled counters

Every sweep SHALL be in exactly one state: `pending`, `running`, `paused`, `cancelling`, `cancelled`, `failed`, `partial_failure`, or `completed`. `cancelled`, `failed`, `partial_failure`, and `completed` are terminal. At all observable points `processed = succeeded + failed + skipped` and `0 ≤ processed ≤ total`; these counters represent reconciled combination dispositions, not optimizer starts. Every terminal state SHALL have `processed = total`.

Terminal `failed` SHALL carry a required `terminal_reason` in one of two classes: (a) `all_results_failed`, used after normal result reconciliation when `succeeded = 0` and `failed > 0`; or (b) `operational_failure`, used for unrecoverable setup/worker/reconciliation failure and accompanied by a specific code such as `setup_failure`, `execution_reconciliation_failure`, or `cancellation_reconciliation_failure`. `partial_failure` SHALL be used only after normal result reconciliation when `succeeded > 0` and `failed > 0` and no operational failure is present; `completed` SHALL require `succeeded > 0` and `failed = 0`.

Before any transition to terminal `failed`, the reconciler SHALL close every combination exactly once: already committed outcomes remain `succeeded`/`failed`, a lease with a known committed outcome is recovered to that outcome, and every still non-terminal combination becomes `skipped` with the operational failure code. Therefore `processed = succeeded + failed + skipped = total` in every path. Specifically, `pending → failed` skips all unstarted combinations; `running|paused → failed` preserves committed outcomes and skips all unresolved combinations; `cancelling → failed` preserves settled leases and skips every remainder while retaining the stronger cancellation intent in audit metadata. On terminal `cancelled`, every non-started/pending combination likewise becomes `skipped`; an in-flight leased combination MAY first settle as succeeded/failed.

The complete command/worker transition matrix SHALL be:

| From | Allowed next state(s) | Cause |
| --- | --- | --- |
| `pending` | `running`, `cancelling`, `failed` | dispatcher starts; cancel wins before start; unrecoverable setup failure |
| `running` | `paused`, `cancelling`, `completed`, `partial_failure`, `failed` | pause; cancel; terminal reconciliation |
| `paused` | `running`, `cancelling`, `failed` | resume; cancel; unrecoverable reconciliation failure |
| `cancelling` | `cancelled`, `failed` | leases settle; unrecoverable cancellation reconciliation failure |
| terminal | none | terminal states reject state-changing commands idempotently |

Pause and resume SHALL be rejected while state is `cancelling`; cancellation is the stronger intent and cannot be downgraded by a concurrent command.

#### Scenario: Partial failure terminal

- **WHEN** all combinations are reconciled and at least one failed while at least one succeeded
- **THEN** the sweep becomes `partial_failure`
- **AND** `processed = succeeded + failed + skipped = total`
- **AND** successful results remain rankable

#### Scenario: One hundred percent failure terminal

- **WHEN** every combination is reconciled, `succeeded = 0` and `failed > 0`
- **THEN** the sweep becomes terminal `failed`, never `partial_failure`
- **AND** `processed = failed + skipped = total` and no result is rankable

#### Scenario: Setup failure closes a pending sweep

- **WHEN** an unrecoverable setup failure moves a sweep from `pending` to `failed`
- **THEN** `terminal_reason=operational_failure` and code `setup_failure` are persisted
- **AND** every unstarted combination becomes `skipped`, so `processed = skipped = total`

#### Scenario: Reconciliation failure closes paused or cancelling work

- **WHEN** unrecoverable reconciliation moves a `paused` or `cancelling` sweep to `failed`
- **THEN** committed/settled outcomes retain `succeeded` or `failed`, every unresolved combination becomes `skipped`, and the corresponding operational failure code is persisted
- **AND** `processed = succeeded + failed + skipped = total`; cancellation intent remains in audit metadata when the origin was `cancelling`

#### Scenario: Cancel reconciles pending work

- **WHEN** cancellation is requested during running work
- **THEN** the sweep becomes `cancelling`, new claims are blocked, and pending combinations become `skipped`
- **AND** after active leases settle it becomes `cancelled` with `processed = total`

#### Scenario: Cancelling locks pause and resume

- **WHEN** a sweep is already `cancelling` and pause or resume is requested
- **THEN** the command is rejected without changing state or counters
- **AND** cancellation continues to reconciliation as the prevailing intent

### Requirement: Claim work safely with leases, fairness and bounded concurrency

Each combination SHALL have a unique key `(sweep_id, template_id, symbol, timeframe, direction)` and an idempotent handler. A worker SHALL claim a pending combination with a lease in a transaction that rechecks the parent sweep is `running`; only the lease owner may begin/commit that attempt. Expired leases SHALL be recoverable by a reconciler without duplicating a committed result. Scheduling SHALL enforce configurable global and per-sweep concurrency limits and SHALL use fair round-robin/age ordering so one large sweep cannot starve another.

Optimization stage generation SHALL process each correlated parameter group exactly once. A legacy parameter range that provides `min` and `max` but omits `step` SHALL use the optimizer's deterministic coarse-step fallback rather than passing `None` to range generation or failing the combination.

#### Scenario: Two workers claim one combination

- **WHEN** two workers concurrently attempt to claim the same pending combination
- **THEN** exactly one obtains the lease and starts optimizer work
- **AND** the other observes no claimable row

#### Scenario: Lease expires after crash

- **WHEN** a worker crashes after claim but before committing a result
- **THEN** the reconciler returns the expired combination to pending or awards a new lease
- **AND** the idempotent handler/unique result key prevents a duplicate committed result

#### Scenario: Legacy correlated schema omits step

- **GIVEN** a template has a correlated parameter group whose ranges provide `min`, `max` and `default`, but no `step`
- **WHEN** the discovery worker generates optimization stages
- **THEN** each parameter receives a non-null deterministic coarse step and a finite value list
- **AND** stage generation does not duplicate the group or fail with arithmetic against `None`

### Requirement: Enqueue atomically through an at-least-once outbox and reconcile delivery

Sweep, combinations and enqueue intents SHALL commit in one database transaction. The chosen topology SHALL publish **one orchestrator job per sweep wake-up**, not one durable queue job per combination. The orchestrator payload SHALL contain only idempotent identity (`sweep_id`, orchestration generation/version), then claim combinations from PostgreSQL in bounded batches. Queue and outbox delivery semantics SHALL be at-least-once: a broker may accept a publish and the dispatcher may crash before acknowledging that delivery in PostgreSQL, so the reconciler SHALL redeliver the same idempotent orchestrator payload. Queue publication SHALL never be the sole record that work exists.

The dispatcher SHALL read at most `100` due outbox rows per poll, publish at most `20` per batch, and enforce configurable global/per-sweep outstanding-orchestrator limits (defaults `8` global and `1` per sweep). Each orchestrator activation SHALL claim at most `20` combinations and SHALL reschedule a wake-up only while claimable work remains. These values SHALL be configuration/versioned; queue depth/backpressure SHALL stop new publication without losing committed intents. Result commit and queue ACK SHALL be separate idempotent steps, with unique combination/result keys making redelivery safe.

#### Scenario: Crash between commit and enqueue

- **WHEN** the process crashes after the database transaction commits but before queue publication
- **THEN** the committed outbox intent remains discoverable
- **AND** the reconciler eventually publishes an orchestrator wake-up without creating a second combination

#### Scenario: Broker accepts publish before dispatcher ACK

- **WHEN** the broker accepts an orchestrator publish and the dispatcher crashes before recording delivery acknowledgement in PostgreSQL
- **THEN** the outbox intent remains unacknowledged and MAY be redelivered
- **AND** repeated orchestrator payloads converge on the same sweep/claims without duplicate optimizer result

#### Scenario: Result commits before queue ACK

- **WHEN** an orchestrator commits a combination result and crashes before ACKing its queue delivery
- **THEN** redelivery observes the committed unique result and does not rerun or duplicate it
- **AND** counters reconcile from the single committed combination state

### Requirement: Pause, resume and cancel respect already-enqueued jobs

Pause SHALL move only `pending`/`running` work to `paused` and prevent new optimizer starts. Jobs already present in the external queue MAY wake, but their worker SHALL transactionally recheck parent state and release/retain them pending without starting optimizer work. Resume SHALL move only `paused` work to `running`. Cancel SHALL move `pending`/`running`/`paused` to `cancelling`, apply the same start barrier, mark pending work skipped and await active leases before `cancelled`. Pause/resume during `cancelling` SHALL be rejected because cancellation prevails. Repeated valid commands SHALL return the current state without duplicate side effects.

#### Scenario: Pause races a queued worker

- **WHEN** pause commits while a queued worker is waking
- **THEN** the worker's transactional state recheck prevents optimizer start
- **AND** the combination remains pending for resume

#### Scenario: Cancel races pause and active work

- **WHEN** pause and cancel requests race while one combination holds a valid lease
- **THEN** cancellation wins as the stronger terminal intent
- **AND** no new combination starts, the leased attempt is reconciled, and all remaining pending work becomes skipped

### Requirement: Enforce authorization and operational limits

All read/write endpoints SHALL enforce the repository's administrative authorization. Preflight and creation SHALL return the effective per-axis, total-combination and concurrency limits. A non-admin request or over-limit snapshot SHALL create no sweep, outbox record or queue message.

#### Scenario: Scope exceeds operational limit

- **WHEN** actual valid combinations exceed the configured maximum
- **THEN** preflight reports the calculated total and maximum
- **AND** creation rejects the snapshot before any enqueue side effect

### Requirement: Confirm a successful start in the current viewport

After a successful sweep creation, the UI SHALL immediately expose the active sweep lifecycle without requiring a reload, history selection, or manual page search. It SHALL keep any historical leaderboard selection separate, move focus to the active progress heading, and scroll that heading into the current viewport. A terminal or low-sample result SHALL still remain discoverable through the active lifecycle and history even when it produces no eligible ranked candidate.

#### Scenario: Start one combination while viewing historical results

- **GIVEN** the administrator is viewing a historical leaderboard and the draft contains one valid combination
- **WHEN** creation returns the active `sweep_id`
- **THEN** the active progress block is rendered and scrolled into the current viewport
- **AND** its heading receives focus and identifies the newly created sweep lifecycle
- **AND** the historical leaderboard remains a separate selected run
