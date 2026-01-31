# logging Specification

## Purpose
TBD - created by syncing delta from change hybrid-grid-optimization. Detailed progress logging for Combo Optimizer.

## Requirements

### Requirement: Detailed Progress Logging
The Combo Optimizer SHALL provide detailed, real-time logging of optimization progress.

#### Scenario: Stage Transition Logging
When the optimizer transitions between stages, it SHALL log: stage number and name, optimization mode (Sequential vs Grid Search), total number of tests, locked parameters from previous stages.

#### Scenario: Individual Test Logging
When each combination is tested in a Grid Search stage, it SHALL log test number/total, parameter combination, key metrics (Sharpe, Return, Trades), and "NEW BEST" when a better result is found.

#### Scenario: Completion Summary
When an optimization job completes, it SHALL log final best parameters, total tests, total time, and key metrics.
