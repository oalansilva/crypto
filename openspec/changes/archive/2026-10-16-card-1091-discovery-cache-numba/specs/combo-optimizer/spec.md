## ADDED Requirements

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
