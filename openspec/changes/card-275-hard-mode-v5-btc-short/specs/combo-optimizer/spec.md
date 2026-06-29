## MODIFIED Requirements

### Requirement: Short-only deep candidate evaluation

Card #275 candidate evaluation MUST count only BTC/USDT 1D final deep backtests with `direction=short`, initial capital 100 USD, 100% entry size, 100% exit size, no partial exits, and no pyramiding.

#### Scenario: candidate counts toward the search budget

- **GIVEN** a candidate final backtest uses BTC/USDT 1D, `direction=short`, `deep_backtest=true`, `initial_capital=100`, 100% entry and 100% exit
- **WHEN** the backtest execution mode is `deep_15m` or an equivalent proven deep mode
- **THEN** it may count as an executed material candidate if it is not a duplicate or revalidation

#### Scenario: incompatible direction does not count

- **GIVEN** a candidate or reference is Long-only or direction-incompatible
- **WHEN** benchmarks, references, or winner decisions are built
- **THEN** it MUST NOT be used as a mandatory benchmark or counted as a winner
