## MODIFIED Requirements

### Requirement: Capture complete T0 before search
The execution MUST capture a timestamped T0 snapshot for BTC/USDT 1d long before any optimization, exploratory backtest, template mutation, Favorite save, Pine generation, or durable report generation.

#### Scenario: T0 exists before technical search
- **WHEN** the run begins after card creation and Project `Status=In Progress`
- **THEN** the snapshot includes current Favorites, direction counts, templates, public mappings, related Pine scripts, and current same-direction Favorite deep revalidation payload/results before candidate search starts
- **AND** the snapshot records whether `COLD_START_MODE` is true because no valid same-direction Favorites exist.

### Requirement: Enforce hard BTC deep backtest invariants
Every benchmark, candidate, finalist, saved Favorite, and Pine artifact MUST preserve BTC/USDT, 1d, long, `deep_backtest=true`, initial capital 100 USD, 100% entry, 100% exit, no partial exits, no pyramiding, no leverage, and no residual position.

#### Scenario: Candidate violates sizing or execution mode
- **WHEN** a payload, result, template, Favorite, or Pine artifact violates any invariant
- **THEN** the candidate is invalid and does not count toward benchmarks, quotas, finalists, or final delivery.

#### Scenario: Direction remains single-direction
- **WHEN** candidates, references, benchmarks, Favorites, or Pine scripts are evaluated
- **THEN** only Long-compatible evidence may be used for this execution
- **AND** Short strategies or references are discarded and recorded as incompatible instead of being used as fallbacks.

#### Scenario: SHORT engine support is missing
- **WHEN** the configured direction is SHORT and the engine cannot prove true SHORT execution with 100 USD, 100% entry/exit, and Deep Backtest
- **THEN** the run blocks before counting any winner and records the proof in the Project card

### Requirement: Revalidate current Favorites as Pareto benchmarks
The execution MUST revalidate every current BTC/USDT 1d long Favorite on the full available period using the hard invariants and derive `BENCHMARK_RETURN`, `BENCHMARK_DD`, `BENCHMARK_SHARPE`, `BENCHMARK_PF`, and the current non-dominated Pareto set before final ranking when same-direction Favorites exist.

#### Scenario: No same-direction benchmark exists
- **WHEN** T0 has no valid BTC/USDT 1d Long Favorite
- **THEN** `COLD_START_MODE=true`
- **AND** `BENCHMARK_RETURN`, `BENCHMARK_DD`, `BENCHMARK_SHARPE`, and `BENCHMARK_PF` are null
- **AND** `BENCHMARK_PARETO_SET` is empty
- **AND** the execution continues to search for Winner 1.

#### Scenario: Benchmarks are stronger than stored metrics
- **WHEN** deep revalidation materially improves a benchmark relative to stored metrics
- **THEN** previous candidate rankings are discarded and post-benchmark adaptive rounds target the revalidated Pareto set

### Requirement: Save exactly five sequential direction-aware winners
The execution MUST save exactly five new BTC/USDT 1d Long Favorites in sequence, recalibrating benchmarks after each saved winner.

#### Scenario: Winner 1 starts cold chain
- **WHEN** `COLD_START_MODE=true` and no winner has been saved
- **THEN** Winner 1 only needs to pass novelty, direction, hard invariant, robustness, anti-duplicate, anti-fallback, and readback gates
- **AND** Winner 1 becomes the first real chain benchmark after save.

#### Scenario: Later winner improves over prior winners
- **WHEN** Winner N is evaluated and N is greater than 1
- **THEN** the candidate must have return greater than or equal to every prior winner
- **AND** max drawdown less than or equal to every prior winner
- **AND** Sharpe or profit factor greater than or equal to every prior winner
- **AND** at least one configured material improvement over the best prior winner.

#### Scenario: Later winner does not beat the chain
- **WHEN** a candidate does not satisfy sequential improvement against all prior saved winners
- **THEN** it cannot be saved as the next winner even if it is better than T0 benchmarks

#### Scenario: Five valid winners are saved
- **WHEN** WINNER_1 through WINNER_5 are saved, visible, backtest-updated, public-name-safe, direction-correct, and sequentially validated
- **THEN** the card may move to Done técnico after required branch, review, validation, integration, and restart steps

### Requirement: Reject duplicates and dominated candidates
The execution MUST reject candidates that duplicate T0 strategies, duplicate saved winners, or are dominated by any current revalidated same-direction Favorite or prior winner before final ranking or saving.

#### Scenario: Candidate is a renamed existing strategy
- **WHEN** a candidate has new copy or a new `strategy_name` but materially matches T0 or prior-winner logic, parameters, template data, ranges, metrics, or Pine
- **THEN** it is classified as duplicate and cannot be saved or counted as a material executed candidate.

### Requirement: Block only after configured evidence thresholds
The execution MUST report a no-winner blocker only after satisfying the configured minimum active search time, cycles, theses, template families, executed unique deep candidates, post-benchmark adaptive rounds, Pareto-member targeting, and finalist stress requirements unless a real technical blocker prevents continuation.

#### Scenario: Search has not met blocker quotas
- **WHEN** fewer than five valid winners exist but one or more configured blocker quotas remain unmet
- **THEN** the execution continues or reports partial progress instead of claiming no strategy was found.

#### Scenario: Real technical blocker prevents search
- **WHEN** data, PostgreSQL, Deep Backtest, Favorite save/readback, direction persistence, public-name resolution, or supported capital/sizing execution is unavailable
- **THEN** the execution may block before budget quotas
- **AND** the card records the exact evidence, impact, and unblocking decision.
