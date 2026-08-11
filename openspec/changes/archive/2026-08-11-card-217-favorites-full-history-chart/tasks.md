## 1. Favorites Chart Source Selection

- [x] 1.1 Merge saved and market candle series when opening Favorites analysis.
- [x] 1.2 Preserve current market candles when they are at least as complete as saved chart context.
- [x] 1.3 Request full persisted symbol/timeframe history for Favorites charts, independent of strategy.
- [x] 1.4 Preserve recent backend candles when saved backtest chart context is longer but stale.
- [x] 1.5 Schedule OHLCV backfill automatically when full market history is incomplete or stale.
- [x] 1.6 Include favorite symbols/timeframes in the OHLCV backfill scheduler by default.
- [x] 1.7 Run the backfill scheduler once on backend startup so Favorites history begins filling automatically.

## 2. Regression Coverage

- [x] 2.1 Add Playwright coverage for a long-history Multi MA Crossover favorite.
- [x] 2.2 Keep existing stale-saved-candle behavior covered.
- [x] 2.3 Add backend endpoint coverage for `full_history=true`.
- [x] 2.4 Add backend coverage for automatic full-history backfill scheduling.

## 3. Validation

- [x] 3.1 Run focused Favorites Playwright tests.
- [x] 3.2 Run frontend build.
- [x] 3.3 Run OpenSpec validation for the change and global OpenSpec validation.

Note: use project skills when applicable: `crypto-frontend` for UI changes and OpenSpec skills for artifact/apply/verify flow.
