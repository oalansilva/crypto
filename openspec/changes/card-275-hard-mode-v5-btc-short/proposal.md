## Why

Alan requested a governed HARD MODE V5 search for exactly five new BTC/USDT 1D Short favorites. The run must be single-direction, must not use Long as fallback or mandatory benchmark, and must prove each saved strategy is new, visible, deep-backtested, non-duplicated, non-dominated, and sequentially better than previous winners.

## What Changes

- Create a complete T0 snapshot for BTC/USDT 1D Short favorites, compatible templates, public-name mappings, descriptions, Pine scripts, and revalidated current Short favorites.
- Build Short-only benchmark sets from current Short favorites: return, drawdown, Sharpe, profit factor, and Pareto set.
- Run adaptive Short-only candidate exploration with deep backtest, capital 100 USD, 100% entry, 100% exit, no partial exits, no pyramiding, and no additional leverage.
- Save only candidates that pass novelty, anti-duplicate, anti-fallback public naming, robustness, dominance, and sequential superiority gates.
- Generate versioned evidence and Pine Script for each accepted Short winner.
- Stop in DEV/`develop` with `Status=Done` only after 5/5 winners are saved and validated, or block with the evidence required by the goal contract.

## Capabilities

### Modified Capabilities

- `favorites`: New BTC/USDT 1D Short winners must persist direction and public display/description without fallback names.
- `combo-optimizer`: Candidate optimization/backtest evidence must prove deep execution with Short direction and the required capital/sizing model.
- `chart-visualization`: TradingView Pine exports for accepted winners must represent real Short entry/cover behavior.

## Impact

- Backend/runtime: read/write via existing Combos/Favorites APIs and PostgreSQL DEV data.
- Repo artifacts: OpenSpec, T0/evidence reports, and Pine Script files if winners are saved.
- Production: none. `PROD_RELEASE=false`.
