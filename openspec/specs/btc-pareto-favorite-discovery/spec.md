# btc-pareto-favorite-discovery Specification

## Purpose
Govern BTC/USDT 1d long strategy discovery runs that must prove novelty, Deep Backtest execution, Pareto comparison, and Favorite visibility before success.

## Requirements

### Requirement: Capture complete T0 before search
The execution MUST capture a timestamped T0 snapshot for BTC/USDT 1d long before any optimization, exploratory backtest, template mutation, Favorite save, Pine generation, or durable report generation.

#### Scenario: T0 exists before technical search
- **WHEN** the run begins after card creation
- **THEN** the snapshot includes current Favorites, templates, public mappings, related Pine scripts, and current Favorite deep revalidation payload/results before candidate search starts

### Requirement: Enforce hard BTC deep backtest invariants
Every benchmark, candidate, finalist, saved Favorite, and Pine artifact MUST preserve BTC/USDT, 1d, long, `deep_backtest=true`, initial capital 100 USD, 100% entry, 100% exit, no partial exits, no pyramiding, no leverage, and no residual position.

#### Scenario: Candidate violates sizing or execution mode
- **WHEN** a payload, result, template, Favorite, or Pine artifact violates any invariant
- **THEN** the candidate is invalid and does not count toward benchmarks, quotas, finalists, or final delivery

### Requirement: Revalidate current Favorites as Pareto benchmarks
The execution MUST revalidate every current BTC/USDT 1d long Favorite on the full available period using the hard invariants and derive `BENCHMARK_RETURN`, `BENCHMARK_DD`, `BENCHMARK_SHARPE`, `BENCHMARK_PF`, and the current non-dominated Pareto set before final ranking.

#### Scenario: Benchmarks are stronger than stored metrics
- **WHEN** deep revalidation materially improves a benchmark relative to stored metrics
- **THEN** previous candidate rankings are discarded and post-benchmark adaptive rounds target the revalidated Pareto set

### Requirement: Reject duplicates and dominated candidates
The execution MUST reject candidates that duplicate T0 strategies or are dominated by any current revalidated Favorite before final ranking or saving.

#### Scenario: Candidate is a renamed existing strategy
- **WHEN** a candidate has new copy or a new `strategy_name` but materially matches T0 logic, parameters, template data, ranges, metrics, or Pine
- **THEN** it is classified as duplicate and cannot be saved or counted as a material executed candidate

### Requirement: Save only a defensible Pareto winner
The execution MUST save a new Favorite only if it satisfies one configured strong superation path: clear dominance, defensible new Pareto profile, or exceptional defensive profile.

#### Scenario: Candidate is worse on return and drawdown
- **WHEN** a candidate has lower return and worse drawdown than a relevant current Favorite
- **THEN** the candidate cannot be saved even if Sharpe or profit factor is marginally better

### Requirement: Block only after configured evidence thresholds
The execution MUST report a no-winner blocker only after satisfying the configured minimum active search time, cycles, theses, template families, executed unique deep candidates, post-benchmark adaptive rounds, Pareto-member targeting, and finalist stress requirements unless a real technical blocker prevents continuation.

#### Scenario: Search has not met blocker quotas
- **WHEN** no winner exists but one or more configured blocker quotas remain unmet
- **THEN** the execution continues or reports partial progress instead of claiming no strategy was found
