# Hybrid Grid Optimization for Combo Strategies

**Status:** Proposed  
**Created:** 2026-01-19  
**Author:** System  
**Target:** `/combo/select` (Combo Optimizer)  
**Scope:** All combo strategies (CRUZAMENTOMEDIAS, RSI, MACD, etc.)

## Why

The current Combo Optimizer (`/combo/select`) cannot find globally optimal parameter combinations for strategies with correlated parameters. This results in suboptimal strategy recommendations, leaving significant performance on the table.

**Concrete Impact:**
- Current optimizer finds configurations with +22,973% return
- Manual testing revealed superior configuration with +133,453% return (5.8x better)
- Users cannot trust automated optimization results
- **Problem affects ANY strategy with correlated parameters** (not just Moving Averages)

This change enables the Combo Optimizer to discover truly optimal combinations by testing correlated parameters jointly via Grid Search, while maintaining computational efficiency through hybrid optimization.

## Problem Statement

The current Combo Optimizer suffers from the "Local Maximum Trap" when optimizing correlated parameters. 

**Example 1: CRUZAMENTOMEDIAS (Moving Averages)**
- The "Antiga" configuration (`media_curta=3, media_inter=32, media_longa=37, stop_loss=2.7%`) achieves +133,453% return
- The Combo Optimizer found "Nova DeepBacktest" (`media_curta=19, media_inter=21, media_longa=35, stop_loss=4.3%`) with only +22,973% return
- The optimizer missed "Antiga" because it tests `media_curta=3` with **default** values for other MAs, where it performs poorly

**Example 2: RSI Multi-Timeframe**
- RSI strategies often use multiple timeframes (e.g., `rsi_fast`, `rsi_slow`)
- Testing `rsi_fast=14` with default `rsi_slow=28` may perform poorly
- But `rsi_fast=14` with `rsi_slow=50` could be optimal
- Sequential testing misses this combination

**Example 3: Bollinger Bands + ATR**
- `bb_length` and `atr_multiplier` are often correlated
- Optimal combination depends on both values together
- Sequential optimization finds local maximum, not global

## Root Cause

Sequential optimization (used in `ComboOptimizer.run_optimization`) assumes parameters are independent. For strategies with correlated parameters:
- Their effectiveness depends on the **combination**, not individual values
- Testing them sequentially creates bias toward "safe" values that work with any partner
- **This affects multiple strategy types**, not just Moving Averages

## Proposed Solution

Implement **Hybrid Grid Optimization** with **metadata-driven correlation detection**:

1. **Metadata-Driven Correlation Groups**
   - Each combo template defines which parameters are correlated
   - Example: `"correlated_groups": [["media_curta", "media_inter", "media_longa"]]`
   - Works for ANY strategy (RSI, MACD, BBands, custom strategies)

2. **Grid Search for Correlated Parameters**
   - Test all combinations of correlated parameter groups
   - Example: 7 values × 6 values × 7 values = ~294 combinations
   - Guarantees finding the global maximum for correlated params
   - **Leverage existing parallelization** (ProcessPoolExecutor already in place)

3. **Sequential Search for Independent Parameters**
   - After finding best correlated combo, optimize independent params sequentially
   - Example: 63 stop_loss values tested with the winning combo
   - Total: 294 + 63 = **357 tests** (vs. 50,000+ for full grid)

4. **Single Round Execution**
   - Disable Iterative Refinement when Grid Search is active (`max_rounds = 1`)
   - Grid already finds global maximum, no refinement needed
   - Saves ~75% execution time

5. **Deep Backtest Already Enabled** ✅
   - Combo Optimizer already uses Deep Backtest by default
   - All tests use 15m intraday validation
   - No changes needed here

## Benefits

- **Universal**: Works for ANY strategy with correlated parameters
- **Finds Global Maximum**: Eliminates local maximum trap
- **Computationally Efficient**: 357 tests vs. 50,000+ for naive full grid
- **Mathematically Sound**: Grid Search guarantees optimal solution within search space
- **Leverages Existing Infrastructure**: Uses current parallelization (ProcessPoolExecutor)
- **Backward Compatible**: Falls back to sequential for strategies without correlated params
- **Extensible**: Easy to add correlation metadata to new strategies

## Implementation Details

### 1. Database Schema Changes

