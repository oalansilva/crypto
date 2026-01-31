# Sequential Parameter Optimization

## Problem Statement

Currently, the optimization system tests all parameter combinations simultaneously in a grid search, which becomes exponentially expensive as parameters increase. For example, testing 5 timeframes × 7 values for param1 × 7 values for param2 × 7 values for param3 × 10 stop-loss values = **17,150 combinations**.

This approach:
- Takes too long to complete
- Makes it hard to understand which parameters matter most
- Wastes computational resources testing poor parameter combinations

## Proposed Solution

Implement a **Dynamic Sequential Optimization Workflow** that:
1. **Introspects the selected indicator** to determine its parameters
2. **Generates optimization stages automatically** (1 for timeframe + 1 per indicator param + 1 for stop-loss)
3. **Optimizes one parameter at a time**, using the best result from each stage as the baseline for the next

### Dynamic Stage Generation

The system automatically creates stages based on the indicator's parameter schema:

**Example: RSI (2 parameters)**
- Stage 1: Timeframe
- Stage 2: RSI Period (default: 14, range: 10-20)
- Stage 3: Overbought/Oversold Levels (default: 70/30, range: 65-80 / 20-35)
- Stage 4: Stop-Loss
- **Total: 4 stages**

**Example: MACD (3 parameters)**
- Stage 1: Timeframe
- Stage 2: Fast Period (default: 12, range: 6-18)
- Stage 3: Slow Period (default: 26, range: 20-32)
- Stage 4: Signal Period (default: 9, range: 6-12)
- Stage 5: Stop-Loss
- **Total: 5 stages**

**Example: Bollinger Bands (2 parameters)**
- Stage 1: Timeframe
- Stage 2: Period (default: 20, range: 15-25)
- Stage 3: Standard Deviation (default: 2.0, range: 1.5-3.0)
- Stage 4: Stop-Loss
- **Total: 4 stages**

### Optimization Stages (Generic Flow)

1. **Stage 1: Timeframe Optimization** (Always present)
   - Fixed: Symbol, Strategy, all indicator params at defaults, no stop-loss
   - Variable: Timeframe (test: 5m, 15m, 30m, 1h, 2h, 4h, 1d)
   - Output: Best timeframe

2. **Stage 2 to N+1: Indicator Parameter Optimization** (Dynamic, based on indicator)
   - For each parameter P in the indicator's parameter list:
     - Fixed: Symbol, Strategy, best timeframe, all previously optimized params, remaining params at defaults, no stop-loss, no stop-gain
     - Variable: Parameter P (range defined in indicator schema)
     - Output: Best value for parameter P

3. **Stage N+2: Stop-Loss Optimization** (Always present)
   - Fixed: Symbol, Strategy, best timeframe, all optimized indicator params, no stop-gain
   - Variable: Stop-loss percentage (e.g., 0.5% to 5% in 0.5% steps)
   - Output: Best stop-loss value

4. **Stage N+3: Stop-Gain (Take Profit) Optimization** (Always present, but "None" is an option)
   - Fixed: Symbol, Strategy, best timeframe, all optimized indicator params, best stop-loss
   - Variable: Stop-gain percentage (options: None, 1%, 2%, 3%, 4%, 5%, 7.5%, 10%)
   - Output: Best stop-gain value (or None if no stop-gain performs better)
   - Note: This stage tests whether using a take-profit target improves results

> [!IMPORTANT]
> **Full History Testing**
> 
> ALL tests in ALL stages MUST use the complete available historical data for the selected symbol:
> - ✅ No date range selection (uses all available data automatically)
> - ✅ System detects earliest and latest data points for the symbol
> - ✅ Ensures robust optimization across all market conditions
> - ✅ Prevents overfitting to specific time periods
> - ✅ Provides maximum sample size for statistical significance
> 
> Example: If BTC/USDT has data from 2017-01-01 to 2025-12-30, every test will backtest across this entire 8-year period.

### Indicator Parameter Schema

Each indicator must define its parameters with optimization metadata:

```python
# Example: MACD indicator schema
MACD_PARAMS = {
    "fast_period": {
        "default": 12,
        "optimization_range": {"min": 6, "max": 18, "step": 1},
        "description": "Fast EMA period"
    },
    "slow_period": {
        "default": 26,
        "optimization_range": {"min": 20, "max": 32, "step": 1},
        "description": "Slow EMA period"
    },
    "signal_period": {
        "default": 9,
        "optimization_range": {"min": 6, "max": 12, "step": 1},
        "description": "Signal line period"
    }
}

# Stop-loss and stop-gain ranges are also defined in schema
RISK_MANAGEMENT_PARAMS = {
    "stop_loss": {
        "default": 0.015,  # 1.5%
        "optimization_range": {"min": 0.005, "max": 0.05, "step": 0.005},
        "description": "Stop-loss percentage"
    },
    "stop_gain": {
        "default": None,  # No take-profit by default
        "optimization_range": {"options": [None, 0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.10]},
        "description": "Take-profit percentage (optional)"
    }
}
```

