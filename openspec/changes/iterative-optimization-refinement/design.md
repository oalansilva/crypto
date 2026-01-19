# Design: Iterative Optimization Refinement

## Architecture
The `ComboOptimizer` class will be modified to support a multi-round approach.

### `ComboOptimizer.run_optimization`
Currently, this method roughly looks like:

```python
stages = generate_stages()
for stage in stages:
    optimize(stage)
```

**New Logic:**

```python
stages = generate_stages()
converged = False
round_num = 1
max_rounds = 5

while not converged and round_num <= max_rounds:
    logging.info(f"--- STARTING ROUND {round_num} ---")
    
    # Snapshot parameters at start of round
    params_at_start = best_params.copy()
    
    for stage in stages:
        # Optimization logic (Parallel execution) ...
        # Updates best_params in place
    
    # Check for convergence
    if best_params == params_at_start:
        converged = True
        logging.info("CONVERGENCE ACHIEVED: Parameters stabilized.")
    else:
        logging.info("Parameters changed. Creating new round for refinement.")
        round_num += 1
```

## Logging
- Logs must strictly separate rounds visually.
- "Round X of Y" context.

## UX Implications
- Optimization jobs will take longer (N times longer in worst case).
- User feedback (logs) becomes critical to show *why* it's taking longer ("Refining parameters...").
