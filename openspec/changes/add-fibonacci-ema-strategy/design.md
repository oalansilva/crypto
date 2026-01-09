# Design: Fibonacci (0.5 / 0.618) + EMA 200 Strategy

## Overview
This design document outlines the implementation approach for the Fibonacci retracement strategy combined with EMA 200 trend filter. This is a professional institutional pullback strategy that provides excellent risk/reward ratios.

## Strategy Logic

### Core Concept
The strategy combines three key elements:
1. **Trend Filter (EMA 200)**: Only trade in the direction of the long-term trend
2. **Swing Detection**: Identify recent swing highs and lows to calculate Fibonacci levels
3. **Fibonacci Retracement**: Enter on pullbacks to institutional levels (0.5 and 0.618)

### Mathematical Foundation

#### Fibonacci Retracement Calculation
```
Given:
  swing_high = recent local maximum
  swing_low = recent local minimum
  
Calculate:
  range = swing_high - swing_low
  fib_0.5 = swing_low + (range * 0.5)      # 50% retracement
  fib_0.618 = swing_low + (range * 0.618)  # Golden ratio (61.8%)
```

#### Swing Detection Algorithm
```
Swing High:
  - Price[i] > Price[i-lookback:i]  (higher than all previous bars)
  - Price[i] > Price[i+1:i+lookback] (higher than all subsequent bars)
  - Confirmed after lookback bars pass without breaking the high

Swing Low:
  - Price[i] < Price[i-lookback:i]  (lower than all previous bars)
  - Price[i] < Price[i+1:i+lookback] (lower than all subsequent bars)
  - Confirmed after lookback bars pass without breaking the low
```

### Buy Signal Logic
```
BUY when ALL conditions are true:
1. close > EMA_200                           # Bullish trend filter
2. swing_high and swing_low identified       # Valid Fibonacci range
3. (abs(close - fib_0.5) / close <= tolerance) OR
   (abs(close - fib_0.618) / close <= tolerance)  # Price at Fib level
4. bounce_confirmation                       # Price reversal detected
```

**Bounce Confirmation**:
- Current candle closes higher than it opened (bullish candle)
- OR current close > previous close (upward momentum)
- After touching or approaching Fibonacci level

### Sell Signal Logic
```
SELL when ANY condition is true:
1. close < EMA_200                    # Trend reversal
2. close >= swing_high                # Target reached (resistance)
3. stop_loss triggered                # Risk management
```

## Implementation Architecture

### 1. Strategy Class (`FibonacciEmaStrategy`)

**File**: `backend/app/strategies/fibonacci_ema.py`

**Responsibilities**:
- Detect swing highs and swing lows
- Calculate Fibonacci retracement levels
- Calculate EMA 200 using `pandas_ta.ema()`
- Generate buy/sell signals based on logic above
- Store simulation data with Fibonacci levels for visualization

**Parameters**:
- `ema_period` (int, default=200): EMA period for trend filter
- `swing_lookback` (int, default=20): Bars to look back for swing detection
- `fib_level_1` (float, default=0.5): First Fibonacci retracement level
- `fib_level_2` (float, default=0.618): Second Fibonacci retracement level (golden ratio)
- `level_tolerance` (float, default=0.005): Tolerance for price touching Fibonacci level (0.5%)

**Key Methods**:
- `__init__(config: dict)`: Initialize with parameters
- `_detect_swings(df: pd.DataFrame) -> tuple`: Detect swing highs and lows
- `_calculate_fibonacci(swing_high, swing_low) -> dict`: Calculate Fibonacci levels
- `_is_at_fib_level(price, fib_level, tolerance) -> bool`: Check if price is at Fibonacci level
- `_detect_bounce(df, index) -> bool`: Detect price bounce/reversal
- `generate_signals(df: pd.DataFrame) -> pd.Series`: Generate signals

### 2. Swing Detection Implementation

