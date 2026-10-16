## MODIFIED Requirements

### Requirement: Speed only — identical talib calls and float expressions

No trading rule or calculation SHALL change except the explicit runtime binding of RSI_14/ADX_14 to effective candidate indicators in long_ma_pullback_rsi_adx, specified below. Thresholds, comparison operators and formulas SHALL remain unchanged. Indicators SHALL still come from the same `talib.*` calls in `ComboStrategy.calculate_indicators` on the same series (same function, same arguments). The cache SHALL store the **output** of those calls and SHALL NOT reimplement EMA/SMA/RSI/MACD/BBANDS/ATR/ADX/ROC. Position loop, Deep 15m simulation, and `fast_1d` fallback SHALL be rewritten with the **same expressions** and the same float operation order, not «equivalent» formulas. PnL, fee `0.00075`, stop (`entry*(1-stop)` / `(low-entry)/entry <= -stop`), score `0.7*ns + 0.3*nr`, min/max normalization, and `_metrics_from_trades` / `_calculate_heavy_metrics` SHALL keep the current calls (no vectorized reductions that change pairwise summation). Grid, steps, round count, `top_k`, `BATCH_SIZE` meaning, `short<inter<long` heuristic, `_select_top_candidates`, and holdout burn-in SHALL remain. Workers SHALL be configured by environment/resource budget; DEV uses one. Batches MAY shrink for byte limits without changing candidates. Equivalence tests SHALL use exact equality (`np.testing.assert_array_equal`, identical trade fields) with zero `allclose` / `rtol` / rounding.

#### Scenario: Review sees no formula or talib change

- **WHEN** review inspects `git diff` of this change
- **THEN** there is no change to PnL / fee / stop / score / metrics formulas
- **AND** `talib.*` calls keep the same function and arguments
- **AND** outside the explicit RSI/ADX binding correction, only *when* and *how many times* a value is computed may change
- **AND** the reviewer lists each rewritten function beside the original

#### Scenario: Goldens reject tolerance

- **WHEN** an equivalence test of this change is written
- **THEN** it SHALL NOT use `allclose`, `rtol`, or rounding
- **AND** it SHALL compare with exact equality

### Requirement: One combination in flight and R2–R4 occupying the worker pool

A sweep SHALL keep at most one combination in flight (`OUTBOX_MAX_PER_SWEEP=1`). Within a combination, R2–R4 SHALL admit the round's branch batches incrementally, at most 2×effective_workers unconsumed futures and 64 MiB pending serialized bytes; DEV SHALL use one worker and batches of at most 200, without changing per-round selection. Parallelizing branches inside a combination SHALL NOT raise sweep concurrency.

#### Scenario: Sweep still runs one combination at a time

- **GIVEN** a sweep with work remaining
- **WHEN** combinations are leased
- **THEN** at most one combination is in flight
- **AND** `OUTBOX_MAX_PER_SWEEP` remains 1

#### Scenario: R2–R4 branches share configured workers

- **GIVEN** a round with 10 independent branches
- **WHEN** R2, R3, or R4 runs
- **THEN** the configured pool receives all branches through the bounded admission window
- **AND** per-round candidate selection is unchanged

### Requirement: Winner, holdout, and eligibility stay on Deep plus walk-forward

On representative previously valid combinations over frozen parquet, `run_optimization` before and after the change with deterministic order SHALL yield the same `best_parameters`, `best_metrics`, holdout metrics, and GO/NO-GO verdict. Persisted eligibility (`eligible` / `low_sample` / `insufficient_sample`), ranking inputs, and winning parameters SHALL still come from the optimizer contract (Deep 15m + train/holdout), not from a fast-only grid. Preflight/create SHALL remain unchanged. Lease/reconcile/persistence SHALL additionally enforce durable attempts and fencing from discovery-sweep; numeric output stays unchanged for previously valid cases. Previously invalid indicator-period candidates SHALL follow the approved independent corrected semantic oracle; a newly complete search MAY select different winners or GO/NO-GO outcomes without changing ranking formulas or coverage.

#### Scenario: Representative winner matches across the change

- **GIVEN** a previously valid representative combination on frozen parquet
- **WHEN** `run_optimization` runs with deterministic order before and after the speed change
- **THEN** `best_parameters`, `best_metrics`, holdout metrics, and GO/NO-GO are equal

#### Scenario: Persisted best is not a fast-only grid

- **GIVEN** the same grid and the same Deep+WF contract
- **WHEN** the best is persisted
- **THEN** eligibility, ranking inputs, and winning parameters do not come from a fast-only grid

## ADDED Requirements

### Requirement: Exact global ranking with bounded retention
The optimizer SHALL lazily generate the identical grid/trial order and retain results within 128 MiB RAM and 2 GiB private disk spool per attempt. It SHALL calculate complete-domain extrema before scoring per stage/branch exactly as the reference, preserving float expressions, trial-index ties, intermediate candidates and diversity. Batch-local normalization and premature top-k SHALL NOT change output. Quota/I/O failure SHALL abort without truncating search.

