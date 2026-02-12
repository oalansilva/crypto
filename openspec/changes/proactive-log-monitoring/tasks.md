# Tasks: proactive-log-monitoring

- [ ] Add Dev-stage input normalizer for timeframe and symbol before backtest.
- [ ] Add error classifier utility for exchange/download errors.
- [ ] Capture classifier output in Dev execution flow and attach to run record.
- [ ] Add Dev fallback adjustment when backtest fails with classified error.
- [ ] Persist diagnostic in run log JSON.
- [ ] Expose diagnostic in lab run API response schema.
- [ ] Add tests for Dev normalization (4H -> 4h, BTC/USDT -> BTCUSDT).
- [ ] Add tests for invalid interval classification.
