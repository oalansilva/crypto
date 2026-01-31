# Proposal: Parallelize Optimization Tests

## Why
The `SequentialOptimizer` (and by extension `ComboOptimizer`) runs tests sequentially. Even though strategies are optimized one parameter at a time (stage-by-stage), the tests *within* a stage (e.g., testing `sma_long` values 20, 21, ..., 100) are independent and can be parallelized. Running them sequentially on a single core is inefficient and slow for large ranges.

## What Changes
Implement parallel execution for the inner optimization loop (testing multiple values for the *current* parameter) using `concurrent.futures.ProcessPoolExecutor`.

The process will remain sequential *between* stages (Stage 1 finishes -> best result picked -> Stage 2 starts), but *within* Stage 1, all candidate values will be tested in parallel.

### Key Changes
1.  **Refactor `Optimizer` Services**:
    - Extract backtest logic into a picklable, top-level static/worker function that does *not* rely on database connections (to avoid pickling issues).
    - Use `ProcessPoolExecutor` in `run_optimization` to map the worker function over the list of parameter values to test.
    - Adjust `ComboService` or `BacktestService` usage to ensure worker processes can instantiate strategies without external dependencies.

2.  **Performance Tuning**:
    - Use `max_workers = cpu_count - 1` to utilize available cores while leaving one for the orchestration process.
    - Fetch necessary metadata (template info, historical data) *once* in the main process and pass it to workers to minimize I/O overhead.

### Benefits
- **Significant Speedup**: Backtesting is CPU-bound. Parallel execution should scale almost linearly with core count for this workload.
- **Better User Experience**: Faster results for optimization tasks, especially with fine-grained steps (like step=1).
