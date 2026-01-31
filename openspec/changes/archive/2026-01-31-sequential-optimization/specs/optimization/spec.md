# Spec: Sequential Optimization Logic

## ADDED Requirements

### Requirement: Stage-Based Parameter Locking

The system MUST execute optimization in sequential stages where:
1. Each stage optimizes exactly ONE parameter or parameter group
2. All previous stage results are LOCKED (fixed) for subsequent stages
3. The best result from each stage becomes the baseline for the next stage

#### Scenario: MACD Sequential Optimization

**Given** a user selects BTC/USDT with MACD strategy  
**When** they start sequential optimization  
**Then** the system executes 5 stages:
1. Stage 1: Tests timeframes [5m, 15m, 30m, 1h, 2h, 4h, 1d] (excludes 3d, 1w) → selects best (e.g., 1h)
2. Stage 2: Tests fast_period [6-18] with timeframe=1h locked → selects best (e.g., 12)
3. Stage 3: Tests slow_period [20-32] with timeframe=1h, fast=12 locked → selects best (e.g., 26)
4. Stage 4: Tests signal_period [6-12] with timeframe=1h, fast=12, slow=26 locked → selects best (e.g., 9)
5. Stage 5: Tests stop_loss [0.5%-5%] with all params locked → selects best (e.g., 1.5%)
6. Stage 6: Tests stop_gain [None, 1%, 2%, 3%, 4%, 5%, 7.5%, 10%] with all params locked → selects best (e.g., 3% or None)

**And** the final configuration is: timeframe=1h, fast=12, slow=26, signal=9, stop_loss=1.5%, stop_gain=3% (or None)  
**And** all tests used the complete available historical data for BTC/USDT

### Requirement: Full History Backtesting

The system MUST use the complete available historical data for ALL tests in ALL stages:
1. No date range selection or filtering
2. Automatically detect the earliest and latest available data points
3. Use the entire dataset for every backtest
4. This ensures robust optimization across all market conditions

#### Scenario: Full History Data Usage

**Given** BTC/USDT has historical data from 2017-01-01 to 2025-12-30  
**When** any test is executed in any stage  
**Then** the backtest runs from 2017-01-01 to 2025-12-30  
**And** no date range parameters are exposed to the user  
**And** the UI displays: "Testing on full history: 2017-01-01 to 2025-12-30 (8 years)"

#### Scenario: Different Symbols Have Different History

**Given** ETH/USDT has data from 2018-06-01 to 2025-12-30  
**And** BTC/USDT has data from 2017-01-01 to 2025-12-30  
**When** user optimizes ETH/USDT strategy  
**Then** all tests use 2018-06-01 to 2025-12-30  
**When** user optimizes BTC/USDT strategy  
**Then** all tests use 2017-01-01 to 2025-12-30  
**And** each symbol uses its own maximum available history

### Requirement: Dynamic Stage Generation

The system MUST automatically generate optimization stages based on the selected indicator's parameter schema:
1. Introspect the indicator to retrieve its parameter list
2. Create Stage 1 for timeframe optimization
3. Create one stage for each indicator parameter (in order)
4. Create Stage N+2 for stop-loss optimization
5. Create Stage N+3 for stop-gain optimization (optional, includes "None" as an option)
6. Total stages = 3 + number_of_indicator_parameters

#### Scenario: RSI Generates 4 Stages

**Given** user selects RSI strategy  
**When** the system initializes sequential optimization  
**Then** it generates exactly 5 stages:
1. Stage 1: Timeframe (7 tests)
2. Stage 2: RSI Period (11 tests: 10-20)
3. Stage 3: Overbought/Oversold Levels (16 tests each)
4. Stage 4: Stop-Loss (10 tests)
5. Stage 5: Stop-Gain (8 tests: None, 1%, 2%, 3%, 4%, 5%, 7.5%, 10%)

**And** the total estimated tests = 7 + 11 + 16 + 16 + 10 + 8 = 68

#### Scenario: Bollinger Bands Generates 4 Stages

**Given** user selects Bollinger Bands strategy  
**When** the system initializes sequential optimization  
**Then** it generates exactly 5 stages:
1. Stage 1: Timeframe (7 tests)
2. Stage 2: Period (11 tests: 15-25)
3. Stage 3: Standard Deviation (16 tests: 1.5-3.0, step 0.1)
4. Stage 4: Stop-Loss (10 tests)
5. Stage 5: Stop-Gain (8 tests: None, 1%, 2%, 3%, 4%, 5%, 7.5%, 10%)

**And** the total estimated tests = 7 + 11 + 16 + 10 + 8 = 52

### Requirement: Indicator Parameter Schema

Each indicator MUST define a parameter schema containing:
- Parameter name
- Default value
- Optimization range (min, max, step)
- Description

#### Scenario: Validate MACD Schema

**Given** the MACD indicator is registered  
**When** the system loads the indicator schema  
**Then** it contains:
- `fast_period`: default=12, range=[6-18], step=1
- `slow_period`: default=26, range=[20-32], step=1
- `signal_period`: default=9, range=[6-12], step=1

