## MODIFIED Requirements

### Requirement: Capture complete T0 before search
The execution MUST capture a timestamped T0 snapshot for BTC/USDT 1d in the configured direction before any optimization, exploratory backtest, template mutation, Favorite save, Pine generation, or durable report generation.

#### Scenario: T0 exists before technical search
- **WHEN** the run begins after Project 1 card creation and OpenSpec setup
- **THEN** the snapshot includes current Favorites, direction counts, compatible templates, public mappings, related Pine scripts, and current Favorite deep revalidation payload/results before candidate search starts
- **AND** the snapshot explicitly states whether valid Favorites exist for the configured direction

### Requirement: Enforce hard BTC deep backtest invariants
Every benchmark, candidate, finalist, saved Favorite, and Pine artifact MUST preserve BTC/USDT, 1d, configured direction, `deep_backtest=true`, initial capital 100 USD, 100% entry, 100% exit, no partial exits, no pyramiding, no leverage, and no residual position.

#### Scenario: Candidate violates direction or sizing
- **WHEN** a payload, result, template, Favorite, or Pine artifact violates direction, sizing, execution mode, or position-management invariants
- **THEN** the candidate is invalid and does not count toward benchmarks, quotas, finalists, or final delivery

#### Scenario: SHORT engine support is missing
- **WHEN** the configured direction is SHORT and the engine cannot prove true SHORT execution with 100 USD, 100% entry/exit, and Deep Backtest
- **THEN** the run blocks before counting any winner and records the proof in the Project 1 card

## MODIFIED Requirements

### Requirement: Revalidate current Favorites as Pareto benchmarks
The execution MUST revalidate every current BTC/USDT 1d Favorite in the configured direction on the full available period using the hard invariants and derive `BENCHMARK_RETURN`, `BENCHMARK_DD`, `BENCHMARK_SHARPE`, `BENCHMARK_PF`, and the current non-dominated Pareto set when such Favorites exist.

#### Scenario: No same-direction Favorites exist
- **WHEN** no valid current Favorites exist for BTC/USDT 1d in the configured direction at T0
- **THEN** `COLD_START_MODE=true`
- **AND** all benchmark fields may be null or empty
- **AND** the run proceeds to search WINNER_1 instead of blocking

#### Scenario: Benchmarks are stronger than stored metrics
- **WHEN** deep revalidation materially improves a benchmark relative to stored metrics
- **THEN** previous candidate rankings are discarded and post-benchmark adaptive rounds target the revalidated Pareto set

## MODIFIED Requirements

### Requirement: Reject duplicates and dominated candidates
The execution MUST reject candidates that duplicate T0 strategies, duplicate earlier winners, use the opposite direction, or are dominated by any current revalidated same-direction Favorite or prior winner before final ranking or saving.

#### Scenario: Candidate is a renamed existing strategy
- **WHEN** a candidate has new copy or a new `strategy_name` but materially matches T0 logic, parameters, template data, ranges, metrics, or Pine
- **THEN** it is classified as duplicate and cannot be saved or counted as a material executed candidate

## ADDED Requirements

### Requirement: Save exactly five sequential direction-aware winners
The execution MUST save exactly five new Favorites in the configured direction or block with the configured evidence. WINNER_1 MAY initialize the chain in cold-start mode; each later winner MUST satisfy the sequential improvement contract against every prior winner.

#### Scenario: Later winner does not beat the chain
- **WHEN** a candidate does not satisfy sequential improvement against all prior saved winners
- **THEN** it cannot be saved as the next winner even if it is better than T0 benchmarks

#### Scenario: Five valid winners are saved
- **WHEN** WINNER_1 through WINNER_5 are saved, visible, backtest-updated, public-name-safe, direction-correct, and sequentially validated
- **THEN** the card may move to Done técnico after required branch, review, validation, integration, and restart steps

### Requirement: Block fallback public names before save
The execution MUST validate an explicit public-name contract before saving each new Favorite, including `name`, `strategy_name`, `strategy_display_name`, `strategy_description`, `direction`, and the resolver or payload source used by the API/tela.

#### Scenario: Public resolver would fall back
- **WHEN** the public resolver or save payload would produce empty, generic, or `Estratégia Cripto Farol` copy
- **THEN** the Favorite MUST NOT be saved
- **AND** the product path MUST be fixed through the governed workflow or the run must block with evidence

## MODIFIED Requirements

### Requirement: Block only after configured evidence thresholds
The execution MUST report a no-winner blocker only after satisfying the configured minimum active search time, cycles, theses, template families, executed unique deep candidates, post-benchmark adaptive rounds, Pareto-member targeting, and finalist stress requirements unless a real technical blocker prevents continuation.

#### Scenario: Search has not met blocker quotas
- **WHEN** no full five-winner chain exists but one or more configured blocker quotas remain unmet
- **THEN** the execution continues or reports partial progress instead of claiming no strategy was found