```python
def _detect_swings(self, df: pd.DataFrame) -> tuple:
    """
    Detect swing highs and swing lows using rolling window.
    
    Returns:
        tuple: (swing_highs_series, swing_lows_series)
    """
    lookback = self.swing_lookback
    
    # Swing High: local maximum
    swing_highs = pd.Series(False, index=df.index)
    for i in range(lookback, len(df) - lookback):
        window_before = df['high'].iloc[i-lookback:i]
        window_after = df['high'].iloc[i+1:i+lookback+1]
        current = df['high'].iloc[i]
        
        if (current > window_before.max()) and (current > window_after.max()):
            swing_highs.iloc[i] = True
    
    # Swing Low: local minimum
    swing_lows = pd.Series(False, index=df.index)
    for i in range(lookback, len(df) - lookback):
        window_before = df['low'].iloc[i-lookback:i]
        window_after = df['low'].iloc[i+1:i+lookback+1]
        current = df['low'].iloc[i]
        
        if (current < window_before.min()) and (current < window_after.min()):
            swing_lows.iloc[i] = True
    
    return swing_highs, swing_lows
```

### 3. Fibonacci Calculation

```python
def _calculate_fibonacci(self, swing_high: float, swing_low: float) -> dict:
    """
    Calculate Fibonacci retracement levels.
    
    Args:
        swing_high: Recent swing high price
        swing_low: Recent swing low price
        
    Returns:
        dict: Fibonacci levels with their prices
    """
    range_price = swing_high - swing_low
    
    return {
        'swing_high': swing_high,
        'swing_low': swing_low,
        'fib_0.5': swing_low + (range_price * self.fib_level_1),
        'fib_0.618': swing_low + (range_price * self.fib_level_2),
        'range': range_price
    }
```

### 4. Strategy Registration

**File**: `backend/app/services/backtest_service.py`

**Changes**:
- Import `FibonacciEmaStrategy` class
- Add conditional check in `_get_strategy()` method:
  ```python
  if strategy_name_lower == 'fibonacciema':
      strategy_config = {"name": name_or_config}
      if params:
          strategy_config.update(params)
      return FibonacciEmaStrategy(strategy_config)
  ```

### 5. Schema Definition

**File**: `backend/app/schemas/indicator_params.py`

**Schema Structure**:
```python
FIBONACCI_EMA_SCHEMA = IndicatorSchema(
    name="FIBONACCI_EMA",
    display_name="Fibonacci (0.5 / 0.618) + EMA 200",
    category="Pullback",
    parameters=[
        ParameterDef(name="ema_period", type="int", default=200, min=100, max=300, step=50),
        ParameterDef(name="swing_lookback", type="int", default=20, min=10, max=40, step=5),
        ParameterDef(name="fib_level_1", type="float", default=0.5, min=0.382, max=0.618, step=0.05),
        ParameterDef(name="fib_level_2", type="float", default=0.618, min=0.5, max=0.786, step=0.05),
        ParameterDef(name="level_tolerance", type="float", default=0.005, min=0.001, max=0.01, step=0.001),
    ]
)
```

## Visualization

### Indicator Metadata
The strategy will return rich indicator metadata for visualization:

```python
indicators = [
    {
        "name": "EMA_200",
        "type": "line",
        "color": "#3b82f6",  # Blue
        "panel": "main",
        "data": [{"time": "...", "value": ...}, ...]
    },
    {
        "name": "Fib_0.5",
        "type": "horizontal",
        "color": "#10b981",  # Green
        "panel": "main",
        "value": 45000,
        "data": [{"time": "...", "value": 45000}, ...]
    },
    {
        "name": "Fib_0.618",
        "type": "horizontal",
        "color": "#f59e0b",  # Gold
        "panel": "main",
        "value": 46180,
        "data": [{"time": "...", "value": 46180}, ...]
    },
    {
        "name": "Swing_High",
        "type": "marker",
        "color": "#ef4444",  # Red
        "panel": "main",
        "shape": "triangle-down",
        "data": [{"time": "2024-01-15", "value": 50000}, ...]
    },
    {
        "name": "Swing_Low",
        "type": "marker",
        "color": "#10b981",  # Green
        "panel": "main",
        "shape": "triangle-up",
        "data": [{"time": "2024-01-10", "value": 40000}, ...]
    }
]
```

