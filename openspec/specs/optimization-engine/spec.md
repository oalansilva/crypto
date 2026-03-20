# optimization-engine Specification

## Purpose
Implement adaptive coarse-to-fine grid search with smart bounds calculation for efficient parameter optimization.

## Requirements

### Requirement: Adaptive Coarse-to-Fine Grid Search
The system MUST implement a 4-stage adaptive grid search. Integer parameters: 4 rounds with decreasing step sizes (5, 3, 2, 1); each round constricts range to neighborhood of previous winner. Decimal parameters: 4 rounds with steps (0.5, 0.3, 0.2, 0.1) and Smart Bounds. Combinatorial integrity: full Cartesian Product within each round, no random/genetic sampling.

#### Scenario: 4-stage adaptive grid for integer parameters
- **GIVEN** integer parameters require optimization
- **WHEN** the adaptive grid search executes
- **THEN** 4 rounds run with decreasing step sizes (5, 3, 2, 1)
- **AND** each round constricts range to neighborhood of previous winner
- **AND** full Cartesian Product is maintained within each round

### Requirement: Smart Bounds Calculation
The system MUST calculate search range for subsequent rounds as [BestValue - PreviousStep, BestValue + PreviousStep] to ensure coverage of optimal area.

#### Scenario: Smart bounds for subsequent rounds
- **GIVEN** Round N finds BestValue with PreviousStep
- **WHEN** Round N+1 begins
- **THEN** search range is calculated as [BestValue - PreviousStep, BestValue + PreviousStep]
- **AND** optimal area coverage is maintained

### Requirement: Simplified Input Handling
The implementation MUST derive optimization logic from minimal inputs; backend MAY ignore frontend step and apply automatic adaptive step logic (Target Precision 1 or 0.1).

#### Scenario: Automatic adaptive step logic
- **GIVEN** minimal inputs are provided to the optimization engine
- **WHEN** optimization runs
- **THEN** backend derives optimization logic automatically
- **AND** applies adaptive step logic with Target Precision 1 or 0.1
