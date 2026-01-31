# Spec: Combo Optimizer

## MODIFIED Requirements

### Requirement: Grid-Based Optimization for Correlated Parameters

The Combo Optimizer SHALL support joint optimization of correlated parameters using Grid Search.

#### Scenario: CRUZAMENTOMEDIAS Moving Averages

**Given** a user requests optimization for the CRUZAMENTOMEDIAS combo template  
**When** the optimizer detects correlated parameters (`media_curta`, `media_inter`, `media_longa`)  
**Then** it SHALL create a single joint stage that tests all combinations  
**And** the stage SHALL use cartesian product of parameter value lists  
**And** the total number of tests SHALL equal the product of individual list sizes  
**And** Grid Search SHALL execute in Round 1 only (not in refinement rounds)

**Example:**
```
Input: 
  media_curta: [3, 5, 7, 9, 11, 13, 15]  (7 values)
  media_inter: [15, 19, 23, 27, 31, 35]  (6 values)
  media_longa: [25, 30, 35, 40, 45, 50, 55, 60]  (8 values)

Output:
  Round 1: Grid Stage: 7 × 6 × 8 = 336 combinations tested
  Round 2-5: Skip Grid (use best combo from Round 1)
```

#### Scenario: Fallback to Sequential for Uncorrelated Parameters

**Given** a strategy has no correlated parameter groups  
**When** the optimizer generates stages  
**Then** it SHALL use the existing sequential optimization logic  
**And** each parameter SHALL be optimized independently in separate stages  
**And** Iterative Refinement SHALL work normally (all 5 rounds)

### Requirement: Iterative Refinement Compatibility

Grid Search SHALL disable Iterative Refinement to avoid redundant testing.

#### Scenario: Single Round When Grid Search is Active

**Given** a combo template with correlated parameters (Grid Search enabled)  
**When** the optimizer starts  
**Then** it SHALL set `max_rounds = 1` (disable refinement)  
**And** it SHALL execute Grid Search for correlated params  
**And** it SHALL lock the best combination found  
**And** it SHALL optimize independent parameters (e.g., stop_loss) sequentially  
**And** it SHALL complete in a single round

**Rationale:** Grid Search already finds the global maximum by testing all combinations. Iterative refinement would redundantly re-test the same 336 combinations 5 times, wasting ~30 minutes.

**Example:**
```
Round 1 (ONLY round) - Timeframe=1d (user-selected):
  Stage 1: MA Grid [336 tests] → Best: (3, 32, 37)
  Stage 2: Stop Loss [63 tests] → Best: 2.7%
  Total: 399 tests in ~5-10 minutes

Rounds 2-5: SKIPPED (Grid already found global max)
```

#### Scenario: Normal Refinement When Grid is Disabled

**Given** a strategy has no correlated parameter groups  
**When** the optimizer generates stages  
**Then** it SHALL use the existing sequential optimization logic  
**And** each parameter SHALL be optimized independently in separate stages  
**And** Iterative Refinement SHALL work normally (all 5 rounds)

### Requirement: Grid Size Validation

The optimizer SHALL prevent excessively large grids that would cause performance issues.

#### Scenario: Maximum Grid Size Limit

**Given** a user configures parameter ranges  
**When** the optimizer calculates the grid size (product of all value counts)  
**Then** if the grid size exceeds 1000 combinations  
**Then** it SHALL log a warning  
**And** it SHALL suggest reducing the step size or range

**Example:**
```
Input:
  media_curta: range(1, 50, 1)  # 50 values
  media_inter: range(1, 50, 1)  # 50 values
  media_longa: range(1, 50, 1)  # 50 values
  Grid size: 50 × 50 × 50 = 125,000 combinations

Output:
  WARNING: Grid size (125,000) exceeds recommended limit (1,000)
  SUGGESTION: Increase step size (e.g., step=5) or reduce range
  PROCEEDING: Will take ~70 hours at 0.5s/test
```

### Requirement: Stage Configuration Schema

Stage configurations SHALL support both single and joint parameter optimization.

#### Scenario: Joint Parameter Stage Schema

**Given** a joint optimization stage  
**Then** the stage config SHALL have:
- `parameter`: List of parameter names (e.g., `["media_curta", "media_inter", "media_longa"]`)
- `values`: List of value lists, one per parameter (e.g., `[[3,5,7], [15,19,23], [25,30,35]]`)
- `stage_name`: Descriptive name (e.g., "Moving Averages Combo")
- `grid_mode`: Boolean flag set to `True`

**Example:**
```python
{
    "stage_num": 2,
    "stage_name": "Moving Averages Combo",
    "parameter": ["media_curta", "media_inter", "media_longa"],
    "values": [[3, 5, 7], [15, 19, 23], [25, 30, 35]],
    "grid_mode": True  # ← Indicates Grid Search
}
```

#### Scenario: Single Parameter Stage Schema (Unchanged)

**Given** a sequential optimization stage  
**Then** the stage config SHALL have:
- `parameter`: Single parameter name string (e.g., `"stop_loss"`)
- `values`: Flat list of values (e.g., `[0.01, 0.015, 0.02]`)
- `grid_mode`: Boolean flag set to `False` or omitted

### Requirement: Result Storage

Optimization results SHALL store complete parameter combinations for joint stages.

#### Scenario: Joint Stage Result Format

**Given** a test from a joint optimization stage  
**When** the result is stored  
**Then** it SHALL include:
- `params`: Dictionary with ALL tested parameters (not just the joint ones)
- `metrics`: Standard backtest metrics
- `test_num`: Current test index
- `total_tests`: Total tests in this stage

**Example:**
```python
{
    "params": {
        "media_curta": 3,
        "media_inter": 32,
        "media_longa": 37,
        "timeframe": "1d"  # From previous stage
    },
    "metrics": {"sharpe_ratio": 1.84, "total_return_pct": 133453, ...},
    "test_num": 150,
    "total_tests": 336
}
```

### Requirement: Performance Requirements

Grid Search SHALL complete within reasonable time for typical parameter ranges.

#### Scenario: CRUZAMENTOMEDIAS Optimization Time Budget

**Given** a CRUZAMENTOMEDIAS optimization with:
- 7 timeframes
- 336 MA combinations (7×6×8)
- 63 stop_loss values
- Parallel execution (4 workers)
- Deep Backtest enabled

**When** the optimization runs  
**Then** it SHALL complete in under 15 minutes on standard hardware  
**And** the average time per test SHALL be under 2 seconds

**Rationale:** With 4 workers, 336 tests / 4 = 84 batches. At 2s/test, total = ~3 minutes for Grid + ~2 minutes for other stages = ~5 minutes total.

## ADDED Requirements

### Requirement: Deep Backtest Validation

The Combo Optimizer SHALL continue using Deep Backtest by default for all tests.

#### Scenario: Deep Backtest Remains Active

**Given** the Grid Search feature is implemented  
**When** any optimization test runs  
**Then** it SHALL use Deep Backtest (15m validation)  
**And** the `deep_backtest` parameter SHALL default to `True`  
**And** no regression SHALL occur in stop-loss accuracy
