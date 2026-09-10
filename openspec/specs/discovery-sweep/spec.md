# discovery-sweep Specification

## Purpose
TBD - created by archiving change card-469-varredura-backtest. Update Purpose after archive.
## Requirements
### Requirement: Preflight a bounded swing discovery snapshot server-side

The system SHALL expose an admin-only dry-run endpoint `POST /combos/discovery/sweeps/preflight`. It SHALL accept one or more existing templates, one or more supported symbols, one or both swing timeframes (`4h`, `1d`), one or both directions (`long`, `short`) and a valid historical period. It SHALL return the normalized axes, raw cartesian total, valid combinations, excluded combinations with a reason keyed by `template × symbol × timeframe`, configured axis/total limits, actual valid total, expiry and a cryptographically bound `snapshot_token` plus `snapshot_hash`. Empty axes, inverted dates and unsupported values SHALL be reported against the responsible axis without discarding the draft.

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

### Requirement: Idempotency key is per draft, not snapshot_hash

The client SHALL send a draft-scoped `idempotency_key` (UUID generated for that draft). The server SHALL NOT treat `snapshot_hash` as the idempotency key. `payload_hash` SHALL canonicalize templates, symbols, timeframes and directions (stable sorted order). Starting a new draft SHALL generate a new key so a second start does not reuse the previous sweep's key.

#### Scenario: New draft gets a new key

- **WHEN** the user activates "Novo rascunho" after a sweep
- **THEN** the next start uses a new `idempotency_key`
- **AND** that start creates a distinct sweep instead of returning the previous `sweep_id`

#### Scenario: Same draft retry keeps the key

- **WHEN** the user retries start on the same draft without creating a new draft
- **THEN** the same `idempotency_key` is reused
- **AND** an equivalent payload returns the original sweep

### Requirement: Persist an explicit sweep lifecycle and reconciled counters

Every sweep SHALL be in exactly one state: `pending`, `running`, `paused`, `cancelling`, `cancelled`, `failed`, `partial_failure`, or `completed`. `cancelled`, `failed`, `partial_failure`, and `completed` are terminal. At all observable points `processed = succeeded + failed + skipped + insufficient_sample` and `0 ≤ processed ≤ total`; these counters represent reconciled combination dispositions, not optimizer starts. Every terminal state SHALL have `processed = total`.

Terminal `failed` SHALL carry a required `terminal_reason` in one of two classes: (a) `all_results_failed`, used after normal result reconciliation when `succeeded = 0` and `failed > 0`; or (b) `operational_failure`, used for unrecoverable setup/worker/reconciliation failure and accompanied by a specific code such as `setup_failure`, `execution_reconciliation_failure`, or `cancellation_reconciliation_failure`. `partial_failure` SHALL be used only after normal result reconciliation when `succeeded > 0` and `failed > 0` and no operational failure is present. `completed` SHALL require `failed = 0` and (`succeeded > 0` or `insufficient_sample > 0`). A sweep with `succeeded = 0`, `failed = 0`, `insufficient_sample = 0` and `skipped > 0` after normal reconciliation SHALL remain `failed` with `operational_failure`.

Before any transition to terminal `failed`, the reconciler SHALL close every combination exactly once: already committed outcomes remain `succeeded`/`failed`/`insufficient_sample`, a lease with a known committed outcome is recovered to that outcome, and every still non-terminal combination becomes `skipped` with the operational failure code. Therefore `processed = succeeded + failed + skipped + insufficient_sample = total` in every path. Specifically, `pending → failed` skips all unstarted combinations; `running|paused → failed` preserves committed outcomes and skips all unresolved combinations; `cancelling → failed` preserves settled leases and skips every remainder while retaining the stronger cancellation intent in audit metadata. On terminal `cancelled`, every non-started/pending combination likewise becomes `skipped`; an in-flight leased combination MAY first settle as succeeded/failed/insufficient_sample.

The complete command/worker transition matrix SHALL be:

