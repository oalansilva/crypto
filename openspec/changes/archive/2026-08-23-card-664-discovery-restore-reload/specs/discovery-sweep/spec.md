# Discovery sweep Delta Specification

## ADDED Requirements

### Requirement: Restore active sweeps after page reload

The system SHALL expose an admin-only active-sweep read that returns all non-terminal sweeps for the authenticated actor, ordered deterministically by `created_at DESC, sweep_id DESC`, or an empty list when none exists. On opening the Discovery page, the client SHALL use that server result to restore the newest active lifecycle instead of treating a browser reload as a new draft, while keeping any additional non-terminal sweeps accessible in history.

#### Scenario: Reload while a sweep is running

- **WHEN** an administrator opens `/combo/discovery` and the server has a `running` sweep with pending or running combinations for that actor
- **THEN** the page renders the same `sweep_id`, snapshot identity, state and reconciled counters from the server
- **AND** the active progress block and that sweep's leaderboard become visible without requiring history search
- **AND** polling resumes while the sweep remains non-terminal

#### Scenario: Reload while a sweep is paused

- **WHEN** an administrator opens `/combo/discovery` and the latest non-terminal sweep is `paused`
- **THEN** the page renders `PAUSED` with the `Retomar` action and the persisted processed/success/failure/skipped counters
- **AND** no new optimizer work starts until the administrator explicitly resumes

#### Scenario: No non-terminal sweep exists

- **WHEN** the active-sweep read returns an empty `sweeps` list
- **THEN** the page renders the normal editable draft and keeps terminal sweeps available through the history selector
- **AND** it does not fabricate an active progress block

#### Scenario: Active sweep becomes terminal during recovery

- **WHEN** a parallel detail poll or delayed `GET /sweeps/{id}` reports terminal for a sweep the page was restoring
- **THEN** the page does not leave that sweep marked as `activeSweep`
- **AND** it selects that same `sweep_id` in history and renders its persisted leaderboard

#### Scenario: Reload after the sweep already finished

- **WHEN** an administrator reloads `/combo/discovery` and the newest owned sweep is already terminal
- **THEN** the page does not render an active progress block
- **AND** history selects that same `sweep_id` (not a different older terminal run) and shows its leaderboard

#### Scenario: Recovery endpoint is unavailable

- **WHEN** the active-sweep read fails or returns an invalid snapshot
- **THEN** the page shows an inline recovery error with a retry action
- **AND** the start action remains disabled until the active check succeeds or explicitly confirms that no active sweep exists

### Requirement: Rehydrate and freeze the active draft from the persisted snapshot

When a non-terminal sweep is restored, the client SHALL hydrate the draft controls from the immutable persisted snapshot, including templates, symbols, timeframes, directions, historical period and the server-confirmed client-generated `draft_key`, without running a new preflight or recalculating the planned total in the browser. The draft SHALL remain frozen until the active sweep becomes terminal or the administrator explicitly starts a separate new draft according to the existing lifecycle.

The restored detail SHALL expose `draft_key: string`, `snapshot.axes.templates: string[]`, `snapshot.axes.symbols: string[]`, `snapshot.axes.timeframes: string[]`, `snapshot.axes.directions: string[]`, `snapshot.start_date: string|null`, `snapshot.end_date: string|null`, `snapshot.period_type: string|null`, `snapshot.raw_total: integer`, `snapshot.valid_total: integer`, `snapshot.exclusions: object`, `snapshot.limits: object`, `snapshot.snapshot_token: string` and `snapshot.snapshot_hash: string`. The client-generated draft key is echoed and bound to the returned `sweep_id`; it is not reissued during reload.

#### Scenario: Restore a valid snapshot

- **WHEN** the active sweep detail contains a valid persisted snapshot
- **THEN** the page shows the snapshot's axes, valid total, exclusions, period and snapshot label
- **AND** selection controls and the start action are disabled on restore while the recovered draft stays frozen
- **AND** the displayed counters remain the server's reconciled values

#### Scenario: Explicit new draft while another sweep is still non-terminal

- **WHEN** the administrator chooses Novo rascunho while a non-terminal sweep remains visible
- **THEN** the client generates a new `draft_key`, unfreezes the configurator and enables start for a distinct sweep
- **AND** the previous non-terminal sweep stays in the active panel and is not cancelled

#### Scenario: Focus another owned non-terminal sweep from history

