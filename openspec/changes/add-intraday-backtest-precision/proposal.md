# Change: Add Deep Backtesting with 15m Intraday Precision

## Why
The current backtesting engine uses daily (1d) OHLC data, which creates **"temporal ambiguity"** for tight stop losses (< 2%). When a candle's Low touches the stop price and High exceeds the target, we cannot determine which event occurred first without intraday data.

**The Problem:**
- Strategy generates signals on **1D** (daily candles)
- Execution is simulated using only **OHLC** of that day
- System doesn't know the **real sequence** of events (did price rally first, or drop first?)
- Creates **phantom profits**, especially with tight stops
- Distorts metrics (Sharpe, Drawdown, CAGR)

**The Solution: Deep Backtesting**
TradingView's "Deep Backtesting" uses **15-minute candles** to reconstruct the actual price path within each day. This eliminates guesswork and produces results that match live trading.

Our system needs equivalent precision: **1D signals + 15m execution simulation**.

## What Changes
- Add capability to fetch and store **15m intraday data** alongside daily data
- Implement **"Deep Backtest" mode**:
  - Generate signals on 1D candles (strategy logic unchanged)
  - Simulate execution using 15m candles (reconstruct real price path)
  - Check stop/target/reversal candle-by-candle in chronological order
- Add UI toggle: **"Fast Backtest"** (daily only, current behavior) vs **"Deep Backtest"** (15m precision)
- **BREAKING**: Optimization results will change significantly for strategies with stops < 2% (results will be lower but realistic)

**Why 15m?**
- Resolves 95% of temporal ambiguity
- Much more realistic than 1h
- Much lighter than 1m or 5m
- Optimal balance between precision and performance

## Impact
- Affected specs: `data-caching`, `backend`, `backtest-config`, `performance-metrics`
- Affected code: 
  - `backend/src/data/incremental_loader.py` (15m data fetching)
  - `backend/app/services/combo_optimizer.py` (intraday execution simulation)
  - `backend/app/schemas/backtest_params.py` (deep backtest mode parameter)
  - `frontend/src/pages/ComboConfigPage.tsx` (UI toggle)