| From | Allowed next state(s) | Cause |
| --- | --- | --- |
| `pending` | `running`, `cancelling`, `failed` | dispatcher starts; cancel wins before start; unrecoverable setup failure |
| `running` | `paused`, `cancelling`, `completed`, `partial_failure`, `failed` | pause; cancel; terminal reconciliation |
| `paused` | `running`, `cancelling`, `failed` | resume; cancel; unrecoverable reconciliation failure |
| `cancelling` | `cancelled`, `failed` | leases settle; unrecoverable cancellation reconciliation failure |
| terminal | none | terminal states reject state-changing commands idempotently |

Pause and resume SHALL be rejected while state is `cancelling`; cancellation is the stronger intent and cannot be downgraded by a concurrent command. Concurrency limits («1 por sweep» on this 4-core VPS) SHALL NOT change.

#### Scenario: Partial failure terminal

- **WHEN** all combinations are reconciled and at least one failed while at least one succeeded
- **THEN** the sweep becomes `partial_failure`
- **AND** `processed = succeeded + failed + skipped + insufficient_sample = total`
- **AND** successful results remain rankable

#### Scenario: One hundred percent failure terminal

- **WHEN** every combination is reconciled, `succeeded = 0` and `failed > 0`
- **THEN** the sweep becomes terminal `failed`, never `partial_failure`
- **AND** `processed = failed + skipped + insufficient_sample = total` and no result is rankable

#### Scenario: Setup failure closes a pending sweep

- **WHEN** an unrecoverable setup failure moves a sweep from `pending` to `failed`
- **THEN** `terminal_reason=operational_failure` and code `setup_failure` are persisted
- **AND** every unstarted combination becomes `skipped`, so `processed = skipped = total`

#### Scenario: Reconciliation failure closes paused or cancelling work

- **WHEN** unrecoverable reconciliation moves a `paused` or `cancelling` sweep to `failed`
- **THEN** committed/settled outcomes retain `succeeded`, `failed` or `insufficient_sample`, every unresolved combination becomes `skipped`, and the corresponding operational failure code is persisted
- **AND** `processed = succeeded + failed + skipped + insufficient_sample = total`; cancellation intent remains in audit metadata when the origin was `cancelling`

#### Scenario: Cancel reconciles pending work

- **WHEN** cancellation is requested during running work
- **THEN** the sweep becomes `cancelling`, new claims are blocked, and pending combinations become `skipped`
- **AND** after active leases settle it becomes `cancelled` with `processed = total`

#### Scenario: Cancelling locks pause and resume

- **WHEN** a sweep is already `cancelling` and pause or resume is requested
- **THEN** the command is rejected without changing state or counters
- **AND** cancellation continues to reconciliation as the prevailing intent

#### Scenario: Insufficient-sample-only sweep is completed

- **WHEN** every combination is `insufficient_sample` and `failed = 0` and `succeeded = 0`
- **THEN** the sweep becomes `completed`
- **AND** it SHALL NOT become `failed` with `operational_failure`

### Requirement: Cancel closes on its own when nothing is in flight

When cancellation is requested and no combination is `running`, the command SHALL reconcile immediately under its lock: every `pending` combination becomes `skipped`, and the sweep SHALL become `cancelled` with `processed = total` in the same commit, without waiting for any worker, wake-up or operator action.

#### Scenario: Cancel with zero running closes inline

- **WHEN** the operator cancels a sweep with `pending` combinations and zero
  `running`
- **THEN** the command response is `cancelled`
- **AND** every `pending` became `skipped` and `processed = total`

### Requirement: Cancel with in-flight work waits and concludes alone

