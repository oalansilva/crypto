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