- **WHEN** `GET .../sweeps/active` returns more than one non-terminal sweep and the administrator selects a non-newest non-terminal run in history
- **THEN** pause, resume and cancel target that selected sweep
- **AND** the other non-terminal sweeps remain listed
- **AND** a later reload restores lifecycle focus to the newest non-terminal sweep from the server list

#### Scenario: Catalog labels are temporarily unavailable

- **WHEN** the active snapshot is valid but the auxiliary template or symbol catalog cannot load
- **THEN** the page still displays the persisted IDs and lifecycle state
- **AND** it does not issue a replacement preflight or enable a second start

#### Scenario: Active sweep finishes after reload

- **WHEN** polling observes a terminal state for the restored sweep
- **THEN** the page stops active polling, displays the terminal state and refreshes history
- **AND** a future reload treats the sweep as historical rather than active

### Requirement: Scope discovery history and lifecycle reads to the authenticated actor

The history, active-sweep, sweep-detail, leaderboard and lifecycle command endpoints SHALL scope every query and mutation to the authenticated administrative principal. History SHALL order rows by `created_at DESC, sweep_id DESC`; a caller that supplies another actor's sweep ID SHALL receive `404` without learning or changing that resource.

#### Scenario: History is isolated between administrators

- **WHEN** an administrator requests discovery history
- **THEN** the response contains only that principal's sweeps
- **AND** equal timestamps are ordered deterministically by descending `sweep_id`

#### Scenario: Cross-actor detail or command is attempted

- **WHEN** an administrator requests detail, leaderboard, pause, resume or cancel for a sweep owned by another actor
- **THEN** the endpoint returns `404`
- **AND** no state, counter, combination or outbox row changes

### Requirement: Report deferred wake-up publication without losing the intent

When a valid lifecycle command commits a state transition and a durable wake-up intent but broker publication is unavailable, the service SHALL preserve the `pending` outbox intent and return the committed state with an explicit deferred dispatch status. A later dispatcher poll SHALL publish that intent; the client SHALL not be required to repeat a successful resume to recover work.

#### Scenario: Broker is unavailable during resume

- **WHEN** resume changes a paused sweep to `running` and the broker rejects publication
- **THEN** the response reports `state=running`, `wake_up_state=pending` and `dispatch_status=deferred`
- **AND** the pending intent remains durable for dispatcher retry
- **AND** no pending combination is lost or started twice

#### Scenario: Running sweep is repaired after reload

- **WHEN** a running sweep has pending combinations and no pending or delivered wake-up
- **THEN** dispatcher repair creates one pending intent and eventually publishes it without browser-side queue access

### Requirement: Discard stale lifecycle polling responses

The Discovery client SHALL associate each sweep-detail poll with a monotonically increasing request revision and SHALL ignore a response older than the latest applied revision or server `updated_at`. It SHALL use single-flight polling or cancellation so an older running response cannot overwrite a newer terminal or paused state.

#### Scenario: Delayed running response arrives after terminal

- **WHEN** a delayed `running` poll response arrives after a newer `completed` response was applied
- **THEN** the client keeps the terminal state and does not restart polling

#### Scenario: Delayed historical response arrives after a new selection

- **WHEN** a leaderboard response for a previous `viewSweep` arrives after a newer selection
- **THEN** the client discards the old response and keeps rows, metadata and filters for the selected run

## MODIFIED Requirements

### Requirement: Enqueue atomically through an at-least-once outbox and reconcile delivery

Sweep, combinations and enqueue intents SHALL commit in one database transaction. The chosen topology SHALL publish **one orchestrator job per sweep wake-up**, not one durable queue job per combination. The orchestrator payload SHALL contain only idempotent identity (`sweep_id`, orchestration generation/version), then claim combinations from PostgreSQL in bounded batches. Queue and outbox delivery semantics SHALL be at-least-once: a broker may accept a publish and the dispatcher may crash before acknowledging that delivery in PostgreSQL, so the reconciler SHALL redeliver the same idempotent orchestrator payload. Queue publication SHALL never be the sole record that work exists.

The dispatcher SHALL read at most `100` due outbox rows per poll, publish at most `20` per batch, and enforce configurable global/per-sweep outstanding-orchestrator limits (defaults `8` global and `1` per sweep). Each orchestrator activation SHALL claim at most `20` combinations and SHALL reschedule a wake-up only while claimable work remains. These values SHALL be configuration/versioned; queue depth/backpressure SHALL stop new publication without losing committed intents. Result commit and queue ACK SHALL be separate idempotent steps, with unique combination/result keys making redelivery safe. A `running` sweep with claimable combinations and no `pending` or `delivered` wake-up SHALL be repaired into one durable `pending` outbox intent before publication.

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