**And** all parameters have valid optimization ranges (min < max, step > 0)

### Requirement: Schema-Driven Configuration (Zero Hardcoding)

The system MUST derive ALL configuration from indicator and risk management schemas:
1. NO hardcoded parameter names (read from indicator schema)
2. NO hardcoded default values (read from indicator schema)
3. NO hardcoded optimization ranges (read from indicator schema)
4. NO hardcoded stop-loss values (read from risk management schema)
5. NO hardcoded stop-gain options (read from risk management schema)
6. The system must work with ANY indicator by introspecting its schema

#### Scenario: New Indicator Without Code Changes

**Given** a developer creates a new indicator "Stochastic RSI"  
**And** defines its schema with 3 parameters:
```python
STOCH_RSI_PARAMS = {
    "rsi_period": {"default": 14, "optimization_range": {"min": 10, "max": 20, "step": 1}},
    "stoch_period": {"default": 14, "optimization_range": {"min": 10, "max": 20, "step": 1}},
    "smooth_k": {"default": 3, "optimization_range": {"min": 1, "max": 5, "step": 1}}
}
```

**When** the user selects "Stochastic RSI" for optimization  
**Then** the system automatically generates 6 stages:
1. Timeframe
2. RSI Period (10-20)
3. Stoch Period (10-20)
4. Smooth K (1-5)
5. Stop-Loss (from risk schema)
6. Stop-Gain (from risk schema)

**And** NO code changes were required to support this new indicator

### Requirement: Stop-Gain (Take Profit) Testing

The system MUST include a final stage to test stop-gain (take profit) values, where:
1. "None" (no stop-gain) is always included as an option
2. Multiple percentage values are tested (e.g., 1%, 2%, 3%, 4%, 5%, 7.5%, 10%)
3. The best performing option is selected (which may be "None")
4. This allows the system to determine if using a take-profit target improves results

#### Scenario: Stop-Gain Improves Performance

**Given** all previous stages completed with best params  
**When** Stage N+3 (Stop-Gain) executes  
**Then** the system tests: [None, 1%, 2%, 3%, 4%, 5%, 7.5%, 10%]  
**And** if stop_gain=3% produces higher PnL than None  
**Then** the final configuration includes stop_gain=3%

#### Scenario: No Stop-Gain Performs Better

**Given** all previous stages completed with best params  
**When** Stage N+3 (Stop-Gain) executes  
**Then** the system tests: [None, 1%, 2%, 3%, 4%, 5%, 7.5%, 10%]  
**And** if None produces higher PnL than all stop-gain values  
**Then** the final configuration includes stop_gain=None (no take-profit)

### Requirement: Stage Result Persistence

The system MUST persist each stage's results including:
- Stage number and name
- Parameter being optimized
- All tested values and their performance metrics
- Best value selected
- Timestamp of stage completion

#### Scenario: Retrieve Stage 2 Results

**Given** a sequential optimization job has completed Stage 2  
**When** the user requests Stage 2 results via API  
**Then** the system returns:
- Stage number: 2
- Parameter name: "fast_period"
- Tested values: [6, 7, 8, ..., 18]
- Performance for each value (PnL, win rate, trades)
- Best value: 12
- Locked parameters from previous stages: {timeframe: "1h"}
- Timestamp: "2025-12-30T10:15:00Z"

### Requirement: Stage Re-execution

Users MUST be able to:
- Re-run any completed stage with different parameter ranges
- Skip a stage (use default value and proceed)
- Restart the entire sequence from Stage 1

#### Scenario: Re-run Stage with Wider Range

**Given** Stage 2 completed with fast_period range [6-18], best=12  
**When** user re-runs Stage 2 with range [10-20]  
**Then** the system:
- Keeps Stage 1 result locked (timeframe=1h)
- Tests fast_period values [10, 11, ..., 20]
- Selects new best value
- Invalidates Stages 3-5 (they must be re-run with new Stage 2 result)

#### Scenario: Skip Stage

**Given** user is on Stage 3 (slow_period optimization)  
**When** user clicks "Skip Stage" and enters default value 26  
**Then** the system:
- Sets slow_period=26 without testing
- Proceeds to Stage 4
- Marks Stage 3 as "skipped" in results

### Requirement: Performance Comparison

The system MUST display:
- Estimated total tests for sequential mode vs grid search mode
- Time savings estimate
- Performance improvement across stages (chart)

#### Scenario: Display Test Count Comparison

**Given** user configures MACD optimization with:
- 7 timeframes
- 13 fast_period values
- 13 slow_period values
- 7 signal_period values
- 10 stop_loss values

**When** the UI calculates test estimates  
**Then** it displays:
- Grid Search: 7 × 13 × 13 × 7 × 10 = **82,810 tests**
- Sequential: 7 + 13 + 13 + 7 + 10 = **50 tests**
- Savings: **99.94%** (1,656x faster)

## MODIFIED Requirements

None - This is a new feature.

## DELETED Requirements

None - Grid search mode remains available.
