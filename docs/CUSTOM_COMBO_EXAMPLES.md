# Custom Combo Creation Examples

This guide provides step-by-step examples for creating custom combo strategies.

---

## Example 1: Simple EMA Crossover

### Goal
Create a basic trend-following strategy using two EMAs.

### Step 1: Define Indicators

```json
{
  "indicators": [
    {
      "type": "ema",
      "alias": "fast",
      "params": {"length": 12}
    },
    {
      "type": "ema",
      "alias": "slow",
      "params": {"length": 26}
    }
  ]
}
```

### Step 2: Define Entry Logic

Buy when fast EMA crosses above slow EMA:

```python
crossover(fast, slow)
```

### Step 3: Define Exit Logic

Sell when fast EMA crosses below slow EMA:

```python
crossunder(fast, slow)
```

### Complete Template

```json
{
  "name": "simple_ema_cross",
  "description": "Basic EMA crossover strategy",
  "indicators": [
    {
      "type": "ema",
      "alias": "fast",
      "params": {"length": 12}
    },
    {
      "type": "ema",
      "alias": "slow",
      "params": {"length": 26}
    }
  ],
  "entry_logic": "crossover(fast, slow)",
  "exit_logic": "crossunder(fast, slow)",
  "stop_loss": 0.02
}
```

### Usage

```bash
curl -X POST http://localhost:8000/api/combos/templates \
  -H "Content-Type: application/json" \
  -d @simple_ema_cross.json
```

---

## Example 2: RSI Mean Reversion

### Goal
Create a mean reversion strategy using RSI and Bollinger Bands.

### Strategy Logic
- **Buy**: When RSI is oversold (<30) AND price touches lower Bollinger Band
- **Sell**: When RSI returns to neutral (>50) OR price reaches middle Bollinger Band

### Complete Template

```json
{
  "name": "rsi_mean_reversion",
  "description": "RSI oversold + Bollinger Bands mean reversion",
  "indicators": [
    {
      "type": "rsi",
      "params": {"length": 14}
    },
    {
      "type": "bbands",
      "alias": "bb",
      "params": {
        "length": 20,
        "std": 2
      }
    }
  ],
  "entry_logic": "(RSI_14 < 30) & (close < bb_lower)",
  "exit_logic": "(RSI_14 > 50) | (close > bb_middle)",
  "stop_loss": 0.025
}
```

### Backtest

```python
import requests

backtest_request = {
    "template_name": "rsi_mean_reversion",
    "symbol": "ETH/USDT",
    "timeframe": "1h",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}

response = requests.post(
    'http://localhost:8000/api/combos/backtest',
    json=backtest_request
)

results = response.json()
print(f"Win Rate: {results['metrics']['win_rate']:.2%}")
print(f"Total Return: {results['metrics']['total_return']:.2%}")
```

---

## Example 3: Multi-Timeframe Trend

### Goal
Create a strategy that confirms trend across multiple indicators.

### Strategy Logic
- **Buy**: Price above 50 EMA, MACD bullish, AND volume above average
- **Sell**: MACD bearish OR price below 50 EMA

### Complete Template

```json
{
  "name": "multi_confirm_trend",
  "description": "Multi-indicator trend confirmation",
  "indicators": [
    {
      "type": "ema",
      "alias": "trend",
      "params": {"length": 50}
    },
    {
      "type": "macd",
      "params": {
        "fast": 12,
        "slow": 26,
        "signal": 9
      }
    },
    {
      "type": "volume_sma",
      "alias": "vol_avg",
      "params": {"length": 20}
    }
  ],
  "entry_logic": "(close > trend) & (MACD_macd > MACD_signal) & (volume > vol_avg)",
  "exit_logic": "(MACD_macd < MACD_signal) | (close < trend)",
  "stop_loss": 0.02
}
```

### Optimization

```python
optimize_request = {
    "template_name": "multi_confirm_trend",
    "symbol": "BTC/USDT",
    "timeframe": "4h",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "custom_ranges": {
        "ema_length": {"min": 30, "max": 70, "step": 5},
        "macd_fast": {"min": 8, "max": 16, "step": 2},
        "macd_slow": {"min": 20, "max": 30, "step": 2}
    }
}

response = requests.post(
    'http://localhost:8000/api/combos/optimize',
    json=optimize_request
)

best_params = response.json()['best_parameters']
print("Optimal Parameters:", best_params)
```

---

## Example 4: Breakout with Volume Confirmation

### Goal
Catch breakouts with volume confirmation and ATR-based exits.

### Strategy Logic
- **Buy**: Price breaks above 20-day high AND volume > 2x average
- **Sell**: Price drops by 1 ATR from entry

### Complete Template