When cancellation is requested while combinations are `running`, the sweep SHALL stay `cancelling`, SHALL NOT force in-flight combinations to `skipped`, and the command SHALL schedule a single pending finalizer wake-up (no duplicate while one is outstanding) — but only if, after the inline reconcile, the sweep is still `cancelling` with `running > 0` (no insert when the inline reconcile already promoted it to `cancelled`). The finalizer claims nothing, runs scoped lease release for that sweep only (flush-only, no own commit), reconciles under lock with explicit post-lock re-read, and acks via a flush-only variant (`_ack_locked`: `delivered`-to-`acked` flip only, no own commit - option (a); the current `ack_outbox` with its own commit SHALL NOT be called on this path), as the last mutation — all in the same per-sweep commit; the global lease release with its own commit SHALL NOT run on this path. A dedup race that slips past the check and violates the unique (`sweep_id`, `generation`) constraint implies full rollback (no savepoint, no `created: False`), healed by command retry or next-dispatch repair. The reconcile where `pending == 0` and `running == 0` post-refresh SHALL promote `cancelling -> cancelled` with `processed = total`, with no operator action. A repeated `cancel` against a sweep already in `cancelling` SHALL still pass through the finalizer ensure (deduplicated — no duplicate while one is outstanding), never returning before it; a repeated `cancel` against an already `cancelled` sweep SHALL be an idempotent no-op, leaving any residue to the repair below.

#### Scenario: In-flight evaluations settle then the sweep closes

- **WHEN** the operator cancels with `running` combinations
- **THEN** the sweep stays `cancelling` and in-flight work is not forced to
  `skipped`
- **AND** exactly one finalizer is scheduled
- **AND** after the in-flight work settles the sweep becomes `cancelled`
  with `processed = total`

### Requirement: Claims are fenced and terminal close is re-finalizable

Claiming SHALL be fenced by the sweep row lock: a claim SHALL lock the sweep,
execute an explicit re-read after the lock (`db.refresh(locked)` or expire +
reload — without it the identity map still carries pre-lock values), proceed
only when the post-refresh sweep state is `running`, and commit the lock check
and the row claims atomically — a claim racing an inline cancel SHALL observe
`cancelling`/`cancelled` post-refresh and claim nothing. Reconciliation SHALL
lock the sweep row and execute an explicit re-read after the lock, re-reading
state and counters; it SHALL NEVER use pre-lock reads for any terminal
transition or fence guard — every decision uses post-refresh values. It SHALL
NEVER move a `cancelled` (or any terminal) sweep to another terminal nor
rewrite `state`/`completed_at` — over a `cancelled` sweep it SHALL only re-mark any
residual `pending` as `skipped` and recount so that
`processed = total` holds; the run pre-check SHALL return a combination to
`pending` under `cancelling` but SHALL mark it `skipped` directly under a
terminal state. Scoped lease release MAY transiently move an expired `running`
row back to `pending` even under a terminal sweep (including `cancelled`),
but the repair converts it in the same per-sweep commit (`pending → skipped`
under `cancelling`/`cancelled`), so no `pending` survives the commit; a
settle that commits after the close is absorbed by recount in the next
repair.

#### Scenario: Late claim after inline close claims nothing

- **WHEN** a claim and an inline cancel race and the cancel commits first
- **THEN** the claim observes the terminal state post-refresh under the lock
  and claims zero combinations
- **AND** the sweep stays `cancelled` with `processed = total`

### Requirement: Repair heals orphaned cancelling sweeps

The periodic repair inside outbox dispatch SHALL also cover `cancelling`
sweeps: it SHALL run scoped lease release for that sweep, then reconcile
them, and SHALL ensure a finalizer while `running` remains. A `cancelling` sweep with an `acked` outbox and zero
`running` SHALL become `cancelled` with `processed = total` on the next
dispatch, without backfill and without reprocessing skipped combinations.
The repair SHALL additionally cover `cancelled` sweeps with residue
(`pending > 0 OR running > 0 OR processed != total`): under the sweep lock
with explicit post-lock re-read, in the sweep's own transaction, it SHALL run
scoped lease release for that sweep, then re-mark residual `pending` as
`skipped` and recount — without
changing `state`/`completed_at` and without scheduling a new wake-up. A
`cancelled` sweep holding `running` rows on expired leases of a dead worker
therefore converges at lease TTL: the scoped release returns them to
`pending` transiently and the same-commit reconcile marks them `skipped`.
Each sweep SHALL be repaired in its own transaction (commit; on failure
rollback, expire/cleanup and continue — failure in one sweep SHALL NOT block
the others); no single transaction spans the sweep loop and no nested
savepoint is the default pattern.

