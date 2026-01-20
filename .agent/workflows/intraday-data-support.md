<openspec_proposal>
id: intraday-data-support
title: Intraday Data Support for Realistic Backtesting
description: Implement "Deep Backtesting" capability by fetching and utilizing intraday (1h/15m) data to validate trade execution precision, resolving the "Look-Inside Bias" of Daily-only backtests.
source: user-request (fix daily bias)
tags: [backend, data-integrity, backtest-engine, high-priority]

files:
  - backend/app/services/backtest_service.py
  - backend/app/services/combo_optimizer.py
  - backend/src/data/incremental_loader.py
  - backend/app/schemas/backtest_params.py

testing:
  - Verify that a tight stop (1.5%) trade that survives in Daily but fails in Intraday is correctly marked as a LOSS.
  - Compare results against TradingView's "Deep Backtesting" metric for the same period.

security:
  - Ensure API rate limits are respected when fetching multiplied data volume (24x or 96x data points per day).

parameters:
  - Resolution: 1h (default) or 15m.
  - Lookback: Intraday data availability might be limited compared to Daily history.

objectives:
  - [ ] Update `IncrementalLoader` to fetch secondary timeframe data (e.g., download 1h data for the same period as 1d).
  - [ ] Modify `combo_optimizer.py` execution logic:
      - Generate signals on `1d` dataframe.
      - For each trade day, slice the corresponding `1h` (or `15m`) candles.
      - Iterate through `1h` candles to check:
          1. Did `Low` hit Stop Loss? -> EXIT NOW.
          2. Did `High` hit Target/Close? -> EXIT LATER.
      - Determine exact exit time and price based on the first event.
  - [ ] Update DB schema (if needed) to store heavy intraday data efficiently (Parquet already handles this well).
  - [ ] Add UI toggle: "Deep Backtest (Slower, More Accurate)" vs "Fast Backtest (Daily Only)".
</openspec_proposal>
