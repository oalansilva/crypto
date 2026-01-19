# Combo Strategies - User Guide

## Overview

Combo Strategies allow you to combine multiple technical indicators into a single trading strategy with custom entry and exit logic. This powerful feature enables you to create sophisticated trading systems without writing code.

**Architecture**: All combo strategies are stored in the database as JSON configurations. This means:
- ✅ No code deployment needed for new strategies
- ✅ Easy customization and sharing
- ✅ Version control via database backups
- ✅ Runtime configuration without server restarts

## Quick Start

### 1. Select a Template

Navigate to **Combo Strategies** from the homepage and choose from:

- **Pre-built Templates**: 6 professionally designed strategies (stored in database)
- **Example Templates**: 4 sample strategies for learning
- **Custom Templates**: Your saved custom strategies

### 2. Configure & Backtest

1. Select your template
2. Choose symbol (e.g., BTC/USDT)
3. Select timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
4. Set date range
5. Click **Run Backtest**

### 3. Analyze Results

View comprehensive results including:
- **Performance Metrics**: Sharpe Ratio, Total Return, Win Rate
- **Trade History**: All entries and exits with profit/loss
- **Interactive Chart**: Candlesticks with trade markers and indicators
- **Indicator Values**: Full time series data for analysis

### 4. Optimize Parameters

1. Click **Optimize** from the results page
2. Configure parameter ranges (Min, Max, Step)
3. Run optimization to find best parameters
4. Apply optimized parameters to your strategy

## Complete Workflow Example

### Using EMA + RSI Strategy

**Step 1: Select Template**
```
Template: EMA + RSI
Description: Trend following with momentum confirmation
Indicators: EMA Fast (9), EMA Slow (21), RSI (14)
```

**Step 2: Configure Backtest**
```
Symbol: BTC/USDT
Timeframe: 1h
Start Date: 2024-01-01
End Date: 2024-12-31
```

**Step 3: Review Results**
```
Total Return: +15.3%
Sharpe Ratio: 1.45
Win Rate: 58.2%
Total Trades: 47
```

**Step 4: Optimize (Optional)**
```
ema_fast: 5-15 (step 1)
ema_slow: 15-30 (step 1)
rsi_period: 10-20 (step 2)

Optimized Result:
ema_fast: 7
ema_slow: 23
rsi_period: 12
Sharpe Ratio: 1.68 ✨
```

## Understanding Entry/Exit Logic

### Logic Syntax

Combo strategies use Python-like expressions with bitwise operators:

- `&` - AND (both conditions must be true)
- `|` - OR (at least one condition must be true)
- `>`, `<`, `>=`, `<=` - Comparison operators
- `()` - Grouping for complex logic

### Example Logic

**Entry Logic:**
```python
(close > fast) & (close > slow) & (RSI_14 > 30) & (RSI_14 < 50)
```
Translation: "Buy when price is above both EMAs AND RSI is between 30-50"

**Exit Logic:**
```python
(RSI_14 > 70) | (close < fast)
```
Translation: "Sell when RSI is overbought OR price drops below fast EMA"

### Helper Functions

Available helper functions for advanced logic:

- `crossover(series1, series2)` - Detects when series1 crosses above series2
- `crossunder(series1, series2)` - Detects when series1 crosses below series2
- `above(series1, series2, periods=N)` - True if series1 > series2 for N periods
- `below(series1, series2, periods=N)` - True if series1 < series2 for N periods

**Example with Helpers:**
```python
crossover(close, EMA_50) & (RSI_14 < 30)
```

## Creating Custom Combos

### Method 1: Using the UI (Coming Soon)

The visual combo builder will allow drag-and-drop strategy creation.

### Method 2: Using the API

**POST /api/combos/templates**

```json
{
  "name": "my_custom_strategy",
  "description": "Custom EMA + MACD strategy",
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
    }
  ],
  "entry_logic": "(close > trend) & (MACD_macd > MACD_signal)",
  "exit_logic": "(MACD_macd < MACD_signal) | (close < trend)",
  "stop_loss": 0.02
}
```

### Supported Indicators

| Indicator | Type | Parameters | Columns Generated |
|-----------|------|------------|-------------------|
| EMA | `ema` | `length` | `EMA_{length}` or alias |
| SMA | `sma` | `length` | `SMA_{length}` or alias |
| RSI | `rsi` | `length` | `RSI_{length}` |
| MACD | `macd` | `fast`, `slow`, `signal` | `MACD_macd`, `MACD_signal`, `MACD_histogram` |
| Bollinger Bands | `bbands` | `length`, `std` | `BB_upper`, `BB_middle`, `BB_lower` |
| ATR | `atr` | `length` | `ATR_{length}` |
| ADX | `adx` | `length` | `ADX_{length}` |
| Volume SMA | `volume_sma` | `length` | `VOL_SMA_{length}` |

### Using Aliases

Aliases make your logic more readable:

```json
{
  "indicators": [
    {
      "type": "ema",
      "alias": "fast",
      "params": {"length": 9}
    },
    {
      "type": "ema",
      "alias": "slow",
      "params": {"length": 21}
    }
  ],
  "entry_logic": "crossover(fast, slow)",
  "exit_logic": "crossunder(fast, slow)"
}
```

## Best Practices

### 1. Start Simple
Begin with 2-3 indicators. Complex strategies aren't always better.

### 2. Use Appropriate Timeframes
- **Scalping**: 1m, 5m
- **Day Trading**: 15m, 30m, 1h
- **Swing Trading**: 4h, 1d

### 3. Backtest Thoroughly
- Test on at least 6-12 months of data
- Use different market conditions (bull, bear, sideways)
- Verify results on multiple symbols

### 4. Optimize Carefully
- Don't over-optimize (curve fitting)
- Use reasonable parameter ranges
- Validate on out-of-sample data

### 5. Consider Risk Management
- Always use stop-loss
- Consider position sizing
- Monitor drawdowns

## Troubleshooting

### "No signals generated"
- Check if your logic is too restrictive
- Verify indicator parameters are reasonable
- Ensure sufficient data for indicators to calculate

### "Too many signals"
- Logic may be too permissive
- Add additional filters
- Increase indicator periods

### "Optimization takes too long"
- Reduce parameter ranges
- Increase step sizes
- Use fixed timeframe instead of optimizing it

### "Chart not displaying"
- Ensure backtest completed successfully
- Check browser console for errors
- Verify candle data is present in response

## Next Steps

1. **Explore Pre-built Templates**: Try each template to understand different approaches
2. **Experiment with Parameters**: Modify parameters to see their impact
3. **Create Custom Combos**: Build strategies tailored to your trading style
4. **Optimize**: Find the best parameters for your chosen symbols
5. **Paper Trade**: Test strategies in real-time before live trading

## Support

For issues or questions:
- Check API documentation at `/docs`
- Review database schema in `backend/app/migrations/`
- Consult the technical documentation
- All strategies are stored in `combo_templates` database table

---

**Remember**: Past performance does not guarantee future results. Always practice proper risk management.