**Storage Approach:** Use existing `optimization_schema` JSON field (no migration needed)

```python
# In combo_templates table (existing):
optimization_schema = {
    "correlated_groups": [
        ["media_curta", "media_inter", "media_longa"]
    ],
    "parameters": {
        "media_curta": {"min": 3, "max": 15, "step": 2},
        "media_inter": {"min": 15, "max": 35, "step": 4},
        "media_longa": {"min": 25, "max": 60, "step": 5},
        "stop_loss": {"min": 0.005, "max": 0.13, "step": 0.002}
    }
}
```

**Benefits:**
- No database migration required
- Backward compatible (existing templates have `optimization_schema = null`)
- Easy to update via SQL

### 2. Validation & Error Handling

**Validation Rules:**
1. All parameters in `correlated_groups` must exist in `parameters`
2. No duplicate parameters across groups
3. Grid size per group must not exceed 1,000 combinations

**Implementation:**
```python
def _validate_correlation_metadata(self, template_metadata):
    """Validate correlated_groups against available parameters."""
    correlated_groups = template_metadata.get("optimization_schema", {}).get("correlated_groups", [])
    parameters = template_metadata.get("optimization_schema", {}).get("parameters", {})
    
    if not correlated_groups:
        return  # No validation needed (backward compatible)
    
    all_correlated_params = set()
    
    for group in correlated_groups:
        for param in group:
            # Check if parameter exists
            if param not in parameters:
                raise ValueError(
                    f"Invalid correlated_groups: parameter '{param}' not found in parameters. "
                    f"Available: {list(parameters.keys())}"
                )
            
            # Check for duplicates
            if param in all_correlated_params:
                raise ValueError(
                    f"Invalid correlated_groups: parameter '{param}' appears in multiple groups"
                )
            all_correlated_params.add(param)
```

### 3. Stage Execution Order

**Defined Order:**
1. **Timeframe** (if not fixed) - Sequential
2. **All Grid Search stages** (correlated groups) - Parallel within each grid
3. **All Sequential stages** (independent params) - Sequential

**Rationale:**
- Timeframe first (changes data, must be locked early)
- All Grids next (find optimal combinations for strategy logic)
- Sequential last (fine-tune risk params with optimal strategy)

**Example:**
```python
# CRUZAMENTOMEDIAS execution order:
Stage 1: Timeframe [7 tests] - Sequential
Stage 2: MA Grid [336 tests] - Grid Search (parallel)
Stage 3: Stop Loss [63 tests] - Sequential

# BBANDS_ATR execution order:
Stage 1: Timeframe [7 tests] - Sequential
Stage 2: BBands Grid [20 tests] - Grid Search (parallel)
Stage 3: ATR Grid [15 tests] - Grid Search (parallel)
Stage 4: Stop Loss [63 tests] - Sequential
```

### 4. Backward Compatibility & Migration

**Automatic Fallback:**
```python
def generate_stages(self, template_name, symbol, fixed_timeframe, custom_ranges):
    """Generate stages with automatic fallback to sequential."""
    metadata = self.combo_service.get_template_metadata(template_name)
    optimization_schema = metadata.get("optimization_schema", {})
    correlated_groups = optimization_schema.get("correlated_groups", [])
    
    if not correlated_groups:
        # FALLBACK: No correlation metadata → use Sequential (current behavior)
        logging.info(f"No correlated_groups defined for {template_name} - using Sequential optimization")
        return self._generate_sequential_stages(...)
    else:
        # NEW: Use Hybrid Grid optimization
        logging.info(f"Using Grid Search for {len(correlated_groups)} correlated groups")
        return self._generate_hybrid_stages(...)
```

**Migration Strategy for Existing Templates:**
```sql
-- Update CRUZAMENTOMEDIAS template (example)
UPDATE combo_templates
SET optimization_schema = json('{
    "correlated_groups": [
        ["media_curta", "media_inter", "media_longa"]
    ],
    "parameters": {
        "media_curta": {"min": 3, "max": 15, "step": 2},
        "media_inter": {"min": 15, "max": 35, "step": 4},
        "media_longa": {"min": 25, "max": 60, "step": 5},
        "stop_loss": {"min": 0.005, "max": 0.13, "step": 0.002}
    }
}')
WHERE name = 'CRUZAMENTOMEDIAS';
```

