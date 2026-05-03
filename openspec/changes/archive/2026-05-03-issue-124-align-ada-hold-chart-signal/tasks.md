## 1. Backend Contract

- [x] 1.1 Update Monitor position-state resolution so `HOLD` requires an active entry confirmation.
- [x] 1.2 Preserve stop-loss and normal-exit handling when active entry confirmation exists or is invalidated.
- [x] 1.3 Keep non-holding bullish strategies in entry-distance context instead of exit-distance context.
- [x] 1.4 Downgrade chart-modal `HOLD` when the active entry signal is not visible in the displayed candles.
- [x] 1.5 Refresh chart candles from CCXT when persisted TimescaleDB candles are stale.
- [x] 1.6 Open Monitor charts on the strategy timeframe by default so signal validation uses matching candles.

## 2. Tests And Validation

- [x] 2.1 Add unit coverage for no-entry bullish trend, active entry, normal exit, and stop-loss exit.
- [x] 2.2 Run focused backend tests for the changed position-state logic.
- [x] 2.3 Run OpenSpec validation for this change.
- [x] 2.4 Run proportional frontend/build validation to confirm the existing UI contract still compiles.
- [x] 2.5 Re-run frontend build after chart-modal active-entry visibility fix.
- [x] 2.6 Add and run regression tests for stale persisted chart candles.
- [x] 2.7 Re-run Playwright chart validation after candle refresh and strategy-timeframe default.

## 3. Operational Closure

- [x] 3.1 Run worktree status classification before moving card to `Done`.
- [x] 3.2 Restart the runtime with `./restart` after validation.
- [x] 3.3 Move GitHub Project card 124 to `Done` with evidence.

Note: use project skills when applicable, especially testing/debugging and frontend validation.
