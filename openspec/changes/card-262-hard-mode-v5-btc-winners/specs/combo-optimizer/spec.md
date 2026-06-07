## ADDED Requirements

### Requirement: Hard Mode Deep Candidate Evidence
The combo optimization and backtest evidence used for issue #262 SHALL preserve BTC/USDT, timeframe 1d, long direction, Deep Backtest, initial capital 100 USD, 100 percent entry sizing, 100 percent exit sizing, no partial exits, and no pyramiding.

#### Scenario: Candidate optimization preserves invariants
- **WHEN** issue #262 runs `/api/combos/optimize` or an equivalent optimizer path for a candidate
- **THEN** the payload SHALL request Deep Backtest
- **AND** the payload SHALL use BTC/USDT, timeframe 1d, long direction, initial capital 100 USD, 100 percent entry sizing, 100 percent exit sizing, no partial exits, and no pyramiding.

#### Scenario: Final candidate count requires deep final backtest
- **WHEN** issue #262 counts a candidate toward the executed material candidate budget
- **THEN** the candidate SHALL have a final Deep Backtest result with deep execution mode evidence
- **AND** theoretical optimizer combinations, duplicate parameters, revalidations, renamed strategies, and non-deep results SHALL NOT count toward the budget.

#### Scenario: Benchmarks use the same capital model
- **WHEN** issue #262 revalidates current Favorites or references such as multi-ma and buy-and-hold
- **THEN** the benchmark payload SHALL use the same Deep Backtest, capital, sizing, direction, timeframe, and no-partial/no-pyramiding constraints as candidate payloads.
