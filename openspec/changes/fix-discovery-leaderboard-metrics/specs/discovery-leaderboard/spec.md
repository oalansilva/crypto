## ADDED Requirements

### Requirement: Discovery optimizer path SHALL persist ranking metrics without walk-forward split

When Discovery runs `ComboOptimizer.run_optimization` without `split_train_ratio` (legacy full-window path), the system SHALL compute and persist on each successful combination the same ranking metrics defined for the leaderboard: CAGR from optimizer annualized return, Buy & Hold CAGR from identical asset/candles/window, delta as strategy CAGR minus B&H in percentage points, and Calmar from CAGR divided by absolute maximum drawdown. The computation SHALL use the final backtest trades and close series for the effective window. When there are zero closed trades or values are non-finite, the persisted fields SHALL remain `N/A` (null), not numeric zero substitutes.

#### Scenario: Combination with trades gets full ranking metrics

- **WHEN** a discovery combination completes with at least one closed trade and finite drawdown
- **THEN** the persisted `DiscoveryResult` includes finite `cagr`, `calmar_ratio`, `benchmark_cagr`, and `delta_cagr_vs_bh`
- **AND** the leaderboard can rank or display them without rerunning the optimizer

#### Scenario: Zero-trade combination keeps N/A ranking metrics

- **WHEN** a discovery combination completes with zero closed trades
- **THEN** `cagr`, `calmar_ratio`, `benchmark_cagr`, and `delta_cagr_vs_bh` are persisted as null
- **AND** Sharpe/profit factor/win rate are not coerced to fake ranking values beyond their own semantics
