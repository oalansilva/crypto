## Why

Alan requested a governed HARD MODE V5 execution to find and save five new BTC/USDT 1d SHORT Favorites without relying on manual card creation, mixed-direction fallback, or public-name fallback. The existing BTC Pareto discovery contract is long-specific and needs a direction-aware operational delta for this card before any search artifacts are generated.

## What Changes

- Run a single-direction BTC/USDT 1d SHORT discovery cycle for card #276.
- Require Project 1 traceability, T0 snapshot, benchmark/cold-start classification, and card evidence before technical search.
- Enforce SHORT-only deep backtests with 100 USD, 100% entry, 100% exit, no partial exits, no pyramiding, no leverage, and no residual position.
- Save exactly five sequential Pareto winners only when each Favorite is new, visible, direction-correct, public-name-safe, robust, and better than all prior winners when applicable.
- Generate versioned evidence artifacts and TradingView Pine files for accepted winners.
- Stop only on success or on a real blocker that satisfies the requested evidence thresholds.

## Capabilities

### New Capabilities

### Modified Capabilities
- `btc-pareto-favorite-discovery`: Extend the BTC/USDT 1d discovery workflow from long-only to direction-aware SHORT execution with cold-start handling, sequential winners, anti-fallback public naming, and stricter blocking evidence.

## Impact

- Project 1 issue/card #276 and evidence comments.
- OpenSpec artifacts for this change.
- Runtime/API/DB readback for Favorites and trades using PostgreSQL only.
- Potential versioned artifacts under the repo for T0 snapshot, candidate reports, final report, and TradingView Pine scripts.
- Potential backend/frontend/script changes only if the official save/display path cannot satisfy public-name, direction, or backtest visibility requirements.