> [!IMPORTANT]
> **Zero Hardcoded Values**
> 
> The system MUST NOT hardcode any parameter values, ranges, or test options. All configuration must come from indicator schemas:
> - ✅ Parameter names: Read from indicator schema
> - ✅ Default values: Read from indicator schema
> - ✅ Optimization ranges: Read from indicator schema
> - ✅ Stop-loss range: Read from risk management schema
> - ✅ Stop-gain options: Read from risk management schema
> - ✅ Number of stages: Calculated dynamically based on parameter count
> 
> This ensures the system works with ANY indicator, including future indicators not yet implemented.

### Dynamic Configuration Flow

1. **User selects indicator** (e.g., "MACD")
2. **System loads indicator schema** → retrieves parameter list and ranges
3. **System generates stage plan**:
   - Stage 1: Timeframe (always)
   - Stages 2 to N+1: One per indicator parameter (from schema)
   - Stage N+2: Stop-loss (range from risk schema)
   - Stage N+3: Stop-gain (options from risk schema)
4. **System executes stages** using schema-defined ranges
5. **System returns optimized configuration** with best values for all parameters

### Performance Comparison Examples

#### MACD (3 parameters)
**Traditional Grid Search:**
- 7 timeframes × 13 fast × 13 slow × 7 signal × 10 stop-loss × 8 stop-gain = **662,480 combinations** ❌

**Dynamic Sequential:**
- Stage 1: 7 tests (timeframes)
- Stage 2: 13 tests (fast_period: 6-18)
- Stage 3: 13 tests (slow_period: 20-32)
- Stage 4: 7 tests (signal_period: 6-12)
- Stage 5: 10 tests (stop-loss)
- Stage 6: 8 tests (stop-gain: None, 1%, 2%, 3%, 4%, 5%, 7.5%, 10%)
- **Total: 58 tests** ✅ (11,422x faster!)

#### RSI (2 parameters)
**Traditional Grid Search:**
- 7 timeframes × 11 period × 16 overbought × 16 oversold × 10 stop-loss × 8 stop-gain = **1,569,792 combinations** ❌

**Dynamic Sequential:**
- Stage 1: 7 tests (timeframes)
- Stage 2: 11 tests (period: 10-20)
- Stage 3: 16 tests (overbought: 65-80)
- Stage 4: 16 tests (oversold: 20-35)
- Stage 5: 10 tests (stop-loss)
- Stage 6: 8 tests (stop-gain: None, 1%, 2%, 3%, 4%, 5%, 7.5%, 10%)
- **Total: 68 tests** ✅ (23,085x faster!)

#### Bollinger Bands (2 parameters)
**Traditional Grid Search:**
- 7 timeframes × 11 period × 16 std_dev × 10 stop-loss × 8 stop-gain = **98,560 combinations** ❌

**Dynamic Sequential:**
- Stage 1: 7 tests (timeframes)
- Stage 2: 11 tests (period: 15-25)
- Stage 3: 16 tests (std_dev: 1.5-3.0, step 0.1)
- Stage 4: 10 tests (stop-loss)
- Stage 5: 8 tests (stop-gain: None, 1%, 2%, 3%, 4%, 5%, 7.5%, 10%)
- **Total: 52 tests** ✅ (1,895x faster!)

## User Review Required

> [!IMPORTANT]
> **Backward Compatibility - Zero Breaking Changes**
> 
> This feature is **100% additive** and does NOT modify existing functionality:
> - ✅ Existing grid search optimization remains unchanged
> - ✅ Current `BacktestForm` continues to work as-is
> - ✅ Existing API endpoints (`/api/optimize`) remain functional
> - ✅ Current optimization results display is not affected
> - ✅ All existing backtests and results remain accessible
> 
> **Implementation Strategy:**
> - New routes: `/api/optimize/sequential/*` (separate from existing `/api/optimize`)
> - New UI components: `SequentialOptimizationWizard.tsx` (separate from `BacktestForm.tsx`)
> - New service: `SequentialOptimizer` (does not modify `BacktestService`)
> - User chooses optimization mode via toggle/tabs in UI
> 
> **Migration Path:**
> Users can continue using the existing grid search indefinitely. Sequential optimization is an **opt-in alternative**, not a replacement.

> [!IMPORTANT]
> **Assumption: Local Optima Risk**
> 
> Sequential optimization assumes that parameters are relatively independent. If there are strong interactions (e.g., param1=10 is best with timeframe=1h but param1=15 is best with timeframe=5m), this approach might miss the global optimum.
> 
> **Mitigation:** After sequential optimization, optionally run a small grid search around the discovered values to verify the result.

> [!WARNING]
> **Breaking Change: New Workflow**
> 
> This introduces a completely new optimization mode. The existing "full grid search" will remain available, but users will need to choose between:
> - **Quick Mode:** Sequential optimization (recommended for exploration)
> - **Exhaustive Mode:** Full grid search (for final validation)