```json
{
  "name": "volume_breakout",
  "description": "High volume breakout strategy",
  "indicators": [
    {
      "type": "sma",
      "alias": "high_20",
      "params": {"length": 20}
    },
    {
      "type": "volume_sma",
      "alias": "vol_avg",
      "params": {"length": 20}
    },
    {
      "type": "atr",
      "params": {"length": 14}
    }
  ],
  "entry_logic": "(close > high_20) & (volume > vol_avg * 2)",
  "exit_logic": "close < (entry_price - ATR_14)",
  "stop_loss": 0.03
}
```

**Note**: `entry_price` is automatically tracked by the system.

---

## Example 5: ADX Trend Strength Filter

### Goal
Only trade when a strong trend exists (ADX > 25).

### Strategy Logic
- **Buy**: EMA crossover AND ADX > 25 (strong trend)
- **Sell**: EMA crossunder OR ADX < 20 (weak trend)

### Complete Template

```json
{
  "name": "adx_trend_filter",
  "description": "EMA crossover with ADX trend filter",
  "indicators": [
    {
      "type": "ema",
      "alias": "fast",
      "params": {"length": 12}
    },
    {
      "type": "ema",
      "alias": "slow",
      "params": {"length": 26}
    },
    {
      "type": "adx",
      "params": {"length": 14}
    }
  ],
  "entry_logic": "crossover(fast, slow) & (ADX_14 > 25)",
  "exit_logic": "crossunder(fast, slow) | (ADX_14 < 20)",
  "stop_loss": 0.02
}
```

### Why ADX?
- ADX > 25: Strong trend (good for trend-following)
- ADX < 20: Weak/no trend (avoid trading)
- Reduces whipsaws in ranging markets

---

## Example 6: Fibonacci Retracement Entry

### Goal
Buy at Fibonacci retracement levels in an uptrend.

### Strategy Logic
- **Buy**: Price in uptrend (above 200 EMA) AND near 0.618 Fib level
- **Sell**: Price breaks below 200 EMA

### Complete Template

```json
{
  "name": "fib_retracement",
  "description": "Fibonacci retracement entries in uptrend",
  "indicators": [
    {
      "type": "ema",
      "alias": "trend",
      "params": {"length": 200}
    },
    {
      "type": "rsi",
      "params": {"length": 14}
    }
  ],
  "entry_logic": "(close > trend) & (RSI_14 > 40) & (RSI_14 < 60)",
  "exit_logic": "(close < trend) | (RSI_14 > 70)",
  "stop_loss": 0.025
}
```

**Note**: Full Fibonacci calculation requires custom implementation. This example uses RSI as a proxy for pullback detection.

---

## Tips for Custom Combos

### 1. Start Simple
Begin with 2-3 indicators. Add complexity only if needed.

### 2. Test Logic Separately
Test entry and exit logic independently before combining.

### 3. Use Aliases
Make logic readable with meaningful aliases:
```json
{"type": "ema", "alias": "trend", "params": {"length": 50}}
```
Then use: `close > trend` instead of `close > EMA_50`

### 4. Validate Syntax
Ensure logic uses bitwise operators (`&`, `|`) not boolean (`and`, `or`).

### 5. Backtest Thoroughly
- Test on multiple symbols
- Test different timeframes
- Test different market conditions

### 6. Optimize Wisely
- Don't over-optimize (curve fitting)
- Use reasonable parameter ranges
- Validate on out-of-sample data

---

## Common Patterns

### Trend Following
```python
entry: crossover(fast_ma, slow_ma) & (volume > avg_volume)
exit: crossunder(fast_ma, slow_ma)
```

### Mean Reversion
```python
entry: (RSI < 30) & (close < bb_lower)
exit: (RSI > 50) | (close > bb_middle)
```

### Breakout
```python
entry: (close > resistance) & (volume > avg_volume * 1.5)
exit: close < (entry_price - ATR)
```

### Momentum
```python
entry: (RSI > 50) & (MACD_macd > MACD_signal) & (close > EMA_20)
exit: (RSI < 50) | (MACD_macd < MACD_signal)
```

---

## Debugging Tips

### No Signals Generated
1. Check if logic is too restrictive
2. Verify indicator parameters are reasonable
3. Ensure sufficient data for indicators

### Too Many Signals
1. Add additional filters (volume, ADX, etc.)
2. Tighten entry conditions
3. Increase indicator periods

### Logic Errors
1. Use parentheses for complex conditions
2. Check operator precedence
3. Validate indicator column names

### Performance Issues
1. Reduce parameter optimization ranges
2. Use fixed timeframe
3. Limit date range for testing

---

## Next Steps

1. **Create your first custom combo** using Example 1
2. **Backtest it** on your preferred symbol
3. **Optimize parameters** to improve performance
4. **Iterate and refine** based on results

For more information:
- [User Guide](./COMBO_STRATEGIES_USER_GUIDE.md)
- [Templates Reference](./COMBO_TEMPLATES_REFERENCE.md)
- [API Documentation](./COMBO_API_DOCUMENTATION.md)