#### Scenario: Stuck cancelling with acked outbox heals on dispatch

- **WHEN** a sweep is stuck in `cancelling` with an `acked` outbox,
  remaining `pending` and zero `running`
- **THEN** the next dispatch reconciles it to `cancelled`
- **AND** `processed = total` with no reprocessing of skipped combinations

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

### Requirement: Start begins a new sweep from the on-screen draft

After a terminal sweep (cancelled, failed, partial_failure, completed), creation SHALL treat the on-screen selection (templates, symbols, timeframes, directions, period) as a new start: it SHALL persist a new sweep for the submitted selection even when that selection equals the dead run's, SHALL never reopen the dead run, and SHALL NOT return the draft-conflict rejection for this path. The happy path SHALL NOT require "Novo rascunho".

#### Scenario: Post-terminal start with changed selection

- **WHEN** the previous sweep is terminal and the operator changes the selection and clicks Iniciar
- **THEN** a new sweep with that selection is created and progress appears
- **AND** no draft-conflict failure is returned

#### Scenario: Post-terminal start with identical selection

- **WHEN** the previous sweep is terminal and the selection is unchanged and the operator clicks Iniciar
- **THEN** a new sweep is created
- **AND** the dead run is not reopened

#### Scenario: Reload after cancel does not pin to the old run

- **WHEN** the operator reloads after cancel, builds another selection and clicks Iniciar
- **THEN** a new sweep starts with no second button and no browser-data clearing

### Requirement: Start while a sweep is live never forks

While a sweep is non-terminal (pending, running, paused, cancelling), creation with a different selection SHALL create no second sweep and SHALL NOT replace the live one; the response and the UI SHALL direct the operator to cancel first. A repeat start for the same selection while its sweep is being created or is live SHALL return the existing sweep without duplication, and the screen SHALL show it.

#### Scenario: Other selection while live is blocked with guidance

- **WHEN** a sweep is live and the operator picks another selection and clicks Iniciar
- **THEN** no second sweep is created
- **AND** the screen directs the operator to cancel before starting another

#### Scenario: Repeat start on the same live selection shows the existing sweep

