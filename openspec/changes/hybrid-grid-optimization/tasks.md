# Implementation Tasks

## Phase 1: Core Grid Search Engine ✅ COMPLETED
- [x] Add `itertools` import to `ComboOptimizer`
- [x] Create `_validate_correlation_metadata()` method (GAP 2: Validation)
- [x] Create `_is_correlated_group()` method to detect parameter groups
- [x] Create `_calculate_grid_size()` method to validate grid dimensions
- [x] Create `_generate_range_values()` helper (GAP: Floats + Inclusive Max)
- [x] Add grid size warning (log if > 1000 combinations)
- [x] Modify `generate_stages()` to create joint stages using `_generate_range_values`
- [x] Implement stage ordering: Grids → Sequential (Timeframe is user-selected, not optimized)
- [x] Update stage schema to support `parameter: List[str]`, `values: List[List[Any]]`, and `grid_mode: bool`

## Phase 2: Iterative Refinement Integration ✅ COMPLETED
- [x] Detect if any stage has `grid_mode == True`
- [x] If Grid Search is active, set `max_rounds = 1` (disable refinement)
- [x] If Grid Search is inactive, keep `max_rounds = 5` (normal refinement)
- [x] Add logging: "Grid Search detected - running single round (no refinement)"

## Phase 3: Stage Execution Logic ✅ COMPLETED
- [x] Update `run_optimization()` to detect joint optimization stages (`grid_mode == True`)
- [x] Implement cartesian product iterator using `itertools.product()`
- [x] Modify worker args building to handle joint combinations
- [x] Update parallel execution to distribute grid combinations across workers
- [x] Add cancellation check inside grid loop (`check_cancel_status`) (GAP: Cancellation)
- [x] Ensure result storage saves full param combinations
- [x] Add detailed logging for stage transitions (INFO level)
- [x] Add progress logging for Grid Search (every 10% or 50 tests)
- [x] Add "NEW BEST" indicator when better result found
- [x] Add completion summary with total tests, time, and final config

## Phase 4: Database & Migration ✅ COMPLETED
- [x] Store `correlated_groups` in existing `optimization_schema` JSON field
- [x] Create SQL migration script for CRUZAMENTOMEDIAS template
- [x] Add correlation metadata to other prebuilt templates (RSI, MACD, etc.)
- [x] Implement backward compatibility: fallback to Sequential if no metadata
- [x] Create documentation: `docs/adding_correlation_metadata.md`
- [x] Validate grid size doesn't exceed 1000 combinations

## Phase 5: Validation & Testing ✅ COMPLETED
- [x] Create test case comparing Sequential vs Grid on CRUZAMENTOMEDIAS
- [x] Validate performance improvements (Grid Search reduces total tests vs Sequential with rounds)
- [x] Test cancellation during Grid Search execution
- [x] Verify "Antiga" configuration is discoverable (within grid resolution limits)
- [x] Verify Float parameters (stop_loss) generate correct inclusive ranges
- [x] Verify Grid runs in single round only (max_rounds=1 when Grid active)
- [x] Verify Cancellation stops Grid Search immediately

## Phase 6: Documentation ✅ COMPLETED
- [x] Create walkthrough.md with results
- [x] Update user guide for adding correlation metadata
- [x] Document internal architecture of Hybrid Optimizer
- [x] Update `combo_optimizer.py` docstrings
- [x] Create `docs/adding_correlation_metadata.md` (migration guide)
- [x] Document Grid Search behavior (single round)
- [x] Document grid size limits and recommendations
- [x] Document stage execution order (Grids → Sequential, Timeframe user-selected)
- [x] Document UI considerations (Phase 2 future enhancement) (GAP 5)

- [x] Verify normal strategies still use 5 rounds (max_rounds=5 when no Grid)
- [x] Verify Deep Backtest remains active (no regression)
- [x] Test grid size warning (configure ranges that exceed 1000)
- [x] Benchmark performance (should complete in <10 minutes for ~400 tests with parallelization)
## Phase 6: Documentation
- [ ] Update `combo_optimizer.py` docstrings
- [ ] Create `docs/adding_correlation_metadata.md` (migration guide)
- [ ] Document Grid Search behavior (single round)
- [ ] Document grid size limits and recommendations
- [ ] Document stage execution order (Grids → Sequential, Timeframe user-selected)
- [ ] Document UI considerations (Phase 2 future enhancement) (GAP 5)
