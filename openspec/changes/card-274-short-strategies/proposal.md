## Why

Alan wants to start working with short strategies in the current operational flow: Combos, Favoritos and Monitor. A read-only trace showed that these screens already use the modern combo/favorite/opportunity paths, not the legacy `src.engine.Backtester`, but the product contract is still mixed: some code treats `COMPRA` as entry and `VENDA` as exit, while short strategies need `VENDA` as entry and `COMPRA` as cover/exit.

The legacy long-only engine also remains reachable through stale service imports and old wrappers. Leaving it attached to the modern path makes it easy to accidentally route short work through code that cannot simulate shorts correctly.

## What Changes

- Make the modern Combo/Favoritos/Monitor flow direction-aware for `long` and `short`.
- Preserve the current long behavior as the default.
- Ensure short trades use entry/exit semantics independent of visual `COMPRA`/`VENDA` labels.
- Prevent `ComboStrategy.generate_signals` from applying a long-only stop to short strategies.
- Make Monitor labels, marker classification, chart modal labels and opportunity cards side-aware.
- Keep favorite trade regeneration and refresh on the modern `ComboOptimizer` path.
- Remove dead modern-path dependencies on `BacktestService` and remove unused frontend `/api/backtest/*` wrappers when no active screen imports them.
- Document or isolate remaining legacy long-only services so they are not treated as short-ready.

## Capabilities

### Modified Capabilities

- `combo-optimizer`: Official execution for modern combo strategies must support short-side trade extraction, stop loss and metrics.
- `favorites`: Saved and regenerated favorites must preserve strategy direction through the modern optimizer path.
- `monitor`: Monitor public status, copy and chart context must render long and short actions correctly.
- `chart-visualization`: Trade marker phase must not be inferred only from `COMPRA`/`VENDA` text.

## Impact

- Backend: combo strategy signal generation, combo optimizer dependency cleanup, favorite regeneration, opportunity payload status/copy.
- Frontend: trade marker helpers, Monitor resolver, Monitor list/card/modal labels, favorite/result/export labels.
- Tests: focused backend unit/integration and frontend node tests for short semantics.
- No real exchange short execution, Futures, margin, leverage or liquidation behavior is introduced.
- Runtime target is DEV only until Alan homologates.
