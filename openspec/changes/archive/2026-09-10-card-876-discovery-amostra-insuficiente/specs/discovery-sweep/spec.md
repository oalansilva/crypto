## ADDED Requirements

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

## MODIFIED Requirements

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