- **WHEN** Iniciar just fired (or that selection's sweep is still live) and the operator clicks again on the same selection
- **THEN** no duplicate is born
- **AND** the screen shows the existing sweep

### Requirement: Start failures speak operations language

Any start failure surfaced in the UI SHALL be an operations sentence (what to do next) and SHALL NOT expose JSON or jargon.

#### Scenario: Failure text is operational

- **WHEN** starting fails and the screen shows an error
- **THEN** the text is an operations instruction
- **AND** no JSON or jargon is shown

### Requirement: Sweep payload hash is canonical across axis order
The server SHALL compute `payload_hash` from a canonical serialization of templates, symbols, timeframes, and directions (stable sorted order, not client array order). Equivalent payloads with different list order SHALL produce the same hash.

#### Scenario: Retry with reordered axes is idempotent
- **WHEN** the same actor retries creation with the same `idempotency_key` and an equivalent payload whose templates/symbols/timeframes/directions are in a different order
- **THEN** the response returns the original `sweep_id` and HTTP success (idempotent retry)
- **AND** it SHALL NOT return HTTP `409`

### Requirement: Discovery combinations SHALL run Deep Backtest and walk-forward 70/30

When a Discovery worker runs a claimed combination, it SHALL invoke `ComboOptimizer.run_optimization` with `deep_backtest=true` and `split_train_ratio=0.7`. Optimization stages and the final in-sample backtest SHALL use the oldest 70% of the effective candle window. The newest 30% SHALL be the holdout evaluated by the existing walk-forward gate. The worker SHALL NOT omit `split_train_ratio` (legacy full-window path) for Discovery combinations.

#### Scenario: Combination invokes optimizer with Combo defaults

- **WHEN** a Discovery combination starts optimization
- **THEN** the optimizer call includes `deep_backtest=true` and `split_train_ratio=0.7`
- **AND** Deep Backtest 15m remains enabled for `data_source=ccxt`

#### Scenario: Split is not optional per combination

- **WHEN** any successful Discovery combination completes
- **THEN** the worker requested walk-forward 70/30 rather than omitting `split_train_ratio`
- **AND** the persisted metrics snapshot records `split_train_ratio` of `0.7`
- **AND** `split_applied` is true when holdout metrics/verdict exist, false if the optimizer skipped the split

### Requirement: Skip optimizer when listing cannot produce ranking trades

The worker SHALL, for each claimed combination still in a running sweep, count the observed OHLCV listing in that combination's symbol × timeframe × snapshot period **before** invoking parameter-grid optimization. It SHALL apply the same walk-forward split already used by Discovery (`split_train_holdout` with `DISCOVERY_SPLIT_TRAIN_RATIO=0.7`). When the listing is empty, has fewer than 2 bars, or the in-sample (train) bar count is strictly less than `MIN_ELIGIBLE_TRADES` (default 30), the worker SHALL NOT run the optimizer/grid. The combination SHALL settle as `insufficient_sample` in seconds. A combination whose train bars are at least 30 SHALL follow the existing happy path (optimize, then `eligible` or `low_sample`).

#### Scenario: Short daily listing skips the grid

- **WHEN** a claimed 1d combination has ~27 observed daily bars in the requested period (including «todo o histórico»)
- **THEN** train bars after the 70/30 split are below 30
- **AND** the worker does not start grid optimization
- **AND** the combination settles as `insufficient_sample` in seconds

#### Scenario: Full listing still optimizes

- **WHEN** a claimed combination has enough observed bars for train ≥ 30
- **THEN** the worker runs the existing optimizer path
- **AND** a later `Baixa amostra` outcome remains `succeeded` with `eligibility=low_sample`

### Requirement: Fourth progress bag for insufficient sample

At all observable points the reconciled counters SHALL satisfy `processed = succeeded + failed + skipped + insufficient_sample` and `0 ≤ processed ≤ total`. `succeeded` SHALL count combinations that ran the optimizer and left a decidable candidate (including post-grid `low_sample`). `skipped` SHALL count combinations that did not run (cancel / not started). `insufficient_sample` SHALL count listing-too-short combinations that did not run the optimizer. Every terminal state SHALL have `processed = total`. The active-sweep and leaderboard APIs SHALL expose `insufficient_sample` (default 0 for rows persisted before this change).

#### Scenario: Formula includes the fourth term

- **WHEN** a running sweep has 12 succeeded, 1 failed, 1 skipped and 4 insufficient_sample
- **THEN** `processed` is 18
- **AND** the progress payload reports all four addends

### Requirement: Insufficient-only sweep completes

Normal result reconciliation SHALL treat a sweep with `failed = 0` and `insufficient_sample > 0` as `completed` even when `succeeded = 0`. That outcome SHALL NOT set `terminal_reason=operational_failure` and SHALL NOT use the skipped-only operational-failure branch. The skipped-only operational failure (`succeeded = 0`, `failed = 0`, `insufficient_sample = 0`, `skipped > 0`) SHALL remain unchanged.

#### Scenario: All short listings conclude completed

- **WHEN** every combination is reconciled as `insufficient_sample` and none succeeded or failed
- **THEN** the sweep state is `completed`
- **AND** `processed = insufficient_sample = total`
- **AND** `terminal_reason` is not `operational_failure`

