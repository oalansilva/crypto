# Design: EMA 50/200 + RSI + Volume Strategy

## Overview
This design document outlines the implementation approach for the EMA 50/200 + RSI + Volume trading strategy, which is the most popular strategy for Bitcoin trading.

## Strategy Logic

### Core Concept
The strategy combines three key elements:
1. **Trend Filter (EMA 200)**: Only trade in the direction of the long-term trend
2. **Entry Timing (EMA 50)**: Enter on pullbacks to the fast moving average
3. **Momentum Confirmation (RSI)**: Ensure the pullback is healthy (not oversold)

### Buy Signal Logic
```
BUY when ALL conditions are true:
1. close > EMA_200           # Bullish trend filter
2. close > EMA_50            # Price recovering from pullback
3. close[1] <= EMA_50[1]     # Was below EMA 50 (pullback)
4. RSI >= rsi_min AND RSI <= rsi_max  # Healthy pullback zone (40-50)
```

### Sell Signal Logic
```
SELL when ANY condition is true:
1. close < EMA_50            # Price breaks below fast MA
2. RSI < rsi_min             # Momentum loss (default: RSI < 40)
```

## Implementation Architecture

### 1. Strategy Class (`EmaRsiVolumeStrategy`)

**File**: `backend/app/strategies/ema_rsi_volume.py`

**Responsibilities**:
- Calculate EMA 50 and EMA 200 using `pandas_ta.ema()`
- Calculate RSI using `pandas_ta.rsi()`
- Generate buy/sell signals based on logic above
- Store simulation data for visualization

**Parameters**:
- `ema_fast` (int, default=50): Fast EMA period
- `ema_slow` (int, default=200): Slow EMA period (trend filter)
- `rsi_period` (int, default=14): RSI calculation period
- `rsi_min` (int, default=40): Minimum RSI for buy signal
- `rsi_max` (int, default=50): Maximum RSI for buy signal

**Key Methods**:
- `__init__(config: dict)`: Initialize with parameters
- `generate_signals(df: pd.DataFrame) -> pd.Series`: Generate signals

### 2. Strategy Registration

**File**: `backend/app/services/backtest_service.py`

**Changes**:
- Import `EmaRsiVolumeStrategy` class
- Add conditional check in `_get_strategy()` method:
  ```python
  if strategy_name_lower == 'emarsivolume':
      strategy_config = {"name": name_or_config}
      if params:
          strategy_config.update(params)
      return EmaRsiVolumeStrategy(strategy_config)
  ```

### 3. Schema Definition

**File**: `backend/app/schemas/indicator_params.py`

**Changes**:
- Define `EMA_RSI_VOLUME_SCHEMA` with parameter definitions
- Add optimization ranges for Grid Search
- Register in `INDICATOR_SCHEMAS` dict

**Schema Structure**:
```python
EMA_RSI_VOLUME_SCHEMA = IndicatorSchema(
    name="EMA_RSI_VOLUME",
    display_name="EMA 50/200 + RSI + Volume",
    category="Trend Following",
    parameters=[
        ParameterDef(name="ema_fast", type="int", default=50, min=20, max=100, step=10),
        ParameterDef(name="ema_slow", type="int", default=200, min=100, max=300, step=50),
        ParameterDef(name="rsi_period", type="int", default=14, min=10, max=20, step=2),
        ParameterDef(name="rsi_min", type="int", default=40, min=30, max=45, step=5),
        ParameterDef(name="rsi_max", type="int", default=50, min=45, max=60, step=5),
    ]
)
```

### 4. Dynamic Schema Generator

**File**: `backend/app/schemas/dynamic_schema_generator.py`

**Changes**:
- Add conditional check for 'emarsivolume' strategy
- Return appropriate schema with parameter definitions

### 5. API Metadata

**File**: `backend/app/api.py`

**Changes**:
- Add strategy metadata to `/api/strategies` endpoint:
  ```python
  {
      "id": "emarsivolume",
      "name": "EMA 50/200 + RSI + Volume",
      "description": "Most popular BTC strategy: Trend following with EMA 200 filter, EMA 50 entries, and RSI confirmation",
      "category": "Trend Following",
      "indicators": ["EMA", "RSI"],
      "timeframes": ["4h", "1d"],
      "difficulty": "Intermediate"
  }
  ```

## Visualization

### Indicator Metadata
The strategy will return indicator metadata for visualization:

```python
indicators = [
    {
        "name": "EMA_50",
        "color": "#fb923c",  # Orange
        "panel": "main",
        "data": [{"time": "...", "value": ...}, ...]
    },
    {
        "name": "EMA_200",
        "color": "#3b82f6",  # Blue
        "panel": "main",
        "data": [{"time": "...", "value": ...}, ...]
    },
    {
        "name": "RSI_14",
        "color": "#8b5cf6",  # Purple
        "panel": "lower",
        "data": [{"time": "...", "value": ...}, ...]
    }
]
```

### Chart Layout
- **Main Panel**: Candlesticks + EMA 50 (orange) + EMA 200 (blue)
- **Lower Panel**: RSI (purple) with reference lines at 40 and 50

## Optimization Support

### Parameter Ranges
The strategy supports Grid Search optimization with these suggested ranges:
- `ema_fast`: 20-100 (step 10) → 9 values
- `ema_slow`: 100-300 (step 50) → 5 values
- `rsi_period`: 10-20 (step 2) → 6 values
- `rsi_min`: 30-45 (step 5) → 4 values
- `rsi_max`: 45-60 (step 5) → 4 values

**Total combinations**: 9 × 5 × 6 × 4 × 4 = 4,320 combinations

### Optimization Workflow
1. User selects "EMA 50/200 + RSI + Volume" strategy
2. Frontend fetches parameter schema from backend
3. User configures optimization ranges (or uses defaults)
4. Backend runs Grid Search across all combinations
5. Results sorted by performance metrics (Sharpe, Total Return, etc.)

## Testing Strategy

### Unit Tests
- Test signal generation with known data
- Verify trend filter blocks trades in downtrend
- Verify pullback detection works correctly
- Test RSI range filtering

### Integration Tests
- Run backtest on BTC/USDT 4h data (2 years)
- Verify compatibility with Stop Loss/Take Profit
- Test parameter optimization
- Verify chart visualization

### Performance Tests
- Ensure strategy runs efficiently on large datasets (>10k candles)
- Verify optimization completes in reasonable time

## Trade-offs and Decisions

### Why EMA instead of SMA for fast MA?
- EMA reacts faster to price changes
- More suitable for capturing pullback entries
- EMA 200 is industry standard for long-term trend

### Why RSI 40-50 instead of traditional 30-70?
- Traditional oversold (30) often signals weakness, not strength
- RSI 40-50 indicates a healthy pullback in an uptrend
- Reduces false signals and whipsaws

### Why not include Volume filter in v1?
- Volume analysis adds complexity (need to define "high volume")
- Can be added in future iteration
- Current logic is already proven effective

## Future Enhancements
- Add volume confirmation (e.g., volume > SMA(volume, 20))
- Add ADX filter to avoid ranging markets
- Support for multiple timeframe analysis
- Add trailing stop loss option