### Chart Layout
- **Main Panel**: 
  - Candlesticks
  - EMA 200 (blue line)
  - Fibonacci 0.5 (green horizontal line)
  - Fibonacci 0.618 (gold horizontal line)
  - Swing High markers (red triangles down)
  - Swing Low markers (green triangles up)
  - Optional: Tolerance zones (shaded areas)

## Optimization Support

### Parameter Ranges
The strategy supports Grid Search optimization with these suggested ranges:
- `ema_period`: 100-300 (step 50) → 5 values
- `swing_lookback`: 10-40 (step 5) → 7 values
- `fib_level_1`: 0.382-0.618 (step 0.05) → 5 values
- `fib_level_2`: 0.5-0.786 (step 0.05) → 6 values
- `level_tolerance`: 0.001-0.01 (step 0.001) → 10 values

**Total combinations**: 5 × 7 × 5 × 6 × 10 = 10,500 combinations

### Optimization Strategy
Due to high number of combinations, recommend:
1. **Phase 1**: Optimize `ema_period` and `swing_lookback` (35 combinations)
2. **Phase 2**: Fix best EMA/swing, optimize Fibonacci levels (30 combinations)
3. **Phase 3**: Fine-tune `level_tolerance` (10 combinations)

## Trade-offs and Decisions

### Why Swing Lookback = 20?
- 20 bars on 4h timeframe = ~3.3 days
- Captures meaningful swings without being too sensitive
- Industry standard for swing detection

### Why Fibonacci 0.5 and 0.618?
- **0.5 (50%)**: Psychological level, widely watched
- **0.618 (61.8%)**: Golden ratio, institutional favorite
- These levels have highest probability of bounce

### Why Tolerance = 0.5%?
- Allows for price "noise" around exact level
- Too tight (0.1%) = miss valid entries
- Too loose (2%) = enter too far from level
- 0.5% balances precision and flexibility

### Swing Detection: Forward-Looking Issue
**Problem**: Swing detection requires future data (lookback bars after the swing)
**Solution**: 
- Mark swing as "potential" when detected
- Confirm swing after lookback bars pass
- Only use confirmed swings for Fibonacci calculation
- This introduces lag but ensures validity

## Performance Considerations

### Computational Complexity
- Swing detection: O(n * lookback) for each bar
- Fibonacci calculation: O(1) per swing
- Signal generation: O(n)
- **Total**: O(n * lookback) - acceptable for backtesting

### Optimization
- Pre-calculate swings once, reuse for all Fibonacci levels
- Cache Fibonacci levels to avoid recalculation
- Use vectorized operations where possible (pandas)

## Risk Management

### Natural Stop Loss
- Entry at Fibonacci level (e.g., 46180)
- Natural stop: Below swing low (40000)
- Risk: 46180 - 40000 = 6180 (13.4%)
- Can use tighter stop (e.g., 2-3%) for better R:R

### Natural Take Profit
- Target: Swing high (50000)
- Reward: 50000 - 46180 = 3820 (8.3%)
- Risk/Reward: 3820 / 6180 = 0.62 (not ideal)
- **With tighter stop (2%)**: R:R = 8.3% / 2% = 4.15 (excellent!)

## Future Enhancements
- Add Fibonacci extensions (1.272, 1.618) for targets beyond swing high
- Support multiple Fibonacci levels (0.382, 0.5, 0.618, 0.786)
- Add harmonic pattern detection (Gartley, Butterfly)
- Support Fibonacci time zones
- Add volume confirmation at Fibonacci levels
- Implement dynamic tolerance based on volatility (ATR)
