# Implementation Tasks

## Phase 1: Core Grid Search Engine
- [ ] Add `itertools` import to `ComboOptimizer`
- [ ] Create `_validate_correlation_metadata()` method (GAP 2: Validation)
- [ ] Create `_is_correlated_group()` method to detect parameter groups
- [ ] Create `_calculate_grid_size()` method to validate grid dimensions
- [ ] Create `_generate_range_values()` helper (GAP: Floats + Inclusive Max)
- [ ] Add grid size warning (log if > 1000 combinations)
- [ ] Modify `generate_stages()` to create joint stages using `_generate_range_values`
- [ ] Implement stage ordering: Grids → Sequential (Timeframe is user-selected, not optimized)
- [ ] Update stage schema to support `parameter: List[str]`, `values: List[List[Any]]`, and `grid_mode: bool`

## Phase 2: Iterative Refinement Integration
- [ ] Detect if any stage has `grid_mode == True`
- [ ] If Grid Search is active, set `max_rounds = 1` (disable refinement)
- [ ] If Grid Search is inactive, keep `max_rounds = 5` (normal refinement)
- [ ] Add logging: "Grid Search detected - running single round (no refinement)"

## Phase 3: Stage Execution Logic
- [ ] Update `run_optimization()` to detect joint optimization stages (`grid_mode == True`)
- [ ] Implement cartesian product iterator using `itertools.product()`
- [ ] Modify worker args building to handle joint combinations
- [ ] Update parallel execution to distribute grid combinations across workers
- [ ] Add cancellation check inside grid loop (`check_cancel_status`) (GAP: Cancellation)
- [ ] Ensure result storage saves full param combinations
- [ ] Add detailed logging for stage transitions (INFO level)
- [ ] Add progress logging for Grid Search (every 10% or 50 tests)
- [ ] Add "NEW BEST" indicator when better result found
- [ ] Add completion summary with total tests, time, and final config

## Phase 4: Database & Migration (GAP 1 & 4)
- [ ] Store `correlated_groups` in existing `optimization_schema` JSON field
- [ ] Create SQL migration script for CRUZAMENTOMEDIAS template
- [ ] Add correlation metadata to other prebuilt templates (RSI, MACD, etc.)
- [ ] Implement backward compatibility: fallback to Sequential if no metadata
- [ ] Create documentation: `docs/adding_correlation_metadata.md`
- [ ] Validate grid size doesn't exceed 1000 combinations

## Phase 5: Validation & Testing
- [ ] Create test case comparing Sequential vs Grid on CRUZAMENTOMEDIAS
- [ ] Verify Float parameters (stop_loss) generate correct inclusive ranges
- [ ] Verify "Antiga" configuration is discovered automatically
- [ ] Verify Grid runs in single round only (max_rounds=1 when Grid active)
- [ ] Verify Cancellation stops Grid Search immediately
- [ ] Verify normal strategies still use 5 rounds (max_rounds=5 when no Grid)
- [ ] Verify Deep Backtest remains active (no regression)
- [ ] Test grid size warning (configure ranges that exceed 1000)
- [ ] Benchmark performance (should complete in <10 minutes for ~400 tests with parallelization)
- [ ] Add logging to show: "Grid Search detected - running single round (no refinement)"

## Phase 6: Documentation
- [ ] Update `combo_optimizer.py` docstrings
- [ ] Create `docs/adding_correlation_metadata.md` (migration guide)
- [ ] Document Grid Search behavior (single round)
- [ ] Document grid size limits and recommendations
- [ ] Document stage execution order (Grids → Sequential, Timeframe user-selected)
- [ ] Document UI considerations (Phase 2 future enhancement) (GAP 5)
