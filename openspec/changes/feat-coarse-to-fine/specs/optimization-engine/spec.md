
# Optimization Engine Specs

## ADDED Requirements

### Requirement: Adaptive Coarse-to-Fine Grid Search

The system MUST implement a 4-stage adaptive grid search to optimize strategy parameters efficiently.

#### Scenario: Integer Parameter Optimization
Given a strategy with an integer parameter (e.g., EMA Length)
When the optimization runs
Then it MUST execute 4 rounds with decreasing step sizes (5, 3, 2, 1)
And each subsequent round MUST constrict the search range to the neighborhod of the previous round's winner.

#### Scenario: Decimal Parameter Optimization
Given a strategy with a decimal parameter (e.g., Stop Loss)
When the optimization runs
Then it MUST execute 4 rounds with decreasing step sizes (0.5, 0.3, 0.2, 0.1)
And the search range MUST be recalculated using Smart Bounds logic.

#### Scenario: Combinatorial Integrity
Given multiple parameters (e.g., 3 MAs + 1 Stop Loss)
When a round executes
Then it MUST test the full Cartesian Product (All-vs-All) of the parameters within that round's range
And it MUST NOT use random or genetic sampling.

### Requirement: Smart Bounds Calculation

The system MUST automatically calculate the search range for subsequent rounds based on the previous round's results to ensure optimal coverage.

#### Scenario: Calculating Next Range
Given a round result with `BestValue` and `PreviousStep`
When preparing the next round
Then the new Range MUST be `[BestValue - PreviousStep, BestValue + PreviousStep]`
And this ensures 100% mathematical coverage of the potential optimal area.

### Requirement: Simplified Input Handling

The implementation MUST abstract complex configuration details from the user, deriving optimization logic solely from minimal inputs.

#### Scenario: Ignoring Frontend Step
Given a user request with a defined `Step`
When the backend processes the optimization
Then it MUST ignore the provided step value
And it MUST apply the automatic adaptive step logic (Target Precision 1 or 0.1).
