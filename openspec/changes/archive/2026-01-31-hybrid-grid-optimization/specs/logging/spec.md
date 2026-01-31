# Spec: Logging & Observability

## ADDED Requirements

### Requirement: Detailed Progress Logging

The Combo Optimizer SHALL provide detailed, real-time logging of optimization progress.

#### Scenario: Stage Transition Logging

**Given** an optimization job is running  
**When** the optimizer transitions between stages  
**Then** it SHALL log:
- Stage number and name
- Optimization mode (Sequential vs Grid Search)
- Total number of tests in this stage
- Locked parameters from previous stages

**Example:**
```log
INFO: ========================================
INFO: STAGE 2/3: Moving Averages Grid Search
INFO: Mode: Grid Search (Parallel)
INFO: Parameters: ['media_curta', 'media_inter', 'media_longa']
INFO: Grid Size: 7 × 6 × 8 = 336 combinations
INFO: Workers: 4 (parallel execution)
INFO: Estimated Time: ~3 minutes
INFO: ========================================
```

#### Scenario: Individual Test Logging

**Given** a Grid Search stage is executing  
**When** each combination is tested  
**Then** it SHALL log:
- Test number and total (e.g., `[Grid 150/336]`)
- Parameter combination (e.g., `(3, 32, 37)`)
- Key metrics (Sharpe, Return, Trades)
- "NEW BEST" indicator when a better result is found

**Example:**
```log
INFO: [Grid 150/336] (3, 32, 37) → Sharpe: 2.84, Return: +133,453%, Trades: 75 ✓ NEW BEST!
```

#### Scenario: Completion Summary

**Given** an optimization job completes  
**When** all stages finish  
**Then** it SHALL log:
- Total tests executed
- Total time elapsed
- Optimization mode used
- Final best configuration with all parameters
- Final metrics (Sharpe, Return, Trades, Win Rate, Drawdown)

**Example:**
```log
INFO: ========================================
INFO: OPTIMIZATION COMPLETE
INFO: Total Tests: 406 (7 + 336 + 63)
INFO: Total Time: 8m 42s
INFO: Mode: Hybrid Grid Search (Single Round)
INFO: ========================================
INFO: FINAL BEST CONFIGURATION:
INFO:   timeframe: 4h
INFO:   media_curta: 3
INFO:   media_inter: 32
INFO:   media_longa: 37
INFO:   stop_loss: 2.7%
INFO: METRICS:
INFO:   Sharpe Ratio: 2.84
INFO:   Total Return: +133,453%
INFO:   Total Trades: 75
INFO: ========================================
```

### Requirement: Progress Indicators

The optimizer SHALL provide real-time progress indicators during long-running Grid Search stages.

#### Scenario: Progress Percentage and ETA

**Given** a Grid Search stage with >100 combinations  
**When** tests are executing  
**Then** every 10% progress it SHALL log:
- Percentage complete
- Estimated time remaining
- Average time per test

**Example:**
```log
INFO: [Grid 34/336] (10.1%) - ETA: 2m 45s - Avg: 0.52s/test
INFO: [Grid 67/336] (19.9%) - ETA: 2m 18s - Avg: 0.51s/test
INFO: [Grid 101/336] (30.1%) - ETA: 1m 58s - Avg: 0.50s/test
```

### Requirement: Debug Mode Support

The optimizer SHALL support verbose debug logging for troubleshooting.

#### Scenario: Worker-Level Debugging

**Given** debug logging is enabled  
**When** a worker executes a test  
**Then** it SHALL log:
- Worker ID
- Parameter combination being tested
- Data loading details (candles, timeframe)
- Indicator calculation steps
- Individual trade details
- Execution time

**Example:**
```log
DEBUG: Worker 1 starting test: (3, 15, 25)
DEBUG: Loading 15m data for Deep Backtest: 294,911 candles
DEBUG: Calculating indicators: SMA(3), SMA(15), SMA(25)
DEBUG: Generating signals: 1,247 candles processed
DEBUG: Simulating execution with stop_loss=1.5%
DEBUG: Trade 1: Entry=50,234.5 @ 2023-01-15 14:00, Exit=51,123.8 @ 2023-01-18 09:30
DEBUG: Worker 1 completed: Sharpe=0.92, Time=2.3s
```

### Requirement: Warning and Error Logging

The optimizer SHALL log clear warnings and errors for validation failures and performance issues.

#### Scenario: Grid Size Warning

**Given** a Grid Search stage has >1000 combinations  
**When** the stage is generated  
**Then** it SHALL log a WARNING with:
- Actual grid size
- Recommended limit
- Estimated time
- Suggestion to reduce grid size

**Example:**
```log
WARNING: Grid size (125,000) exceeds recommended limit (1,000)
WARNING: Estimated time: ~70 hours at 0.5s/test
WARNING: Consider increasing step size or reducing range
WARNING: Proceeding with optimization...
```

#### Scenario: Validation Error

**Given** correlation metadata contains invalid parameter names  
**When** validation runs  
**Then** it SHALL log an ERROR with:
- Invalid parameter name
- List of available parameters
- Clear error message

**Example:**
```log
ERROR: Invalid correlated_groups: parameter 'media_longa_TYPO' not found
ERROR: Available parameters: ['media_curta', 'media_inter', 'media_longa', 'stop_loss']
ERROR: Validation failed - aborting optimization
```
