# Spec: Real-Time Optimization UI

## ADDED Requirements

### Requirement: Pre-Optimization Parameter Review

The system MUST display a configuration screen before starting optimization where:
1. User reviews and can modify ALL optimization ranges for indicator parameters
2. User reviews and can modify risk management ranges (stop-loss, stop-gain)
3. System pre-fills with market best practices (most commonly used values)
4. User can accept defaults or customize any range
5. Clear indication of which values are "market standard" vs custom

#### Scenario: Review MACD Parameters with Market Defaults

**Given** user selects MACD strategy for sequential optimization  
**When** the configuration screen loads  
**Then** the UI displays:

```
📋 Review Optimization Parameters

Indicator: MACD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fast Period (Range)
  Min: [6]  Max: [18]  Step: [1]
  💡 Market Standard: 6-18 (most traders use 12)
  
Slow Period (Range)  
  Min: [20]  Max: [32]  Step: [1]
  💡 Market Standard: 20-32 (most traders use 26)
  
Signal Period (Range)
  Min: [6]  Max: [12]  Step: [1]
  💡 Market Standard: 6-12 (most traders use 9)

Risk Management
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stop-Loss (Range)
  Min: [0.5%]  Max: [5%]  Step: [0.5%]
  💡 Market Standard: 0.5%-5% (most traders use 1-2%)
  
Stop-Gain/Take Profit (Options)
  ☑ None  ☑ 1%  ☑ 2%  ☑ 3%  ☑ 4%  ☑ 5%  ☑ 7.5%  ☑ 10%
  💡 Market Standard: Test all options (many traders don't use take-profit)

[Reset to Defaults] [Start Optimization]
```

**And** all fields are editable  
**And** "Market Standard" hints are shown for each parameter

#### Scenario: Customize Parameter Ranges

**Given** user is on the parameter review screen  
**When** user changes Fast Period range to Min: 10, Max: 15  
**And** clicks "Start Optimization"  
**Then** the system uses the custom range [10-15] for Stage 2  
**And** displays a badge "Custom Range" next to Fast Period in the progress UI

#### Scenario: Market Best Practices Tooltip

**Given** user hovers over "💡 Market Standard" hint  
**When** tooltip appears  
**Then** it displays:
```
Market Best Practices:
- 70% of traders use fast_period between 10-14
- Most common value: 12
- Conservative range: 6-18 captures most variations
- Source: Industry surveys & backtesting studies
```

### Requirement: Live Progress Tracking

The system MUST provide a real-time web interface showing:
1. Current stage being executed
2. Progress within the current stage (e.g., "Testing 5/13 values")
3. List of all tests executed in the current stage with their results
4. Best result found so far in the current stage
5. Overall progress across all stages

#### Scenario: User Monitors Stage 2 Execution

**Given** sequential optimization is running on Stage 2 (fast_period)  
**When** the user views the optimization UI  
**Then** the interface displays:
- Stage indicator: "Stage 2/6: Fast Period Optimization"
- Progress bar: "Testing 8/13 values (61%)"
- Live test results table showing:
  - fast_period=6: PnL=$1,234, Win Rate=35%
  - fast_period=7: PnL=$1,456, Win Rate=38%
  - fast_period=8: PnL=$1,789, Win Rate=42% ⭐ (best so far)
  - ...currently testing fast_period=9...
- Best result card: "Best: fast_period=8, PnL=$1,789"

**And** the UI updates automatically as new tests complete

### Requirement: Stage Summary Cards

After each stage completes, the system MUST display a summary card showing:
1. Stage name and number
2. Parameter optimized
3. All tested values and their performance
4. Best value selected
5. Locked parameters from previous stages

#### Scenario: View Completed Stage Summary

**Given** Stage 2 (fast_period) has completed  
**When** the user views the stage summary  
**Then** the UI displays a card with:
- Header: "✅ Stage 2 Complete: Fast Period"
- Best result: "fast_period=12, PnL=$2,145, Win Rate=45%"
- Full results table (sortable):
  - All 13 tested values
  - Performance metrics for each
  - Visual indicator for best value
- Locked params: "timeframe=1h (from Stage 1)"
- Action buttons: "Re-run Stage" | "Continue to Stage 3"

### Requirement: Overall Progress Dashboard

The system MUST provide a dashboard view showing:
1. Progress across all stages (e.g., "Stage 3/6 - 50% complete")
2. Summary cards for all completed stages
3. Current stage in progress
4. Upcoming stages (grayed out)
5. Final optimized configuration (when complete)

#### Scenario: Mid-Optimization Dashboard View

**Given** optimization is on Stage 3 of 6  
**When** the user views the dashboard  
**Then** it displays:
- Overall progress: "Stage 3/6 - 50% Complete"
- Completed stages section:
  - ✅ Stage 1: Timeframe → 1h
  - ✅ Stage 2: Fast Period → 12
- Current stage section:
  - 🔄 Stage 3: Slow Period (in progress, 7/13 tests)