#### Scenario: Running sweep has an ACKed wake-up and pending combinations

- **WHEN** a running sweep has at least one pending combination, no delivered wake-up and only an ACKed or missing outbox intent
- **THEN** the dispatcher creates exactly one monotonic next-generation pending wake-up for that sweep under a sweep-row lock
- **AND** publication happens only after the pending intent is committed
- **AND** repeated repair calls do not create duplicate wake-ups or duplicate results

#### Scenario: Orchestrator rotates to the next batch durably

- **WHEN** an orchestrator finishes a claimed batch and reconciles that the running sweep still has claimable combinations
- **THEN** it commits the next pending wake-up before acknowledging the current delivery
- **AND** a broker or process failure between those steps leaves at least one durable intent that can be redelivered

#### Scenario: Initial start is interrupted after the database commit

- **WHEN** a sweep and its pending outbox intent are committed while the parent sweep is still `pending`, but the process stops before the initial dispatcher transition
- **THEN** the dispatcher atomically transitions the parent to `running` under its sweep-row lock before publishing or allowing a claim
- **AND** the committed combinations are eventually claimable without creating another sweep or intent for the same generation

### Requirement: Pause, resume and cancel respect already-enqueued jobs

Pause SHALL move only `pending`/`running` work to `paused` and prevent new optimizer starts. Jobs already present in the external queue MAY wake, but their worker SHALL transactionally recheck parent state and release/retain them pending without starting optimizer work. Resume SHALL move only `paused` work to `running` and SHALL ensure one durable orchestrator wake-up whenever claimable combinations remain, including when the previous outbox intent is already ACKed. Cancel SHALL move `pending`/`running`/`paused` to `cancelling`, apply the same start barrier, mark pending work skipped and await active leases before `cancelled`. Every lifecycle command SHALL lock and re-read the sweep row, enforce actor ownership, and serialize transitions so `cancelling` remains the prevailing intent. Pause/resume during `cancelling` SHALL be rejected because cancellation prevails. Repeated valid commands SHALL return the current state without duplicate side effects.

#### Scenario: Pause races a queued worker

- **WHEN** pause commits while a queued worker is waking
- **THEN** the worker's transactional state recheck prevents optimizer start
- **AND** the combination remains pending for resume

#### Scenario: Resume after the prior wake-up was ACKed

- **WHEN** a paused sweep has pending combinations and its previous orchestrator outbox intent is `acked`
- **THEN** resume changes the sweep to `running` and records one new monotonic `pending` wake-up before returning success
- **AND** the dispatcher eventually processes the pending combinations
- **AND** a repeated resume or concurrent recovery does not enqueue duplicate durable wake-ups

#### Scenario: Resume with an already-delivered wake-up

- **WHEN** a paused sweep resumes while one wake-up for that sweep is already `delivered`
- **THEN** resume does not create a second outstanding wake-up
- **AND** the delivered worker can claim work after its transactional state recheck

#### Scenario: Cancel races pause and active work

- **WHEN** pause and cancel requests race while one combination holds a valid lease
- **THEN** cancellation wins as the stronger terminal intent
- **AND** no new combination starts, the leased attempt is reconciled, and all remaining pending work becomes skipped

#### Scenario: Lifecycle command targets another actor's sweep

- **WHEN** an administrator sends pause, resume or cancel for a sweep owned by another actor
- **THEN** the service returns `404` without changing the sweep, combinations or outbox

### Requirement: Return reconciled counters for an active sweep

The active-sweep read and sweep detail read SHALL derive or atomically reconcile `succeeded`, `failed`, `skipped` and `processed` from the persisted combination dispositions before returning them. They SHALL preserve `processed = succeeded + failed + skipped` and SHALL never present a stale counter as evidence that a pending combination completed.

#### Scenario: Detail is read after a committed result

- **WHEN** a result commit has settled a combination but the denormalized sweep counters have not yet been refreshed
- **THEN** the read returns counters reconciled from the combination rows
- **AND** `processed` equals the sum of succeeded, failed and skipped dispositions

#### Scenario: Detail is read while combinations remain pending

- **WHEN** a running or paused sweep has pending combinations
- **THEN** the read reports those combinations as not processed
- **AND** it does not mark the sweep terminal or fabricate completion
