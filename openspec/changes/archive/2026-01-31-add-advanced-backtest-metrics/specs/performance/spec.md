# Spec: Strict Performance Metrics

## ADDED Requirements

### Requirement: Calculate Expectancy
The system MUST calculate the expectancy of the strategy, defined as `(Win Rate * Avg Win Amount) - (Loss Rate * Avg Loss Amount)`.
#### Scenario:
A strategy has 50% win rate, Avg Win $200, Avg Loss $100. Expectancy should be (0.5 * 200) - (0.5 * 100) = 50.

### Requirement: Calculate Max Consecutive Losses
The system MUST iterate through the trade list and find the maximum number of consecutive trades with `pnl < 0`.
#### Scenario:
Trade sequence: Win, Loss, Loss, Loss, Win. Max Consecutive Losses = 3.

### Requirement: Calculate Avg Win and Avg Loss
The system MUST separately calculate the average PnL of winning trades (`pnl > 0`) and losing trades (`pnl < 0`).
#### Scenario:
Winning trades: 100, 200. Avg Win = 150. Losing trades: -50, -50. Avg Loss = 50 (absolute value usually, or negative).
