## MODIFIED Requirements

### Requirement: Claim work safely with leases, fairness and bounded concurrency

Each combination SHALL have a unique key `(sweep_id, template_id, symbol, timeframe, direction)` and an idempotent handler. A worker SHALL claim a pending combination with a lease in a transaction that rechecks the parent sweep is `running`; only the current owner with matching attempt sequence, generation and unexpired lease may begin/commit that attempt. Claims SHALL count each attempt durably once before spawn and lease only one combination at a time for the sequential worker. Expired leases SHALL be recovered without duplicating committed results and SHALL obey the three-attempt limit, durable 60/300-second backoff and parent state barrier. Scheduling SHALL enforce configurable global and per-sweep concurrency limits and SHALL use fair round-robin/age ordering so one large sweep cannot starve another.

Optimization stage generation SHALL process each correlated parameter group exactly once. A legacy parameter range that provides `min` and `max` but omits `step` SHALL use the optimizer's deterministic coarse-step fallback rather than passing `None` to range generation or failing the combination.

#### Scenario: Two workers claim one combination

- **WHEN** two workers concurrently attempt to claim the same pending combination
- **THEN** exactly one obtains the lease and starts optimizer work
- **AND** the other observes no claimable row

#### Scenario: Lease expires after crash

- **WHEN** a worker crashes after claim but before committing a result
- **THEN** the reconciler preserves a committed result, or only returns work to pending when attempt budget, backoff and parent state permit; exhausted work terminates operationally
- **AND** the idempotent handler/unique result key prevents a duplicate committed result

#### Scenario: Legacy correlated schema omits step

- **GIVEN** a template has a correlated parameter group whose ranges provide `min`, `max` and `default`, but no `step`
- **WHEN** the discovery worker generates optimization stages
- **THEN** each parameter receives a non-null deterministic coarse step and a finite value list
- **AND** stage generation does not duplicate the group or fail with arithmetic against `None`

## ADDED Requirements

### Requirement: Durable bounded recovery across worker loss
Each combination SHALL have at most three started attempts, counted before spawn across OOM, redelivery, task retry and service restart. Retries SHALL repeat the immutable input snapshot after at least 60 then 300 seconds, discarding provisional output. Deterministic calculation errors SHALL terminate without operational retries. Committed results SHALL not execute again. An external reconciler SHALL run every 30 seconds and startup/dispatch, deduplicating wakeups and respecting pause/cancel.

#### Scenario: Death before reporting
- **WHEN** a started attempt dies before reporting and the service restarts
- **THEN** reconciliation accounts the existing attempt once and schedules only the next allowed attempt after durable backoff
- **AND** redelivery cannot reset or exceed three total attempts

#### Scenario: Third operational failure
- **WHEN** the third attempt fails operationally
- **THEN** the combination and sweep fail with operational_failure/resource_recovery_exhausted
- **AND** committed results remain, unresolved unstarted work becomes skipped and processed equals total
- **AND** an operational alert states three attempts were exhausted and intervention is required

#### Scenario: Cancellation during backoff
- **WHEN** cancellation occurs while awaiting retry
- **THEN** no new optimizer starts and existing scoped reconciliation closes cancellation

### Requirement: Heartbeat is separate from progress and fences all writes
Attempts SHALL renew a 300-second lease every 30 seconds using PostgreSQL time and unique owner/attempt/generation. Progress SHALL advance only upon actual trial completion or verified phase progress. No progress for 120 seconds SHALL warn and 600 seconds SHALL abort operationally. Result/failure/insufficient-sample/counter writes SHALL verify current unexpired possession under sweep-then-combination locks. Terminal sweeps SHALL reject new writes; paused/cancelling sweeps MAY settle already active valid leases according to existing lifecycle.

#### Scenario: Thirty-minute step still progressing
- **WHEN** a step runs over thirty minutes with regular progress and heartbeat
- **THEN** no second owner claims it merely because the original 300 seconds elapsed

#### Scenario: Old owner returns
- **WHEN** an expired or replaced owner reports success or failure
- **THEN** its write is rejected without duplicate result or changes to the current attempt

#### Scenario: Heartbeat without progress
- **WHEN** heartbeat continues but actual progress stops for 600 seconds
- **THEN** cleanup begins and the attempt enters bounded operational recovery
