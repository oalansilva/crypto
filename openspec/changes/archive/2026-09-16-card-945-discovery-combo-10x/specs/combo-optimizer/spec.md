## ADDED Requirements

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

No trading rule or calculation SHALL change. Indicators SHALL still come from the same `talib.*` calls in `ComboStrategy.calculate_indicators` on the same series (same function, same arguments). The cache SHALL store the **output** of those calls and SHALL NOT reimplement EMA/SMA/RSI/MACD/BBANDS/ATR/ADX/ROC. Position loop, Deep 15m simulation, and `fast_1d` fallback SHALL be rewritten with the **same expressions** and the same float operation order, not «equivalent» formulas. PnL, fee `0.00075`, stop (`entry*(1-stop)` / `(low-entry)/entry <= -stop`), score `0.7*ns + 0.3*nr`, min/max normalization, and `_metrics_from_trades` / `_calculate_heavy_metrics` SHALL keep the current calls (no vectorized reductions that change pairwise summation). Grid, steps, round count, `top_k`, `BATCH_SIZE` meaning, `max_workers`, `short<inter<long` heuristic, `_select_top_candidates`, and holdout burn-in SHALL remain. Equivalence tests SHALL use exact equality (`np.testing.assert_array_equal`, identical trade fields) with zero `allclose` / `rtol` / rounding.

#### Scenario: Review sees no formula or talib change

- **WHEN** review inspects `git diff` of this change
- **THEN** there is no change to PnL / fee / stop / score / metrics formulas
- **AND** `talib.*` calls keep the same function and arguments
- **AND** only *when* and *how many times* a value is computed may change
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

A sweep SHALL keep at most one combination in flight (`OUTBOX_MAX_PER_SWEEP=1`). Within a combination, R2–R4 SHALL submit the round's branch batches to the pool together (or with a batch smaller than 200) so the three workers stay busy, without changing per-round selection. Parallelizing branches inside a combination SHALL NOT raise sweep concurrency.

#### Scenario: Sweep still runs one combination at a time

- **GIVEN** a sweep with work remaining
- **WHEN** combinations are leased
- **THEN** at most one combination is in flight
- **AND** `OUTBOX_MAX_PER_SWEEP` remains 1

#### Scenario: R2–R4 branches share the three workers

- **GIVEN** a round with 10 independent branches
- **WHEN** R2, R3, or R4 runs
- **THEN** the pool receives that round's branch batches together
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

On the representative combination over frozen parquet, `run_optimization` before and after the change with deterministic order SHALL yield the same `best_parameters`, `best_metrics`, holdout metrics, and GO/NO-GO verdict. Persisted eligibility (`eligible` / `low_sample` / `insufficient_sample`), ranking inputs, and winning parameters SHALL still come from the optimizer contract (Deep 15m + train/holdout), not from a fast-only grid. Preflight, create, lease, reconcile, and idempotent persistence SHALL remain unchanged.

#### Scenario: Representative winner matches across the change

- **GIVEN** the representative combination on frozen parquet
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
