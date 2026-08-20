## ADDED Requirements

### Requirement: Discovery combinations SHALL run Deep Backtest and walk-forward 70/30

When a Discovery worker runs a claimed combination, it SHALL invoke `ComboOptimizer.run_optimization` with `deep_backtest=true` and `split_train_ratio=0.7`. Optimization stages and the final in-sample backtest SHALL use the oldest 70% of the effective candle window. The newest 30% SHALL be the holdout evaluated by the existing walk-forward gate. The worker SHALL NOT omit `split_train_ratio` (legacy full-window path) for Discovery combinations.

#### Scenario: Combination invokes optimizer with Combo defaults

- **WHEN** a Discovery combination starts optimization
- **THEN** the optimizer call includes `deep_backtest=true` and `split_train_ratio=0.7`
- **AND** Deep Backtest 15m remains enabled for `data_source=ccxt`

#### Scenario: Split is not optional per combination

- **WHEN** any successful Discovery combination completes
- **THEN** the worker requested walk-forward 70/30 rather than omitting `split_train_ratio`
- **AND** the persisted metrics snapshot records `split_train_ratio` of `0.7`
- **AND** `split_applied` is true when holdout metrics/verdict exist, false if the optimizer skipped the split

