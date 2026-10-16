# combo-optimizer Specification

## Purpose
Support grid-based optimization for correlated parameters with iterative refinement compatibility.
## Requirements
### Requirement: Grid-Based Optimization for Correlated Parameters
The Combo Optimizer SHALL support joint optimization of correlated parameters using Grid Search. When correlated parameters (e.g., media_curta, media_inter, media_longa) are detected, it SHALL create a single joint stage testing all combinations (cartesian product). Fallback to sequential for uncorrelated parameters.

#### Scenario: Joint optimization of correlated MA parameters
- **GIVEN** correlated parameters media_curta, media_inter, media_longa are defined
- **WHEN** grid optimization is triggered
- **THEN** a single joint stage tests all Cartesian combinations
- **AND** uncorrelated parameters fallback to sequential optimization

### Requirement: Iterative Refinement Compatibility
Grid Search SHALL disable Iterative Refinement (max_rounds = 1 when Grid is active) to avoid redundant testing. Independent parameters (e.g., stop_loss) SHALL be optimized sequentially after Grid.

#### Scenario: Grid disables iterative refinement
- **GIVEN** Grid Search mode is active
- **WHEN** optimization runs
- **THEN** max_rounds is set to 1
- **AND** independent parameters are optimized sequentially after Grid

### Requirement: Optimization Final Result Execution Mode
The optimization endpoint SHALL return final trades and metrics generated with the same execution mode used for optimization scoring.

#### Scenario: Deep Backtest requested
- **WHEN** `/api/combos/optimize` runs with `deep_backtest=true`
- **THEN** stage scoring SHALL use Deep Backtest when 15m data coverage is available
- **AND** the final returned trades and metrics SHALL also use the Deep Backtest extraction path.

### Requirement: Hard Mode Deep Candidate Evidence
The combo optimization and backtest evidence used for hard-mode BTC discovery SHALL preserve BTC/USDT, timeframe 1d, long direction, Deep Backtest, initial capital 100 USD, 100 percent entry sizing, 100 percent exit sizing, no partial exits, and no pyramiding.

#### Scenario: Candidate optimization preserves invariants
- **WHEN** a hard-mode BTC run uses `/api/combos/optimize` or an equivalent optimizer path for a candidate
- **THEN** the payload SHALL request Deep Backtest
- **AND** the payload SHALL use BTC/USDT, timeframe 1d, long direction, initial capital 100 USD, 100 percent entry sizing, 100 percent exit sizing, no partial exits, and no pyramiding

#### Scenario: Final candidate count requires deep final backtest
- **WHEN** a hard-mode BTC run counts a candidate toward the executed material candidate budget
- **THEN** the candidate SHALL have a final Deep Backtest result with deep execution mode evidence
- **AND** theoretical optimizer combinations, duplicate parameters, revalidations, renamed strategies, and non-deep results SHALL NOT count toward the budget

#### Scenario: Benchmarks use the same capital model
- **WHEN** a hard-mode BTC run revalidates current Favorites or references such as multi-ma and buy-and-hold
- **THEN** the benchmark payload SHALL use the same Deep Backtest, capital, sizing, direction, timeframe, and no-partial/no-pyramiding constraints as candidate payloads

### Requirement: Modern Combo Execution Supports Direction

The combo optimizer SHALL execute modern combo strategies through a direction-aware trade extraction path that supports `long` and `short`.

#### Scenario: Short trade profit follows inverse price movement

- **GIVEN** a combo strategy emits `signal == 1` as entry and `signal == -1` as exit
- **AND** the execution direction is `short`
- **WHEN** exit price is below entry price
- **THEN** the resulting trade profit SHALL be positive

#### Scenario: Short stop loss is above entry

- **GIVEN** a short combo trade entered at a price
- **WHEN** a later candle high reaches the configured stop above entry
- **THEN** the trade SHALL close as a stop loss

#### Scenario: Long default is preserved

- **GIVEN** a combo request omits direction
- **WHEN** the optimizer executes the strategy
- **THEN** direction SHALL default to `long`
- **AND** existing long stop/profit behavior SHALL remain unchanged

### Requirement: Combo Signal Generation Must Not Apply Long-Only Stops To Shorts

`ComboStrategy.generate_signals` SHALL NOT emit a short exit merely because candle low moved below entry as a long-style stop.

#### Scenario: Falling price does not stop a short

- **GIVEN** a strategy is evaluated with direction `short`
- **AND** the active entry price is above a later candle low
- **WHEN** the low movement would be profitable for a short
- **THEN** signal generation SHALL NOT create a stop-loss exit for that low movement

