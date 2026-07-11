## 1. OpenSpec and Governance

- [x] 1.1 Create and publish OpenSpec artifacts to issue #274 before implementation.
- [x] 1.2 Move Project 1 card #274 to `Status=In Progress` and keep board fields verified.

## 2. Backend Short Semantics

- [x] 2.1 Make `ComboStrategy.generate_signals` stop handling safe for short strategies.
- [x] 2.2 Keep `ComboOptimizer.extract_trades_with_mode` as the official modern trade execution path and remove unused `BacktestService` dependency from that path.
- [x] 2.3 Ensure favorite regeneration/refresh preserves `direction=short`.
- [x] 2.4 Make Monitor opportunity status/message fields side-aware for short where current payload is public-facing.

## 3. Frontend Short Semantics

- [x] 3.1 Make trade marker phase classification direction-aware instead of inferring only from `COMPRA`/`VENDA`.
- [x] 3.2 Update Monitor resolver, list/card/modal labels and price lines so short entry renders as `VENDA/SHORT` and short exit as `COMPRA/COBERTURA`.
- [x] 3.3 Update Combo/Favoritos result/export surfaces to preserve and display direction consistently.
- [x] 3.4 Remove unused frontend `/api/backtest/*` wrapper if no active screen imports it.

## 4. Legacy Cleanup

- [x] 4.1 Audit `BacktestService`, `SequentialOptimizer` and `optimization_worker` callers.
- [x] 4.2 Remove dead code or mark remaining legacy code explicitly as long-only/not used by Combos/Favoritos/Monitor.
- [x] 4.3 Confirm active Combos/Favoritos/Monitor paths do not execute `src.engine.Backtester`.

## 5. Validation

- [x] 5.1 Add focused backend tests for short PnL, stop, favorite regeneration and long regression.
- [x] 5.2 Add focused frontend tests for marker/Monitor direction semantics.
- [x] 5.3 Run focused backend and frontend tests.
- [x] 5.4 Run OpenSpec validation for this change and classify any unrelated global failures.
- [x] 5.5 Run `./restart`, validate DEV runtime, and record evidence on issue #274.
