# Combo Templates Reference

Complete documentation for all pre-built combo strategy templates.

---

## 1. Multi-MA Crossover (CRUZAMENTO MEDIAS)

### Overview
Classic moving average crossover strategy using three timeframes for trend confirmation.

### Indicators
- **SMA Short** (9 periods) - Fast trend
- **SMA Medium** (21 periods) - Medium trend  
- **SMA Long** (50 periods) - Long trend

### Logic

**Entry:**
```python
crossover(short, medium) & (short > long)
```
Buy when fast MA crosses above medium MA AND both are above long MA (strong uptrend).

**Exit:**
```python
crossunder(short, medium) | (short < long)
```
Sell when fast MA crosses below medium MA OR drops below long MA.

### Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `sma_short` | 9 | 5-15 | Fast moving average period |
| `sma_medium` | 21 | 15-30 | Medium moving average period |
| `sma_long` | 50 | 30-100 | Long moving average period |
| `stop_loss` | 1.5% | 0.5-3% | Stop loss percentage |

### Best For
- Trending markets
- Medium to long-term trading
- Clear trend identification

### Optimization Tips
- Shorter periods for volatile markets
- Longer periods for stable markets
- Test on 1h-4h timeframes

---

## 2. EMA + RSI

### Overview
Trend following strategy with momentum confirmation using EMAs and RSI.

### Indicators
- **EMA Fast** (9 periods) - Short-term trend
- **EMA Slow** (21 periods) - Long-term trend
- **RSI** (14 periods) - Momentum oscillator

### Logic

**Entry:**
```python
(close > fast) & (close > slow) & (RSI_14 > 30) & (RSI_14 < 50)
```
Buy when price is above both EMAs AND RSI shows healthy momentum (not oversold, not overbought).

**Exit:**
```python
(RSI_14 > 70) | (close < fast)
```
Sell when RSI is overbought OR price drops below fast EMA.

### Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `ema_fast` | 9 | 5-20 | Fast EMA period |
| `ema_slow` | 21 | 15-50 | Slow EMA period |
| `rsi_period` | 14 | 7-21 | RSI calculation period |
| `rsi_min` | 30 | 20-40 | Minimum RSI for entry |
| `rsi_max` | 50 | 40-60 | Maximum RSI for entry |
| `stop_loss` | 1.5% | 0.5-3% | Stop loss percentage |

### Best For
- Trending markets with pullbacks
- Avoiding overbought entries
- 1h-4h timeframes

### Optimization Tips
- Tighten RSI range for fewer, higher quality signals
- Widen RSI range for more signals
- Adjust EMA periods based on volatility

---

## 3. EMA + MACD + Volume

### Overview
Comprehensive trend strategy combining price action, momentum, and volume confirmation.

### Indicators
- **EMA** (20 periods) - Trend direction
- **MACD** (12, 26, 9) - Momentum and trend strength
- **Volume SMA** (20 periods) - Volume confirmation

### Logic

**Entry:**
```python
(close > EMA_20) & (MACD_macd > MACD_signal) & (volume > vol_avg)
```
Buy when price is above EMA, MACD is bullish, AND volume is above average (strong conviction).

**Exit:**
```python
(MACD_macd < MACD_signal) | (close < EMA_20)
```
Sell when MACD turns bearish OR price drops below EMA.

### Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `ema_length` | 20 | 10-50 | EMA period |
| `macd_fast` | 12 | 8-15 | MACD fast period |
| `macd_slow` | 26 | 20-30 | MACD slow period |
| `macd_signal` | 9 | 5-12 | MACD signal period |
| `volume_length` | 20 | 10-30 | Volume SMA period |
| `stop_loss` | 2% | 1-3% | Stop loss percentage |

### Best For
- High-volume assets
- Confirming breakouts
- Avoiding false signals
- 30m-4h timeframes

### Optimization Tips
- Volume filter reduces false signals significantly
- Adjust MACD for different market speeds
- Consider disabling volume filter in low-volume markets

---

## 4. Bollinger Bands + RSI + ADX

### Overview
Mean reversion strategy with trend strength filter using Bollinger Bands, RSI, and ADX.

### Indicators
- **Bollinger Bands** (20, 2) - Volatility and price extremes
- **RSI** (14 periods) - Oversold/overbought conditions
- **ADX** (14 periods) - Trend strength

### Logic

**Entry:**
```python
(close < BB_lower) & (RSI_14 < 30) & (ADX_14 > 20)
```
Buy when price touches lower Bollinger Band, RSI is oversold, AND ADX confirms a trend exists.

**Exit:**
```python
(close > BB_middle) | (RSI_14 > 70)
```
Sell when price returns to middle band OR RSI becomes overbought.

### Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `bb_length` | 20 | 15-30 | Bollinger Bands period |
| `bb_std` | 2.0 | 1.5-2.5 | Standard deviations |
| `rsi_length` | 14 | 10-20 | RSI period |
| `adx_length` | 14 | 10-20 | ADX period |
| `adx_threshold` | 20 | 15-30 | Minimum ADX for entry |
| `stop_loss` | 2% | 1-3% | Stop loss percentage |

### Best For
- Range-bound markets
- Mean reversion trading
- Markets with clear support/resistance
- 1h-1d timeframes

### Optimization Tips
- Higher ADX threshold for stronger trends only
- Adjust BB std for volatility
- RSI thresholds can be tightened for quality

---

## 5. Volume + ATR Breakout

### Overview
Breakout strategy using volume spikes and ATR for volatility-adjusted entries.

### Indicators
- **Volume SMA** (20 periods) - Average volume
- **ATR** (14 periods) - Volatility measure

### Logic

**Entry:**
```python
(volume > vol_avg * 1.5) & (close > close.shift(1) + ATR_14 * 0.5)
```
Buy when volume is 1.5x average AND price breaks out by 0.5 ATR.

**Exit:**
```python
close < close.shift(1) - ATR_14 * 0.3
```
Sell when price drops by 0.3 ATR from previous close.

### Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `volume_length` | 20 | 10-30 | Volume SMA period |
| `volume_multiplier` | 1.5 | 1.2-2.0 | Volume spike threshold |
| `atr_length` | 14 | 10-20 | ATR period |
| `atr_entry_mult` | 0.5 | 0.3-1.0 | Entry ATR multiplier |
| `atr_exit_mult` | 0.3 | 0.2-0.5 | Exit ATR multiplier |
| `stop_loss` | 2.5% | 1.5-4% | Stop loss percentage |

### Best For
- Breakout trading
- High-volatility markets
- News-driven moves
- 15m-1h timeframes

### Optimization Tips
- Increase volume multiplier to reduce false breakouts
- Adjust ATR multipliers for market volatility
- Works best on liquid assets

---

## 6. EMA + RSI + Fibonacci

### Overview
Advanced strategy combining trend, momentum, and Fibonacci retracement levels.

### Indicators
- **EMA** (200 periods) - Long-term trend
- **RSI** (14 periods) - Momentum
- **Fibonacci Levels** - Retracement zones (0.5, 0.618)

### Logic

**Entry:**
```python
(close > EMA_200) & (RSI_14 > 40) & (RSI_14 < 60) & 
(close near fibonacci 0.5 or 0.618 retracement)
```
Buy when price is in uptrend, RSI is neutral, AND price is near key Fibonacci level.

**Exit:**
```python
(RSI_14 > 70) | (close < EMA_200)
```
Sell when RSI is overbought OR trend reverses.

### Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `ema_length` | 200 | 100-300 | Long-term EMA |
| `rsi_length` | 14 | 10-20 | RSI period |
| `fib_lookback` | 50 | 30-100 | Swing high/low lookback |
| `fib_tolerance` | 0.02 | 0.01-0.05 | Fib level tolerance |
| `stop_loss` | 2% | 1-3% | Stop loss percentage |

### Best For
- Swing trading
- Trending markets with pullbacks
- Higher timeframes (4h-1d)
- Technical analysis enthusiasts

### Optimization Tips
- Longer EMA for stronger trend filter
- Adjust fib_tolerance for entry precision
- Works best on major cryptocurrencies

---

## Comparison Matrix

| Template | Complexity | Best Timeframe | Market Type | Signals/Month* |
|----------|------------|----------------|-------------|----------------|
| Multi-MA Crossover | ⭐ Low | 1h-4h | Trending | 5-10 |
| EMA + RSI | ⭐⭐ Medium | 1h-4h | Trending | 10-20 |
| EMA + MACD + Volume | ⭐⭐⭐ High | 30m-4h | Trending | 8-15 |
| Bollinger + RSI + ADX | ⭐⭐⭐ High | 1h-1d | Range-bound | 12-25 |
| Volume + ATR Breakout | ⭐⭐ Medium | 15m-1h | Volatile | 15-30 |
| EMA + RSI + Fibonacci | ⭐⭐⭐⭐ Very High | 4h-1d | Trending | 5-12 |

*Approximate, varies by market conditions

---

## Usage Recommendations

### For Beginners
Start with **Multi-MA Crossover** or **EMA + RSI** - simple logic, easy to understand.

### For Experienced Traders
Try **EMA + MACD + Volume** or **Bollinger + RSI + ADX** - more sophisticated filtering.

### For Scalpers
Use **Volume + ATR Breakout** on 5m-15m timeframes.

### For Swing Traders
Use **EMA + RSI + Fibonacci** on 4h-1d timeframes.

---

## Next Steps

1. **Test each template** on your preferred symbols
2. **Compare performance** across different market conditions
3. **Optimize parameters** for your specific use case
4. **Combine insights** to create custom strategies

For custom combo creation, see [User Guide](./COMBO_STRATEGIES_USER_GUIDE.md).
