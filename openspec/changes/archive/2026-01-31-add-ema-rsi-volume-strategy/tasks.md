## 1. Backend Implementation
- [x] 1.1 Create `EmaRsiVolumeStrategy` class in `backend/app/strategies/ema_rsi_volume.py`
  - [x] Implement `__init__` to accept configurable parameters (ema_fast, ema_slow, rsi_period, rsi_min, rsi_max)
  - [x] Implement `generate_signals` method with buy/sell logic
  - [x] Calculate EMA 50 and EMA 200 using pandas_ta
  - [x] Calculate RSI using pandas_ta
  - [x] Implement buy condition: (price > EMA 200) AND (price pullback to EMA 50) AND (RSI 40-50)
  - [x] Implement sell condition: (price < EMA 50) OR (RSI < 40)
  - [x] Store simulation_data for visualization
- [x] 1.2 Register strategy in `backend/app/services/backtest_service.py`
  - [x] Import `EmaRsiVolumeStrategy` class
  - [x] Add conditional check in `_get_strategy` method for 'emarsivolume' strategy name
  - [x] Handle both dict config and string name formats
  - [x] Support parameter merging for optimization mode
- [x] 1.3 Add schema definition in `backend/app/schemas/indicator_params.py`
  - [x] Define `EMA_RSI_VOLUME_SCHEMA` with parameters: ema_fast (default 50), ema_slow (default 200), rsi_period (default 14), rsi_min (default 40), rsi_max (default 50)
  - [x] Add optimization ranges for each parameter
  - [x] Register schema in `INDICATOR_SCHEMAS` dict
- [x] 1.4 Update dynamic schema generator in `backend/app/schemas/dynamic_schema_generator.py`
  - [x] Add conditional check for 'emarsivolume' strategy
  - [x] Return appropriate schema with parameter definitions
- [x] 1.5 Register strategy in API endpoints `backend/app/api.py`
  - [x] Add strategy metadata to `/api/strategies` endpoint
  - [x] Include id, name, description, and category

## 2. Testing & Validation
- [x] 2.1 Test strategy with default parameters on BTC/USDT 4h timeframe
- [x] 2.2 Verify buy signals generate correctly (trend filter + pullback + RSI)
- [x] 2.3 Verify sell signals generate correctly
- [ ] 2.4 Test parameter optimization with Grid Search
- [ ] 2.5 Verify chart visualization shows EMA 50, EMA 200, and RSI
- [ ] 2.6 Test compatibility with Stop Loss/Take Profit
- [ ] 2.7 Verify frontend dynamic parameter loading works

## 3. Documentation
- [x] 3.1 Add docstrings to strategy class explaining logic
- [x] 3.2 Document parameter ranges and defaults
- [x] 3.3 Add example usage in strategy description
