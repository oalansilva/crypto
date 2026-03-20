# performance Specification

## Purpose
Define strict performance metrics for backtest results including expectancy, consecutive losses, and average win/loss calculations.

## Requirements

### Requirement: Calculate Expectancy
The system MUST calculate the expectancy of the strategy, defined as `(Win Rate * Avg Win Amount) - (Loss Rate * Avg Loss Amount)`.
#### Scenario: Calculate expectancy
A strategy has 50% win rate, Avg Win $200, Avg Loss $100. Expectancy should be (0.5 * 200) - (0.5 * 100) = 50.

### Requirement: Calculate Max Consecutive Losses
The system MUST iterate through the trade list and find the maximum number of consecutive trades with `pnl < 0`.
#### Scenario: Calculate max consecutive losses
Trade sequence: Win, Loss, Loss, Loss, Win. Max Consecutive Losses = 3.

### Requirement: Calculate Avg Win and Avg Loss
The system MUST separately calculate the average PnL of winning trades (`pnl > 0`) and losing trades (`pnl < 0`).

#### Scenario: Calculate average win and loss
- **GIVEN** a list of trades with pnl values
- **WHEN** the system calculates performance metrics
- **THEN** average PnL is calculated for winning trades (pnl > 0)
- **AND** average PnL is calculated for losing trades (pnl < 0)
