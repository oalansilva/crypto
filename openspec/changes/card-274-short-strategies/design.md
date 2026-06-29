## Context

The current product flow is:

1. Admin selects/configures a Combo template.
2. `/api/combos/optimize` or batch optimization runs `ComboOptimizer`.
3. The best result is saved as a Favorite.
4. Favoritos displays saved/regenerated trades.
5. Monitor reads `/api/opportunities/` and `/api/favorites/{id}/trades` for status and markers.

The read-only audit found:

- `ComboOptimizer.extract_trades_with_mode` and `deep_backtest.simulate_execution_with_15m` already accept `direction`.
- `FavoriteStrategy.parameters.direction` already exists in saved payloads, but is not a first-class DB column.
- Monitor and chart code still contain long-side assumptions.
- `BacktestService` and `src.engine.Backtester` are long-only and are not called by the active Combos/Favoritos/Monitor screens.
- `ComboOptimizer.__init__` still instantiates `BacktestService` even though modern optimization does not use it.

## Goals

- Make the active modern flow short-ready without adding real exchange short execution.
- Keep long behavior unchanged by default.
- Separate the concepts:
  - `direction`: `long|short`;
  - phase: `entry|exit|in_position|flat`;
  - market/visual action: `COMPRA|VENDA|COBERTURA`.
- Remove or isolate legacy long-only dependencies from active modern screens.
- Add regression coverage that catches inverted short labels or long-only stops.

## Non-Goals

- Binance Futures/Margin integration.
- Short order placement, leverage, margin risk, liquidation or exchange `positionSide`.
- Full DB redesign of every historical backtest table in this card.
- Production release.

## Decisions

- Treat `direction` in saved favorite parameters as the compatibility source, and normalize it at API boundaries while avoiding broad DB migration unless code proves it is required.
  - Rationale: current favorites already use this JSON contract, and the card can ship safely by making the contract explicit in responses and tests.
- Keep `signal == 1` as strategy entry and `signal == -1` as strategy exit in the combo engine.
  - Rationale: changing signal polarity would break existing combo templates; direction decides whether entry renders as buy or sell.
- Remove the long-only stop from `ComboStrategy.generate_signals` for short, or make it explicitly direction-aware.
  - Rationale: extracting stops in `extract_trades_with_mode` avoids duplicated stop semantics.
- Make marker phase explicit at marker-build time when possible.
  - Rationale: `COMPRA` is an entry only for long; for short it is a cover/exit.
- Keep the legacy backtest service only if it still has non-runtime tests/admin callers, but rename/comment it as legacy long-only and disconnect it from modern combo paths.

## Risks / Trade-offs

- Monitor has several fallback paths; a frontend-only label fix may not cover backend payload status. Backend and frontend need aligned direction semantics.
- Existing favorites may have missing `direction`; they must default to `long`.
- Removing old wrappers can break stale unused components if they are later reconnected. This is acceptable only after search proves no active route imports them.
- Global OpenSpec validation may still include old incomplete changes; focused validation for this change must be recorded separately.

## Validation Plan

- Backend unit tests:
  - short profit positive when exit is below entry;
  - short stop triggers on high above entry;
  - long regression unchanged;
  - `ComboStrategy.generate_signals` does not emit long-only stop exits for short.
- Backend integration/service tests:
  - favorite regeneration preserves `direction=short`;
  - opportunity payload/message is side-aware for short.
- Frontend tests:
  - marker phase classification works for long and short;
  - Monitor resolver labels short active as `VENDA`/short and short exit as `COMPRA`/cover.
- Runtime:
  - `./restart`;
  - DEV URL responds;
  - focused API/browser smoke for one short favorite or deterministic test fixture.