**Documentation:**
- Create migration guide: `docs/adding_correlation_metadata.md`
- List recommended `correlated_groups` for all prebuilt templates

### 5. UI Considerations

**Decision: Admin-Only Configuration** (Phase 1)

**Rationale:**
- Defining correlations requires deep understanding of strategy logic
- Most users will use prebuilt templates (already configured)
- Custom templates can start with Sequential (safe default)

**Implementation:**
- **Phase 1 (This Feature):** No UI changes
  - Prebuilt templates configured via SQL
  - Custom templates use Sequential by default
  - Advanced users can edit database directly

- **Phase 2 (Future Enhancement):** Add UI
  - "Advanced" section in template editor
  - Checkbox: "Enable Grid Search for correlated parameters"
  - Multi-select: "Select parameters to optimize together"
  - Validation: Show estimated grid size

**Example Future UI:**
```
┌─────────────────────────────────────────┐
│ Template: My Custom Strategy           │
├─────────────────────────────────────────┤
│ Parameters:                             │
│ ☑ rsi_period (14)                       │
│ ☑ rsi_oversold (30)                     │
│ ☑ rsi_overbought (70)                   │
│ ☐ stop_loss (1.5%)                      │
│                                         │
│ ☑ Enable Grid Search                    │
│   Selected: rsi_period, rsi_oversold,   │
│             rsi_overbought              │
│   Grid Size: 125 combinations           │
│   Est. Time: ~4 minutes                 │
└─────────────────────────────────────────┘
```

### 9. Logging & Observability

**Requirement:** Users must be able to track optimization progress in real-time with detailed logs.

**Log Levels:**
- `INFO`: Progress updates, stage transitions, best results
- `DEBUG`: Individual test details, parameter combinations
- `WARNING`: Grid size warnings, validation issues

**Example Log Output:**

```log
INFO: ========================================
INFO: Starting Combo Optimization
INFO: Template: CRUZAMENTOMEDIAS
INFO: Symbol: BTC/USDT
INFO: Timeframe: 1d
INFO: Deep Backtest: ENABLED (15m validation)
INFO: ========================================

INFO: Loading correlation metadata...
INFO: Found 1 correlated group: ['media_curta', 'media_inter', 'media_longa']
INFO: Grid Search ENABLED - setting max_rounds=1 (no refinement)

INFO: ========================================
INFO: STAGE 1/3: Timeframe Optimization
INFO: Mode: Sequential
INFO: Tests: 7
INFO: ========================================
INFO: [1/7] Testing timeframe=15m → Sharpe: 0.85, Trades: 142
INFO: [2/7] Testing timeframe=30m → Sharpe: 1.12, Trades: 98
INFO: [3/7] Testing timeframe=1h → Sharpe: 1.45, Trades: 67
INFO: [4/7] Testing timeframe=4h → Sharpe: 1.78, Trades: 34 ✓ BEST
INFO: [5/7] Testing timeframe=1d → Sharpe: 1.62, Trades: 28
INFO: [6/7] Testing timeframe=1w → Sharpe: 0.92, Trades: 12
INFO: [7/7] Testing timeframe=1M → Sharpe: 0.45, Trades: 5
INFO: ✓ Stage 1 Complete - Best: timeframe=4h (Sharpe: 1.78)
INFO: Locked: {'timeframe': '4h'}

INFO: ========================================
INFO: STAGE 2/3: Moving Averages Grid Search
INFO: Mode: Grid Search (Parallel)
INFO: Parameters: ['media_curta', 'media_inter', 'media_longa']
INFO: Grid Size: 7 × 6 × 8 = 336 combinations
INFO: Workers: 4 (parallel execution)
INFO: Estimated Time: ~3 minutes
INFO: ========================================
INFO: [Grid 1/336] (3, 15, 25) → Sharpe: 0.92, Return: +12,453%, Trades: 45
INFO: [Grid 2/336] (3, 15, 30) → Sharpe: 1.05, Return: +18,762%, Trades: 48
INFO: [Grid 3/336] (3, 15, 35) → Sharpe: 1.18, Return: +24,891%, Trades: 52
...
INFO: [Grid 50/336] (3, 27, 40) → Sharpe: 1.42, Return: +45,672%, Trades: 38
INFO: [Grid 100/336] (5, 23, 45) → Sharpe: 1.67, Return: +78,234%, Trades: 42
INFO: [Grid 150/336] (3, 32, 37) → Sharpe: 2.84, Return: +133,453%, Trades: 75 ✓ NEW BEST!
INFO: [Grid 200/336] (7, 27, 50) → Sharpe: 1.45, Return: +52,891%, Trades: 36
INFO: [Grid 250/336] (9, 31, 55) → Sharpe: 1.38, Return: +48,123%, Trades: 32
INFO: [Grid 300/336] (13, 35, 60) → Sharpe: 1.12, Return: +32,456%, Trades: 28
INFO: [Grid 336/336] (15, 35, 60) → Sharpe: 0.98, Return: +28,734%, Trades: 25
INFO: ✓ Stage 2 Complete - Best: (3, 32, 37) (Sharpe: 2.84, Return: +133,453%)
INFO: Locked: {'timeframe': '4h', 'media_curta': 3, 'media_inter': 32, 'media_longa': 37}

INFO: ========================================
INFO: STAGE 3/3: Stop Loss Optimization
INFO: Mode: Sequential
INFO: Tests: 63
INFO: Using locked combo: media_curta=3, media_inter=32, media_longa=37
INFO: ========================================
INFO: [1/63] Testing stop_loss=0.5% → Sharpe: 2.12, Return: +98,234%, Trades: 112
INFO: [2/63] Testing stop_loss=0.7% → Sharpe: 2.34, Return: +108,567%, Trades: 98
...
INFO: [15/63] Testing stop_loss=2.7% → Sharpe: 2.84, Return: +133,453%, Trades: 75 ✓ BEST
...
INFO: [63/63] Testing stop_loss=13.0% → Sharpe: 1.45, Return: +67,891%, Trades: 42
INFO: ✓ Stage 3 Complete - Best: stop_loss=2.7% (Sharpe: 2.84)

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
INFO: 
INFO: METRICS:
INFO:   Sharpe Ratio: 2.84
INFO:   Total Return: +133,453%
INFO:   Total Trades: 75
INFO:   Win Rate: 68.4%
INFO:   Max Drawdown: -12.3%
INFO: ========================================
```

