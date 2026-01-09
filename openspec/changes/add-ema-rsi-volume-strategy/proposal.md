# Change: Add EMA 50/200 + RSI + Volume Strategy

## Why
The user requested the implementation of the most popular Bitcoin trading strategy: **EMA 50/200 + RSI + Volume**. This strategy is widely used for BTC because:
- BTC respects long-term moving averages (EMA 200)
- Reduces noise and false signals
- Ideal for capturing trending moves
- Combines trend confirmation (EMAs) with momentum (RSI) and volume validation

## What Changes
- Add a new strategy class `EmaRsiVolumeStrategy` to the backend
- Implement the strategy logic using pandas-ta:
  - **EMA 50** (fast moving average)
  - **EMA 200** (slow moving average - trend filter)
  - **RSI** (momentum indicator, default period 14)
  - **Volume** (confirmation filter)
- **Buy Logic**:
  - Price above EMA 200 (bullish trend filter - only buy in uptrend)
  - Price pulls back to EMA 50
  - RSI between 40-50 (pullback zone, not oversold)
  - Volume confirmation (optional enhancement)
- **Sell Logic**:
  - Price crosses below EMA 50
  - OR RSI drops below 40 (momentum loss)
- Register the strategy in the backend strategy factory
- Add parameter metadata for dynamic loading in frontend
- Ensure compatibility with:
  - Standard Stop Loss/Take Profit mechanisms
  - Parameter Optimization (Grid Search)
  - Sequential Optimization
- Add visualization for EMA 50, EMA 200, and RSI on results chart

## Impact
- **Affected specs**: `strategy-enablement`, `chart-visualization`
- **Affected code**:
  - Backend: 
    - New strategy class: `backend/app/strategies/ema_rsi_volume.py`
    - Strategy factory: `backend/app/services/backtest_service.py`
    - Schema generator: `backend/app/schemas/dynamic_schema_generator.py`
    - Indicator params: `backend/app/schemas/indicator_params.py`
    - API endpoints: `backend/app/api.py`
  - Frontend: 
    - Strategy selection UI (automatic via dynamic loading)
    - Parameter forms (automatic via schema generation)
    - Chart visualization (automatic via indicator metadata)

## Non-Goals
- This change does NOT include advanced volume analysis (e.g., volume profile, OBV)
- This change does NOT modify existing strategies
- This change does NOT alter the optimization engine
