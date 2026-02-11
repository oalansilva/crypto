# Tasks: proactive-log-monitoring

1. Add Dev-stage input normalizer for timeframe and symbol before backtest.
2. Add error classifier utility for exchange/download errors.
3. Capture classifier output in Dev execution flow and attach to run record.
4. Add Dev fallback adjustment when backtest fails with classified error.
5. Persist diagnostic in run log JSON.
6. Expose diagnostic in lab run API response schema.
7. Add tests for Dev normalization (4H -> 4h, BTC/USDT -> BTCUSDT).
8. Add tests for invalid interval classification.
