# Proposal: Iterative Optimization Refinement

## Why
Currently, the optimization process is "greedy" and sequential. It optimizes Parameter A, then B, then C. However, the optimal value for A might depend on C. Once C is found, the value selected for A might no longer be optimal.

The user wants the system to be "smarter" and revisit parameters in rounds until it finds the absolute best combination where no single parameter change yields improvement (Local Optimum).

## What Changes
We will implement an **Iterative Refinement Loop (Coordinate Descent)**:
1.  **Rounds**: The optimization process will run in "Rounds".
2.  **Convergence Check**: After optimizing all parameters (one full pass), the system checks if any best parameter value changed compared to the start of the round.
3.  **Loop**:
    *   If **changed**: Start a new round using the new best parameters as the baseline.
    *   If **stable** (no changes): Stop. The combination is converged.
4.  **Max Rounds**: A safety limit (e.g., 5 rounds) to prevent infinite loops.

## Impact
- **Backend**: Update `ComboOptimizer.run_optimization` to wrap the stage loop in a `while` loop.
- **Logging**: Enhance logs to clearly show "Round 1", "Round 2", and "Convergence achieved".
