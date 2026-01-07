# Tasks

- [x] Implement `calculate_regime_classification` helper in `app/metrics/regime.py` (new)
- [x] Implement `calculate_avg_indicators` in `app/metrics/indicators.py` (new)
- [x] Update `src/report/metrics.py` (or `app.metrics`) to include Expectancy and Streak loops.
- [x] Update `BacktestService` to ensure `pandas_ta` calculates ADX/ATR/SMA200 for context even if strategy doesn't use them (or conditionally if requested).
- [x] Integrate all new metrics into the final result dictionary.
- [x] Verify optimization results include new metrics.
