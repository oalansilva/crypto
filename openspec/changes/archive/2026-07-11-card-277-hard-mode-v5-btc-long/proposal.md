## Why

Alan requested a governed HARD MODE V5 execution to discover and save five new BTC/USDT 1d Long Favorites. The run needs an auditable card, T0 snapshot, direction-safe benchmarks, sequential Pareto gates, fallback-free public names, and versioned evidence before any technical search counts as complete.

## What Changes

- Execute a single-direction BTC/USDT 1d Long discovery run for exactly five sequential winners.
- Preserve the hard execution model: Deep Backtest, 100 USD initial capital, 100% entry, 100% exit, no partial exits, no pyramiding, no leverage, and full-period final proof.
- Capture T0 before optimization and prove each saved winner is new, non-duplicate, non-dominated, and visible in Favorites without generic fallback copy.
- Generate versioned evidence artifacts and Pine Script exports for the saved winners.
- Do not publish to production; with `PROD_RELEASE=false`, stop at technical Done on `develop` only after valid 5/5 delivery or a real documented blocker.

## Capabilities

### New Capabilities

### Modified Capabilities
- `btc-pareto-favorite-discovery`: extend the hard-mode BTC discovery contract to cover single-direction Long execution, cold-start behavior, five sequential winners, recalibration after each save, and versioned final evidence/Pine artifacts.
- `strategy-template-descriptions`: require every saved sequential winner to resolve explicit display and description copy before save and after served API readback.

## Impact

- Runtime/API: `/api/combos/optimize`, `/api/combos/backtest`, `/api/favorites/`, individual Favorite/trades endpoints, and PostgreSQL-backed Favorite/template state.
- Evidence: T0 snapshot, per-cycle candidate logs, final report, and TradingView Pine files under versioned repo paths.
- Product copy: public strategy display/description mappings if new `strategy_name` values are not accepted directly by the save payload.
- Workflow: issue `#277`, Project 1 `Status=In Progress`, branch `card-277-hard-mode-v5-btc-long`, and OpenSpec change `card-277-hard-mode-v5-btc-long`.
