# Delta — discovery-sweep — cancelamento auto-finaliza (card #853)

## MODIFIED Requirements

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
