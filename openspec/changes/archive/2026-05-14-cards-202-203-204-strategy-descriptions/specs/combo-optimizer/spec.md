## MODIFIED Requirements

### Requirement: Optimization Final Result Execution Mode

The optimization endpoint SHALL return final trades and metrics generated with the same execution mode used for optimization scoring.

#### Scenario: Deep Backtest requested

- **WHEN** `/api/combos/optimize` runs with `deep_backtest=true`
- **THEN** stage scoring SHALL use Deep Backtest when 15m data coverage is available
- **AND** the final returned trades and metrics SHALL also use the Deep Backtest extraction path.