#### Scenario: Final batch changes the extrema
- **WHEN** the last batch contains minimum/maximum metrics and score ties span batches
- **THEN** winners, score, complete ordering, diversity and holdout match the applicable deterministic reference (historical valid cases or independent corrected semantic oracle) without tolerance or rounding

#### Scenario: Spool quota exceeded
- **WHEN** the 2 GiB quota or disk I/O fails
- **THEN** the attempt fails operationally without publishing a provisional winner

### Requirement: Incomplete trials cannot advance a round
The optimizer SHALL record planned, executed, succeeded, failed, unknown and remaining per attempt/stage; executed=succeeded+failed and planned=executed+unknown+remaining. Executed SHALL count confirmed outcomes rather than submissions. Stages SHALL advance only when all planned trials are confirmed successful. Pool loss and calculation errors SHALL never yield fallback winners or silent success; valid no-signal calculations remain successful.

#### Scenario: Pool dies after partial progress
- **WHEN** 32,000 of 492,480 trials have confirmed outcomes and the pool breaks
- **THEN** executed stays 32,000, submitted unconfirmed work is unknown and unsubmitted work remains remaining
- **AND** no next round or successful combination is persisted

#### Scenario: Valid no-signal calculation
- **WHEN** a valid trial completes without signals
- **THEN** it counts as successful with the same reference output


### Requirement: Original strategy binds declared indicators to effective candidate periods
For `long_ma_pullback_rsi_adx`, the runtime SHALL apply versioned policy `effective-indicators-v1` after checking the original declaration contains exactly one unaliased RSI and one unaliased ADX, both originally length 14. It SHALL preserve their identities before overrides and bind only whole expression identifiers RSI_14/ADX_14 to those instances' effective series, before unknown-identifier validation. This SHALL apply to entry/exit, optimizer, final training, holdout, Deep/fallback and other consumers of that template. The stored template SHALL NOT be migrated or mutated by this correction. Thresholds, operators, MA/pullback, stops, fees, TA-Lib formulas, grid, rounds, ranking normalization and tie-breaks SHALL remain unchanged.

#### Scenario: Mixed candidate periods
- **WHEN** the original strategy candidate has rsi_length=10 and adx_length=20
- **THEN** entry RSI_14 and exit RSI_14 both use TA-Lib RSI length 10, and ADX_14 uses TA-Lib ADX length 20
- **AND** other rules and the full R1 candidate set of 492,480 remain unchanged, followed by all subsequent generated rounds

#### Scenario: Already valid candidate
- **WHEN** the candidate uses RSI/ADX length 14/14
- **THEN** indicator arrays, masks, trades, metrics and holdout equal the frozen valid baseline exactly without tolerance or rounding

### Requirement: Binding validation rejects ambiguity without global reinterpretation
The explicit binding SHALL use declared producer identity rather than string replacement, dataframe-name heuristics or first-match selection. Ambiguous/duplicate producers, conflicting symbol origins, missing effective series, incompatible original declarations and unknown identifiers SHALL raise indicator_reference_error as deterministic calculation_error, with no operational retry, false mask, winner or successful result. Existing stable aliases and unrelated literal references SHALL retain their meaning. Other templates SHALL retain their existing behavior; the correction SHALL NOT globally remap arbitrary period tokens. Cache identity SHALL include policy version, binding identity and effective parameters.

#### Scenario: Unknown reference and ambiguous producer
- **WHEN** logic references RSI_140 or ADX_99 without a declared valid producer, or the policy encounters duplicate RSI/ADX instances or symbol-origin collision
- **THEN** evaluation fails explicitly rather than binding by similarity or returning a no-trade success

#### Scenario: Compatibility and cache isolation
- **WHEN** valid existing aliases/literal references and other templates run, or the original template runs A→B→A with changed periods
- **THEN** existing reference semantics remain unchanged and no cached mask or indicator crosses incompatible effective bindings

### Requirement: Newly valid search has an independent semantic baseline
Previously invalid period candidates SHALL be compared exactly against a versioned independent oracle calculating TA-Lib at the effective periods and evaluating the original entry/exit expressions with explicit intended series. The oracle SHALL NOT call the new resolver. Tests SHALL cover every period pair present in the original 10..20 grid, mixed 10/14/20 periods, thresholds, entry/exit, warm-up NaNs, final/holdout and cache eviction. Previously valid cases SHALL retain the historical baseline. Full-search ranking SHALL compare against the corrected complete oracle, not prior incomplete output. Historical persisted results SHALL not be rewritten.

#### Scenario: Restored coverage changes winner
- **WHEN** previously invalid candidates now compute successfully and one wins the full search
- **THEN** the new winner and GO/NO-GO MAY differ from prior incomplete output, but MUST exactly match the approved corrected oracle using unchanged ranking and all candidates
- **AND** no tolerance, reduced grid, always-14 indicator or masked unknown reference is accepted