## Proposed Changes

### Backend

#### [NEW] [sequential_optimizer.py](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/backend/app/services/sequential_optimizer.py)

New service to orchestrate sequential optimization stages:
- `SequentialOptimizer` class with methods for each stage
- `run_stage(stage_config)` to execute a single optimization stage
- `run_full_sequence(initial_config)` to run all stages automatically
- Stage result persistence and retrieval

---

#### [MODIFY] [backtest_service.py](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/backend/app/services/backtest_service.py)

Add new endpoint method:
- `run_sequential_optimization(symbol, strategy, param_ranges)` 
- Returns stage-by-stage results with best values propagated

---

#### [MODIFY] [routes.py](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/backend/app/routes.py)

Add new API endpoints:
- `POST /api/optimize/sequential` - Start sequential optimization
- `GET /api/optimize/sequential/{job_id}/stage/{stage_num}` - Get stage results
- `POST /api/optimize/sequential/{job_id}/pause` - Pause current stage
- `POST /api/optimize/sequential/{job_id}/resume` - Resume paused stage
- `POST /api/optimize/sequential/{job_id}/skip` - Skip current stage
- `WS /api/optimize/sequential/{job_id}/ws` - WebSocket for real-time updates

---

#### [NEW] [websocket_manager.py](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/backend/app/services/websocket_manager.py)

WebSocket manager for real-time updates:
- `WebSocketManager` class to handle connections
- `broadcast_test_complete(job_id, test_data)` - Send test completion event
- `broadcast_stage_complete(job_id, stage_data)` - Send stage completion event
- `broadcast_progress_update(job_id, progress)` - Send progress update
- Connection management per job_id

---

### Frontend

#### [NEW] [SequentialOptimizationWizard.tsx](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/frontend/src/components/optimization/SequentialOptimizationWizard.tsx)

New component for sequential optimization UI:
- **Real-time progress tracking** with WebSocket updates
- **Stage-by-stage visualization** showing current, completed, and upcoming stages
- **Live test results table** updating as each test completes
- **Best result highlighting** for current stage
- **Stage control actions**: Pause, Resume, Skip, Re-run
- **Overall progress dashboard** with summary cards for completed stages
- **Final configuration display** when optimization completes

**UI Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  Sequential Optimization: MACD on BTC/USDT             │
│  Overall Progress: Stage 3/6 (50%)                      │
│  ████████████░░░░░░░░░░░░                               │
├─────────────────────────────────────────────────────────┤
│  ✅ Stage 1: Timeframe → 1h                             │
│  ✅ Stage 2: Fast Period → 12                           │
│  🔄 Stage 3: Slow Period (7/13 tests)                   │
│     ┌───────────────────────────────────────────┐      │
│     │ slow_period | PnL      | Win Rate | Trades│      │
│     │ 20          | $1,234   | 38%      | 145   │      │
│     │ 21          | $1,456   | 41%      | 152   │      │
│     │ 22          | $1,789 ⭐| 45%      | 158   │      │
│     │ 23          | Testing...                   │      │
│     └───────────────────────────────────────────┘      │
│     Best so far: slow_period=22, PnL=$1,789            │
│     [Pause] [Skip Stage]                                │
│  ⏳ Stage 4: Signal Period                              │
│  ⏳ Stage 5: Stop-Loss                                  │
│  ⏳ Stage 6: Stop-Gain                                  │
└─────────────────────────────────────────────────────────┘
```

---

#### [MODIFY] [BacktestForm.tsx](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/frontend/src/components/BacktestForm.tsx)

Add optimization mode selector (minimal changes):
- Add tabs/toggle: "Grid Search" vs "Sequential Optimization"
- When "Sequential" is selected, redirect to new `SequentialOptimizationWizard` component
- Existing grid search functionality remains completely unchanged
- No modifications to existing form logic or state management

**UI Change:**
```tsx
// Add at top of BacktestForm
<Tabs>
  <Tab label="Grid Search" /> {/* Existing functionality */}
  <Tab label="Sequential" onClick={() => navigate('/optimize/sequential')} />
</Tabs>
```

---

#### [NEW] [SequentialResults.tsx](file:///c:/Users/alans.triggo/OneDrive%20-%20Corpay/Documentos/projetos/crypto/frontend/src/components/results/SequentialResults.tsx)

Display sequential optimization results:
- Accordion/tabs for each stage
- Chart showing performance improvement across stages
- Final recommended configuration card
- "Run Full Grid Search" button to validate around discovered values

## Verification Plan

### Automated Tests

```bash
# Backend unit tests
pytest backend/tests/test_sequential_optimizer.py

# Integration test
pytest backend/tests/test_sequential_optimization_flow.py
```

### Manual Verification

1. Start sequential optimization for BTC/USDT with MACD strategy
2. Verify each stage completes and shows best result
3. Confirm final configuration uses best values from all stages
4. Compare performance vs traditional grid search (time and quality)
5. Test "skip stage" and "re-run stage" functionality
