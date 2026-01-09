# Change: Add Fibonacci (0.5 / 0.618) + EMA 200 Strategy

## Why
The user requested the implementation of a Fibonacci retracement strategy combined with EMA 200 trend filter. This is a professional institutional pullback strategy that works well for BTC because:
- BTC respects deep technical Fibonacci levels (0.5 and 0.618)
- Provides excellent risk/reward ratio
- Ideal for 4h and 1d timeframes
- Combines institutional retracement levels with trend confirmation

## What Changes
- Add a new strategy class `FibonacciEmaStrategy` to the backend
- Implement the strategy logic using pandas-ta:
  - **EMA 200** (trend filter - only trade in direction of trend)
  - **Fibonacci Retracement Levels** (0.5 and 0.618 - golden ratio)
  - **Swing High/Low Detection** (to calculate Fibonacci levels)
- **Buy Logic**:
  - Price above EMA 200 (bullish trend filter)
  - Identify recent swing high and swing low
  - Price retraces to 0.5 or 0.618 Fibonacci level
  - Price bounces from Fibonacci level (reversal confirmation)
- **Sell Logic**:
  - Price crosses below EMA 200 (trend reversal)
  - OR price reaches swing high (take profit at resistance)
  - OR stop loss triggered
- Register the strategy in the backend strategy factory
- Add parameter metadata for dynamic loading in frontend
- Ensure compatibility with:
  - Standard Stop Loss/Take Profit mechanisms
  - Parameter Optimization (Grid Search)
  - Sequential Optimization
- Add visualization for EMA 200, Fibonacci levels, and swing points on results chart

## Impact
- **Affected specs**: `strategy-enablement`, `chart-visualization`
- **Affected code**:
  - Backend: 
    - New strategy class: `backend/app/strategies/fibonacci_ema.py`
    - Strategy factory: `backend/app/services/backtest_service.py`
    - Schema generator: `backend/app/schemas/dynamic_schema_generator.py`
    - Indicator params: `backend/app/schemas/indicator_params.py`
    - API endpoints: `backend/app/api.py`
  - Frontend: 
    - Strategy selection UI (automatic via dynamic loading)
    - Parameter forms (automatic via schema generation)
    - Chart visualization (automatic via indicator metadata)

## Non-Goals
- This change does NOT include advanced Fibonacci extensions (1.272, 1.618, etc.)
- This change does NOT implement automatic Fibonacci drawing tools
- This change does NOT modify existing strategies
- This change does NOT include harmonic patterns (Gartley, Butterfly, etc.)

## Technical Challenges
- **Swing Point Detection**: Need to implement algorithm to identify swing highs/lows
- **Dynamic Fibonacci Calculation**: Fibonacci levels must be recalculated as new swings form
- **Level Tolerance**: Need to define tolerance range for price touching Fibonacci levels
- **Multiple Timeframe Swings**: Different lookback periods may identify different swings
