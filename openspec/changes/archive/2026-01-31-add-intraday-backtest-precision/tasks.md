## 1. Data Layer
- [x] 1.1 Update `IncrementalLoader` to support 15m timeframe fetching
- [x] 1.2 Add `fetch_intraday_data(symbol, timeframe='15m', since, until)` method
- [x] 1.3 Store 15m data in separate Parquet files (e.g., `BTC_USDT_15m.parquet`)
- [x] 1.4 Implement cache validation for 15m data
- [x] 1.5 Add data availability check (15m data may have limited history vs 1d)

## 2. Backtest Engine (Deep Backtesting Logic)
- [x] 2.1 Add `deep_backtest` boolean parameter to backtest configuration
- [x] 2.2 Implement `simulate_execution_with_15m()` function in `deep_backtest.py`
- [x] 2.3 For each trade day (1D signal), fetch corresponding 15m candles (96 candles per day)
- [x] 2.4 Iterate through 15m candles chronologically:
  - [x] 2.4.1 Check if Low <= Stop Price → Exit immediately at stop
  - [x] 2.4.2 Check if High >= Target Price → Exit at target
  - [x] 2.4.3 Check for exit signal → Exit at Open of next 15m candle
- [x] 2.5 Update trade exit time/price based on first event
- [x] 2.6 Handle edge case: Entry happens mid-day (use remaining 15m candles only)

## 3. API & Schema
- [x] 3.1 Add `deep_backtest` boolean field to `ComboBacktestRequest` schema (default: false)
- [x] 3.2 Update `/api/backtest` endpoint to accept deep backtest mode
- [x] 3.3 Add `/api/data/15m-availability` endpoint to check 15m data coverage
- [x] 3.4 Return metadata in backtest results: `{ "execution_mode": "deep_15m" | "fast_1d" }`

## 4. Frontend
- [x] 4.1 Add "Deep Backtest (15m Precision)" toggle to Combo Config page
- [x] 4.2 Show warning when using tight stops (< 2%) with fast mode: "⚠️ Tight stops may produce unrealistic results without Deep Backtesting"
- [x] 4.3 Display "Execution: Deep (15m)" badge in results when deep mode was used
- [x] 4.4 Add tooltip explaining: "Deep Backtesting simulates execution using 15-minute candles for realistic stop/target validation"

## 5. Testing & Validation
- [x] 5.1 Create test comparing fast vs deep mode for tight stop strategy (1.5%)
- [x] 5.2 Validate against TradingView results for known parameter set (should match within 5%)
- [x] 5.3 Performance test: measure speed impact of deep mode (expect ~50-100x slower due to 96 candles/day)
- [x] 5.4 Document expected slowdown and recommend deep mode only for final validation
- [x] 5.5 Verify that "Old" parameters (3/32/37, Stop 2.7%) now match TradingView exactly
