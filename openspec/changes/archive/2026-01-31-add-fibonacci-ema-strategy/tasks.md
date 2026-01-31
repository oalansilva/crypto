## 1. Backend Implementation
- [x] 1.1 Create `FibonacciEmaStrategy` class in `backend/app/strategies/fibonacci_ema.py`
  - [x] Implement `__init__` to accept configurable parameters (ema_period, swing_lookback, fib_level_1, fib_level_2, level_tolerance)
  - [x] Implement swing high/low detection algorithm
  - [x] Implement Fibonacci retracement calculation
  - [x] Calculate EMA 200 using pandas_ta
  - [x] Implement buy condition: (price > EMA 200) AND (price at Fib 0.5 or 0.618) AND (bounce confirmation)
  - [x] Implement sell condition: (price < EMA 200) OR (price at swing high)
  - [x] Store simulation_data with Fibonacci levels for visualization
- [x] 1.2 Register strategy in `backend/app/services/backtest_service.py`
  - [x] Import `FibonacciEmaStrategy` class
  - [x] Add conditional check in `_get_strategy` method for 'fibonacciema' strategy name
  - [x] Handle both dict config and string name formats
  - [x] Support parameter merging for optimization mode
- [x] 1.3 Add schema definition in `backend/app/schemas/indicator_params.py`
  - [x] Define `FIBONACCI_EMA_SCHEMA` with parameters
  - [x] Add optimization ranges for each parameter
  - [x] Register schema in `INDICATOR_SCHEMAS` dict
- [x] 1.4 Update dynamic schema generator in `backend/app/schemas/dynamic_schema_generator.py`
  - [x] Add conditional check for 'fibonacciema' strategy
  - [x] Return appropriate schema with parameter definitions
- [x] 1.5 Register strategy in API endpoints `backend/app/api.py`
  - [x] Add strategy metadata to `/api/strategies` endpoint
  - [x] Include id, name, description, and category

## 2. Swing Detection Algorithm
- [ ] 2.1 Implement swing high detection
  - [ ] Use rolling window to find local maxima
  - [ ] Configurable lookback period (default: 20 bars)
  - [ ] Validate swing high is confirmed (not broken)
- [ ] 2.2 Implement swing low detection
  - [ ] Use rolling window to find local minima
  - [ ] Same lookback period as swing high
  - [ ] Validate swing low is confirmed
- [ ] 2.3 Calculate Fibonacci levels
  - [ ] Calculate range: swing_high - swing_low
  - [ ] Calculate 0.5 level: swing_low + (range * 0.5)
  - [ ] Calculate 0.618 level: swing_low + (range * 0.618)
  - [ ] Store levels for each valid swing

## 3. Entry/Exit Logic
- [ ] 3.1 Implement Fibonacci level detection
  - [ ] Check if price is within tolerance of 0.5 level
  - [ ] Check if price is within tolerance of 0.618 level
  - [ ] Default tolerance: 0.5% of price
- [ ] 3.2 Implement bounce confirmation
  - [ ] Detect price reversal at Fibonacci level
  - [ ] Use candlestick pattern or momentum indicator
  - [ ] Confirm bounce direction aligns with trend
- [ ] 3.3 Implement exit logic
  - [ ] Exit when price reaches swing high (target)
  - [ ] Exit when price crosses below EMA 200 (trend break)
  - [ ] Support standard stop loss/take profit

## 4. Testing & Validation
- [ ] 4.1 Test swing detection algorithm with historical data
- [ ] 4.2 Verify Fibonacci levels calculate correctly
- [ ] 4.3 Test strategy with default parameters on BTC/USDT 4h timeframe
- [ ] 4.4 Verify buy signals generate at Fibonacci levels
- [ ] 4.5 Verify sell signals generate correctly
- [ ] 4.6 Test parameter optimization with Grid Search
- [ ] 4.7 Verify chart visualization shows EMA 200, Fibonacci levels, and swing points
- [ ] 4.8 Test compatibility with Stop Loss/Take Profit
- [ ] 4.9 Verify frontend dynamic parameter loading works

## 5. Documentation
- [ ] 5.1 Add docstrings to strategy class explaining logic
- [ ] 5.2 Document swing detection algorithm
- [ ] 5.3 Document Fibonacci calculation methodology
- [ ] 5.4 Document parameter ranges and defaults
- [ ] 5.5 Add example usage in strategy description
- [ ] 5.6 Create visual diagram showing Fibonacci levels and entry points