### Requirement: Common accelerated path for every Discovery catalog strategy

The combo optimizer SHALL run every strategy the Discovery scan accepts (the versioned export of 11 pre-built plus 3 examples: `Bollinger_Breakout`, `MACD_Cross`, `RSI_EMA_Scalping`, `bollinger_rsi_adx`, `ema_macd_volume`, `ema_rsi`, `ema_rsi_fibonacci`, `multi_ma_crossover`, `multi_ma_crossoverV2`, `short_ema200_pullback`, `volume_atr_breakout`, `Example: Breakout with Volume`, `Example: Scalping EMA 5/13`, `Example: Swing RSI Divergence`) through the same accelerated path (`run_combination` → `ComboOptimizer.run_optimization` → `_worker_run_batch` → `_run_backtest_logic` → `ComboStrategy.generate_signals` plus Deep 15m). Custom/quant templates outside that set SHALL NOT be this change's clock proof or golden. The path SHALL NOT branch on `multi_ma` / SMA. 4h SHALL use the same path without its own 14,8 s bar.

#### Scenario: Another catalog template uses the same accelerated runner

- **GIVEN** a Discovery catalog template other than `multi_ma_crossover`
- **WHEN** the sweep optimizes that template
- **THEN** it uses the same accelerated path (indicators cached by that template's resolved-parameter key, common signal loop and Deep 15m)
- **AND** it SHALL NOT take an `if multi_ma` / SMA-only branch

#### Scenario: 4h inherits the path without its own clock bar

- **GIVEN** Discovery accepts 4h and 1d
- **WHEN** a 4h combination runs
- **THEN** it uses the same accelerated path
- **AND** it SHALL NOT be required to finish in 14,8 s

### Requirement: Laboratory, batch, and favorite revalidation share the accelerated path

Laboratory combo optimize, batch generate, favorite revalidation, and favorite regenerate SHALL call the same accelerated ComboOptimizer path as the Discovery scan in this change. They SHALL NOT keep a parallel slow runner. They SHALL NOT have their own 14,8 s bar. A defect in the fast path SHALL be visible on those screens until the legacy switch or git revert.

#### Scenario: Operator optimizes from laboratory, batch, or favorite revalidation

- **WHEN** the operator starts optimize from the combo laboratory, batch generate, or favorite revalidation / regenerate
- **THEN** that call uses the same accelerated path as the scan
- **AND** it SHALL NOT use a leftover slow branch on those screens
- **AND** it SHALL NOT be judged by a 14,8 s wall-clock of its own

### Requirement: Clock proof is the Discovery DEV service not automated tests

A representative combination `multi_ma_crossover` × `1INCH/USDT` × `1d` × long (`period_type=all`, `deep_backtest=True`, `split_train_ratio=0.7`) SHALL finish in ≤ 14,8 s of wall-clock **and** R1–R4 summed SHALL be ≤ 11 s on the **same Discovery DEV service** that measured the 148 s journal baseline, with that pair's 1d+15m candles already on disk covering the period end. Automated tests SHALL pass or fail by exact numeric goldens, NEVER by wall-clock. A first combination of a still-cold pair MAY exceed 14,8 s because of fetch; that SHALL NOT fail this change.

#### Scenario: Representative combination on Discovery DEV with candles on disk

- **GIVEN** the journal baseline of `1INCH/USDT` 1d long = 148 s on the Discovery DEV service
- **WHEN** an equivalent combination runs on that same service (`run_combination` → `ComboOptimizer.run_optimization` with `deep_backtest=True` and `split_train_ratio=0.7`, 1d+15m candles of that pair already on disk covering the period end)
- **THEN** the whole combination clock is ≤ 14,8 s
- **AND** R1–R4 summed are ≤ 11 s

#### Scenario: Automated tests do not use wall-clock as the gate

- **WHEN** the automated golden suite runs on CI or a laptop
- **THEN** the change passes or fails by exact equality goldens
- **AND** a slower test machine or fewer cores SHALL NOT fail the change

#### Scenario: Cold pair fetch may exceed the bar

- **WHEN** the first combination of a pair whose 1d/15m candles are not yet on disk covering the period end runs
- **THEN** exceeding 14,8 s because of fetch SHALL NOT fail this change

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

### Requirement: Indicator and mask cache keyed by resolved params and window

Each worker process SHALL cache indicators and entry/exit masks. The cache key SHALL include indicators **already resolved** by `_run_backtest_logic`'s four override rules (type/alias/final params), `entry_logic`, `exit_logic`, `derived_features`, **and** the `df` window identity (first/last timestamp, `len`, hash of `open/high/low/close/volume`). A key of symbol/params without window SHALL NOT be valid. `stop_loss` SHALL stay **outside** the key and SHALL remain in the position loop. Cache output SHALL be immutable (read-only arrays or `copy()` on read); no trial SHALL write into a cached object. Dtype coercion SHALL remain `pd.to_numeric(errors="coerce")` → `float64`/`NaN`. Train, holdout+burn-in, and final series are distinct windows.

#### Scenario: Same params on two windows do not cross-hit

- **GIVEN** two different windows with the same params and a hot cache
- **WHEN** the second window is evaluated
- **THEN** there is no cache hit across windows
- **AND** the test asserts the keys differ

#### Scenario: Stop is not part of the indicator cache key

- **GIVEN** two trials that differ only in `stop_loss` on the same window
- **WHEN** the second trial runs
- **THEN** indicators and logic masks MAY be reused
- **AND** the position loop still applies that trial's `stop_loss`
- **AND** reusing the finished **signal series** across stops SHALL NOT be treated as equivalent

#### Scenario: Cached object is not mutated

- **GIVEN** a trial that would assign `df["signal"]`
- **WHEN** it runs against a cached indicator object
- **THEN** the cached object remains unchanged for later trials

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

### Requirement: Deterministic result order before score

Before scoring, trial results SHALL be ordered by batch/trial index or by a params tie-break. `as_completed` arrival order SHALL NOT decide exact score ties. Two runs of the same combination on the same parquet SHALL pick the same round-top winner when scores tie exactly.

#### Scenario: Exact score tie picks the same winner twice

- **GIVEN** two runs of the same combination on the same parquet
- **WHEN** an exact score tie exists at the top of a round
- **THEN** the winner is the same in both runs

### Requirement: Exact indicator golden against frozen oracle

For **each** Discovery-accepted strategy (11+3), on frozen parquet, for ≥ 50 params sampled from grid R1, `calculate_indicators` on the new path and on the frozen oracle SHALL run on the **three windows** (train 70%, holdout + burn-in, final series). Each indicator column (`EMA_*`, `SMA_*`, `RSI_*`, `*_macd/_signal/_histogram`, `*_upper/_middle/_lower`, `ATR_*`, `ADX_*`, `ROC_*`, `VOL_SMA_*`, aliases, and `derived_features`) SHALL be equal with `np.testing.assert_array_equal` (`NaN` in the same position), same `dtype` (`float64`), and the same column set/order. `sha256(col.tobytes())` SHALL match the versioned fixture. Zero tolerance.

#### Scenario: Indicator columns match oracle on three windows

- **GIVEN** frozen parquet and, for each Discovery-accepted strategy, ≥ 50 R1 params
- **WHEN** `calculate_indicators` of the new path and of the oracle run on train 70%, holdout + burn-in, and the final series
- **THEN** every indicator column is equal under `np.testing.assert_array_equal`
- **AND** `NaN` positions, `float64` dtype, and column set/order match
- **AND** `sha256(col.tobytes())` matches the versioned fixture

### Requirement: Exact mask golden

For the same cases as the indicator golden, `_evaluate_logic_vectorized(entry_logic)` and `(exit_logic)` on the new path and on the oracle SHALL produce identical boolean series, including `RSI_14` / `EMA_n` / `SMA_n` / `ATR_n` / `ADX_n` compatibilities that depend on `self.indicators`.

#### Scenario: Entry and exit masks match oracle

- **GIVEN** the same frozen parquet cases as the indicator golden
- **WHEN** `_evaluate_logic_vectorized` runs for `entry_logic` and `exit_logic` on the new path and on the oracle
- **THEN** the boolean series are identical

### Requirement: Cache cold, hot, and A-B-A leave identical bytes

Given a trial, running with cache off, then cache on, then A → B → A (B with different params on the same window) SHALL produce identical indicator bytes, masks, `trades`, and `metrics` on all three executions.

#### Scenario: Cold, hot, and A-B-A match

- **GIVEN** a trial
- **WHEN** it runs with cache off, then with cache on, then A → B → A on the same window
- **THEN** indicator, mask, `trades`, and `metrics` bytes are identical across those executions

### Requirement: Exact per-trial trade and metrics golden including short and fast_1d

For frozen parquet of ≥ 2 symbols and **each** Discovery-accepted strategy, long **and** short, ≥ 50 R1 params (including extreme stops), a trial on the new path and on the frozen `_run_backtest_logic` oracle SHALL produce **identical** `trades` (`entry_time`, `exit_time`, `entry_price`, `exit_price`, `profit`, `exit_reason`) and `metrics`. Zero divergences. The golden SHALL also cover the `fast_1d` fallback (`extract_trades_from_signals`). Short SHALL be covered even when a scan template without direction metadata is long-only, because the laboratory MAY request short.

#### Scenario: Trial trades and metrics match oracle for long and short

- **GIVEN** frozen parquet of ≥ 2 symbols and each Discovery-accepted strategy, long and short, ≥ 50 R1 params including extreme stops
- **WHEN** the trial runs on the new path and on the frozen oracle
- **THEN** `trades` and `metrics` are identical
- **AND** zero divergences

#### Scenario: fast_1d fallback matches oracle

- **GIVEN** a trial that lacks 15m coverage and takes `fast_1d`
- **WHEN** it runs on the new path and on the oracle
- **THEN** `trades` and `metrics` are identical

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

### Requirement: Apply floors — oracle first, then speed; pin scientific libs

The first commit on the card branch SHALL contain **only** the frozen oracle (`backend/tests/oracles/card_945_legacy.py`, a literal copy of current `calculate_indicators`, `_evaluate_logic_vectorized`, `generate_signals` loop, `simulate_execution_with_15m`, `extract_trades_from_signals`, `_metrics_from_trades`), versioned parquet fixtures (≥ 2 symbols, 1d + 15m) plus per-column / per-trade-list sha256, and golden tests passing against **current** product code. Later speed commits SHALL NOT touch oracle or fixtures. A fixture diff SHALL block review unless the PR writes a justification. When the card closes, `TA-Lib`, `numpy`, and `pandas` SHALL be pinned in the backend lock to the versions in use on the VPS, and the golden report SHALL record those versions.

#### Scenario: First commit is oracle, fixtures, and green goldens only

- **GIVEN** the card branch
- **WHEN** the first commit is made
- **THEN** it contains only oracle + fixtures + golden tests passing against current code
- **AND** product optimizer code is untouched
- **AND** later speed commits do not touch oracle or fixtures

#### Scenario: Scientific libs are pinned

- **GIVEN** `pip freeze` of the backend venv
- **WHEN** the card closes
- **THEN** `TA-Lib`, `numpy`, and `pandas` are pinned in the lock to the versions in use today
- **AND** the golden test report records those versions

### Requirement: Selective git revert and runtime kill-switch until Homologado

Apply SHALL comment `baseline-945=<sha of origin/develop>` at start. The branch SHALL have at least one commit A (oracle/fixtures/tests, product intact) and at least one commit B (speed only) that are not squashed into each other. `git revert` of B SHALL apply without conflict with A. Emergency after merge SHALL be `git revert -m 1 <merge-sha>` on `develop` (a new commit), never `reset --hard` or force-push. Until Homologado, current slow functions SHALL remain in product files as `_legacy_*`. `COMBO_OPTIMIZER_LEGACY=1` on **every** service that runs the engine (scan, laboratory, batch, revalidation / regenerate) SHALL call `_legacy_*` (current numbers) on **all** those screens; default without the flag SHALL be the fast path. The equivalence golden SHALL keep comparing fast vs legacy. This change SHALL NOT delete `_legacy_*` or the oracle. Git revert SHALL NOT erase already persisted sweep `result_id`s.

#### Scenario: Review sees A and B and baseline-945

- **GIVEN** the branch log
- **WHEN** review runs
- **THEN** there is at least one commit A (oracle/fixtures/tests, product intact) and at least one commit B (speed only)
- **AND** `git revert` of B applies without conflict with A
- **AND** the card comment has `baseline-945=<sha>`

#### Scenario: Kill-switch restores legacy on every engine screen

- **GIVEN** `COMBO_OPTIMIZER_LEGACY=1` on the service that runs the engine
- **WHEN** the scan, laboratory, batch, or favorite revalidation / regenerate runs
- **THEN** it uses `_legacy_*` (current numbers) on all those screens
- **AND** the equivalence golden still compares fast vs legacy
- **AND** default without the flag is the fast path

#### Scenario: Setup skip does not touch sweep preflight

- **GIVEN** 1d and 15m candles of that pair already on disk covering the period end
- **WHEN** a later combination of that pair starts
- **THEN** the per-combination setup MAY skip the exchange tail check
- **AND** sweep preflight remains unchanged

### Requirement: Combo path runs Entra timeframes with table slippage and VWAP

The Combo optimization and backtest path SHALL run `15m` and `1h` with the same engine path used for `4h` and `1d`, applying `backtest-slippage-by-timeframe` and evaluating templates that reference daily or rolling VWAP. It SHALL NOT add a daily-trend filter, hour-of-day rule, ATR stop, or funding model.

Combo MAY continue to accept 1m, 5m and 30m as it already does; those intervals SHALL NOT gain Discovery acceptance or a new slippage row in this change.

#### Scenario: 1h combination uses the shared optimizer path

- **WHEN** Combo or Discovery optimizes a template on 1h
- **THEN** execution uses the existing combination path
- **AND** 0,03% per-side slippage is applied
- **AND** no 1D trend filter is consulted

#### Scenario: VWAP template runs through Combo

- **WHEN** a template with daily VWAP or rolling VWAP is optimized on 15m, 1h or 4h
- **THEN** signal generation completes without error

### Requirement: Incremental acceleration preserves exact current engine results
The shared combo engine SHALL preserve the post-945 engine's complete search, parameters, rounds, filters, scoring, tie-breaking, indicators, masks, trades, costs, train/holdout metrics and GO/NO-GO under #1091 acceleration. TA-Lib, PnL/metric formulas, public contracts and common Discovery/laboratory/batch/favorites consumers SHALL remain equivalent. Holdout SHALL NOT influence parameter selection.

#### Scenario: Full reference optimization
- **WHEN** both engines run frozen Multi-MA/1INCH/1d/long with Deep 15m, 70/30 split and three workers
- **THEN** both execute 21,210 trials with zero failed trials and exactly equal complete results without tolerance or rounding
- **AND** trade dates, prices, profit, exit reasons, indicators, masks and train/holdout outcomes match

#### Scenario: Catalog and execution modes
- **WHEN** 14 catalog templates, two symbols, long/short, 1d/4h, Deep and applicable daily fallback are exercised
- **THEN** current-engine results and consumer contracts remain exact, including stop/signal conflicts and insufficient intraday coverage

### Requirement: Cached execution is isolated immutable and bounded
Caches SHALL reuse only equivalent complete data, indices, windows, resolved parameters and relevant execution contexts. They SHALL enforce retained-byte and entry limits and SHALL NOT expose mutable shared results. Train, holdout with burn-in and final evaluation SHALL preserve separate contexts and existing evaluation boundaries.

#### Scenario: Data changes and repeated windows
- **WHEN** an internal candle or timestamp changes while endpoints and length remain equal, or execution runs A then B then A
- **THEN** each execution uses correct current data and produces the uncached result exactly

#### Scenario: Mutation and eviction
- **WHEN** a trial attempts to modify reused data or a cache reaches its limit
- **THEN** another trial cannot observe changed shared data and eviction only causes recomputation within the budget

#### Scenario: Holdout warmup
- **WHEN** holdout uses train tail for indicator burn-in
- **THEN** the existing burn-in and trade-entry filter remain exact without cache contamination or selection leakage

### Requirement: Consistent measured incremental gain
Acceptance SHALL use five alternating warmed pairs on identical hardware, frozen data and three workers with full equivalence. Optimized median SHALL be lower and at least three pairs SHALL improve. Twenty-five percent SHALL remain an objective, not a required floor. Evidence SHALL include individual durations, dispersion, code/dependencies, initial compilation and memory. CI correctness SHALL NOT use wall-clock deadlines.

#### Scenario: Gain below objective
- **WHEN** median and at least three pairs improve with exact results even below 25 percent
- **THEN** the primary performance criterion passes without reducing search coverage, rounds or workers

#### Scenario: Secondary cases and indicator cache
- **WHEN** AAVE short and EMA+RSI/1INCH long receive five repeated pairs and indicator cache is compared against fingerprint plus Numba
- **THEN** secondary scenarios show no sustained regression (worse median and majority worse), and indicator cache is included only with measured additional benefit within memory limits

### Requirement: Fallback rollback and durable evidence
The engine SHALL preserve validated rollback to the current post-945 engine independently from the pre-945 legacy switch. Missing/unsupported compilation SHALL use equivalent current Python execution with an operational diagnostic. Missing TA-Lib SHALL NOT introduce substitute indicators. Compatible pins, reproducible harness, input hashes and raw reports SHALL be durable; no new operator setting SHALL be introduced.

#### Scenario: Compilation absent or incremental acceleration disabled
- **WHEN** compilation is unavailable or all #1091 components are disabled in a fresh process
- **THEN** the current post-945 result and public contract remain equivalent
- **AND** the pre-945 switch retains its existing meaning and precedence

#### Scenario: Reproduce evidence
- **WHEN** a reviewer uses the versioned harness, frozen input manifest, revisions and dependency pins
- **THEN** the evidence is reproducible without temporary investigation paths and JIT preparation is reported separately from warmed motor time

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

