# optimization-engine Specification

## Purpose
TBD - created by syncing delta from change feat-coarse-to-fine. Adaptive coarse-to-fine grid search.

## Requirements

### Requirement: Adaptive Coarse-to-Fine Grid Search
The system MUST implement a 4-stage adaptive grid search. Integer parameters: 4 rounds with decreasing step sizes (5, 3, 2, 1); each round constricts range to neighborhood of previous winner. Decimal parameters: 4 rounds with steps (0.5, 0.3, 0.2, 0.1) and Smart Bounds. Combinatorial integrity: full Cartesian Product within each round, no random/genetic sampling.

### Requirement: Smart Bounds Calculation
The system MUST calculate search range for subsequent rounds as [BestValue - PreviousStep, BestValue + PreviousStep] to ensure coverage of optimal area.

### Requirement: Simplified Input Handling
The implementation MUST derive optimization logic from minimal inputs; backend MAY ignore frontend step and apply automatic adaptive step logic (Target Precision 1 or 0.1).
