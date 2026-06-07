## Why

Alan requested a governed HARD MODE V5 BTC/USDT 1D Long search that only succeeds when five genuinely new, sequentially superior Favorites are saved and visible without public-name fallback. Prior BTC favorite work showed that DB saves, stale deep backtests, or missing public mappings can create false positives, so this run needs auditable artifacts and gates before any candidate is counted.

## What Changes

- Add an auditable execution package for issue #262, including T0 snapshot, benchmark revalidation, candidate ranking, saved-winner evidence, and TradingView Pine artifacts when winners are found.
- Require each new saved Favorite to preserve BTC/USDT 1d Long, deep backtest, capital 100 USD, 100% entry/exit, no partial exits, and no pyramiding.
- Require sequential winner gates: each later winner must be non-duplicated, non-dominated, and materially better than all previously saved winners in the chain.
- Require explicit public-name and description resolution before saving a new strategy, with no `Estratégia Cripto Farol` or generic fallback in API/readback.
- Do not publish to production; technical completion stops at `develop`/DEV evidence because `PROD_RELEASE=false`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `favorites-management`: Favorites saved by this run must be provably new versus T0, visible through API/readback, and validated after save before counting as winners.
- `combo-optimizer`: Candidate optimization/backtest evidence must use Deep Backtest with the fixed BTC/USDT 1d Long capital and sizing invariants.
- `strategy-template-descriptions`: New strategy keys introduced by this run must resolve specific `strategy_display_name` and `strategy_description` values before save and after served readback.

## Impact

- Affected runtime/API areas: combo optimize/backtest, Favorites save/read/trades, favorite refresh/readback, public strategy description resolver, and PostgreSQL-backed persistence.
- Affected repo artifacts: `openspec/changes/card-262-hard-mode-v5-btc-winners/`, generated T0/report artifacts, optional TradingView Pine files, and focused backend tests if public mappings or save behavior need code changes.
- No production release is authorized by this change.