- Upcoming stages section:
  - ⏳ Stage 4: Signal Period
  - ⏳ Stage 5: Stop-Loss
  - ⏳ Stage 6: Stop-Gain

### Requirement: Real-Time WebSocket Updates

The system MUST use WebSocket connections to push updates to the UI:
1. Test completion events
2. Stage completion events
3. Progress updates
4. Best result updates

#### Scenario: Receive Real-Time Test Update

**Given** user has optimization UI open  
**And** WebSocket connection is established  
**When** a test completes on the backend  
**Then** the UI receives a WebSocket message:
```json
{
  "event": "test_complete",
  "stage": 2,
  "test_number": 8,
  "total_tests": 13,
  "params": {"fast_period": 8},
  "metrics": {"total_pnl": 1789.45, "win_rate": 0.42, "total_trades": 156}
}
```

**And** the UI automatically updates the test results table  
**And** updates the progress bar to "8/13 (61%)"  
**And** highlights the new best result if applicable

### Requirement: Stage Control Actions

Users MUST be able to:
1. Pause the current stage
2. Resume a paused stage
3. Skip the current stage (with default value)
4. Re-run a completed stage with different ranges
5. Cancel the entire optimization

#### Scenario: Pause and Resume Stage

**Given** Stage 3 is running (5/13 tests complete)  
**When** user clicks "Pause"  
**Then** the backend stops executing new tests  
**And** the UI shows "⏸ Paused at 5/13 tests"  
**And** displays a "Resume" button  

**When** user clicks "Resume"  
**Then** the backend continues from test 6  
**And** the UI shows "🔄 In Progress: 6/13 tests"

### Requirement: Performance Trend Visualization

The system MUST clearly show whether the strategy is improving or degrading after each stage:
1. Display performance delta between stages (e.g., "+$345 from Stage 2")
2. Show cumulative performance chart across all completed stages
3. Use visual indicators (green ↑ for improvement, red ↓ for degradation)
4. Highlight the best overall performance achieved so far

#### Scenario: Strategy Improves with Each Stage

**Given** optimization has completed Stages 1-3  
**When** the user views the performance trend  
**Then** the UI displays:

```
Performance Progression:
┌─────────────────────────────────────────────────┐
│ Baseline (defaults): PnL = $1,000               │
├─────────────────────────────────────────────────┤
│ ✅ Stage 1: Timeframe → 1h                      │
│    PnL: $1,234 (+$234 ↑ +23.4%)                │
├─────────────────────────────────────────────────┤
│ ✅ Stage 2: Fast Period → 12                    │
│    PnL: $1,567 (+$333 ↑ +27.0% from Stage 1)   │
├─────────────────────────────────────────────────┤
│ ✅ Stage 3: Slow Period → 26                    │
│    PnL: $1,789 (+$222 ↑ +14.2% from Stage 2)   │
│    🏆 Best so far: +78.9% from baseline         │
└─────────────────────────────────────────────────┘

[Line Chart]
 $1,800 │                              ●
 $1,600 │                      ●
 $1,400 │              ●
 $1,200 │      ●
 $1,000 │  ●
        └────────────────────────────────
         Base  S1   S2   S3   S4   S5
```

**And** all improvements are shown in green with ↑ arrows

#### Scenario: Strategy Degrades in a Stage

**Given** Stage 4 completes with worse performance than Stage 3  
**When** the user views the performance trend  
**Then** the UI displays:

```
┌─────────────────────────────────────────────────┐
│ ✅ Stage 3: Slow Period → 26                    │
│    PnL: $1,789                                  │
├─────────────────────────────────────────────────┤
│ ⚠️  Stage 4: Signal Period → 9                  │
│    PnL: $1,654 (-$135 ↓ -7.5% from Stage 3)    │
│    ⚠️  Performance decreased                    │
└─────────────────────────────────────────────────┘
```

**And** the degradation is shown in red/yellow with ↓ arrow  
**And** a warning icon ⚠️ indicates the decrease  
**And** the UI suggests: "Consider re-running Stage 4 with different range"

#### Scenario: Overall Improvement Summary

**Given** all 6 stages completed  
**When** the user views the final summary  
**Then** the UI displays:

```
🎯 Optimization Complete!

Final Performance: $2,145
Baseline Performance: $1,000
Total Improvement: +$1,145 (+114.5%) 🚀

Stage-by-Stage Breakdown:
  Stage 1 (Timeframe):    +23.4% ✅
  Stage 2 (Fast Period):  +27.0% ✅
  Stage 3 (Slow Period):  +14.2% ✅
  Stage 4 (Signal):       -7.5%  ⚠️
  Stage 5 (Stop-Loss):    +18.3% ✅
  Stage 6 (Stop-Gain):    +5.1%  ✅

Most Impactful Stage: Stage 2 (+27.0%)
Least Impactful Stage: Stage 6 (+5.1%)
```

**And** a visual chart shows the cumulative improvement trend

## MODIFIED Requirements

None - This is a new UI feature.

## DELETED Requirements

None - Existing functionality remains.