**Debug Mode (Optional):**
```log
DEBUG: Worker 1 starting test: (3, 15, 25)
DEBUG: Loading 15m data for Deep Backtest: 294,911 candles
DEBUG: Calculating indicators: SMA(3), SMA(15), SMA(25)
DEBUG: Generating signals: 1,247 candles processed
DEBUG: Simulating execution with stop_loss=1.5%
DEBUG: Trade 1: Entry=50,234.5 @ 2023-01-15 14:00, Exit=51,123.8 @ 2023-01-18 09:30 (Stop hit)
DEBUG: Trade 2: Entry=52,456.2 @ 2023-01-20 10:15, Exit=54,891.3 @ 2023-01-25 16:45 (Signal)
DEBUG: Worker 1 completed: Sharpe=0.92, Return=+12,453%, Time=2.3s
```

**Warning Examples:**
```log
WARNING: Grid size (125,000) exceeds recommended limit (1,000)
WARNING: Estimated time: ~70 hours at 0.5s/test
WARNING: Consider increasing step size or reducing range
WARNING: Proceeding with optimization...

WARNING: Parameter 'media_longa_TYPO' in correlated_groups not found
WARNING: Available parameters: ['media_curta', 'media_inter', 'media_longa', 'stop_loss']
ERROR: Validation failed - aborting optimization
```

**Progress Indicators:**
- Percentage complete: `[Grid 150/336] (44.6%)`
- ETA: `Estimated completion: 2m 15s remaining`
- Speed: `Average: 0.52s/test, Current batch: 0.48s/test`

## User Impact

- **Automatic**: No UI changes required; optimizer becomes smarter
- **Faster Discovery**: Finds superior strategies automatically
- **Confidence**: Users can trust optimization results are truly optimal
- **Same Performance**: Parallel execution keeps optimization fast (~5-10 minutes)
- **Works for all strategies**: RSI, MACD, BBands, custom strategies, etc.
- **Backward Compatible**: Existing templates continue to work (Sequential fallback)
- **Full Observability**: Detailed logs for tracking progress and debugging
