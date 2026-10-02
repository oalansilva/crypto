## ADDED Requirements

### Requirement: Next favorite refresh uses the slippage table

When a favorite is next refreshed by the existing automatic routine, the recalculation SHALL apply `backtest-slippage-by-timeframe` for that favorite's timeframe. This change SHALL NOT enqueue an immediate full recálculo of all favorites.

#### Scenario: Due 4h favorite refresh uses 0,02% slippage

- **WHEN** a due 4h favorite is refreshed by the normal worker
- **THEN** the backtest applies 0,02% slippage per side and 0,075% fee
- **AND** this card does not start a one-shot refresh of every favorite

#### Scenario: Due 1h favorite refresh uses 0,03% slippage

- **WHEN** a due 1h favorite is refreshed by the normal worker
- **THEN** the backtest applies 0,03% slippage per side
