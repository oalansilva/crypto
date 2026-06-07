## Why

Alan requires a new BTC/USDT 1d long Favorite that is genuinely novel versus the current Favorites baseline and strong enough to enter the non-dominated Pareto set after deep full-period validation.
Prior runs can produce false positives when they save renamed, duplicated, fallback-named, or dominated strategies, so this change makes the execution contract auditable before any optimization or save.

## What Changes

- Capture a pre-search T0 snapshot for BTC/USDT 1d long Favorites, templates, public mappings, Pine scripts, and current deep benchmark revalidations.
- Execute a governed HARD MODE V3 search with fixed invariants: deep backtest, 100 USD, 100% entry, 100% exit, no partial exits, no pyramiding, no leverage, BTC/USDT only, 1d only, long only.
- Compare every finalist against all current revalidated Favorites, multi_ma_crossover, multi_ma_crossoverV2, and buy-and-hold/reference where available.
- Save a new Favorite only when it passes novelty, anti-duplicate, non-dominance, Pareto, full-period, OOS, stress, public-name, and API visibility gates.
- Preserve any final Pine script, report, public mapping, test, or other durable artifact in Git through the project card workflow.
- Stop with an explicit blocker only after the configured minimum search, candidate, family, cycle, finalist, and Pareto-member quotas are satisfied or a real technical impediment is proven.

## Capabilities

### New Capabilities
- `btc-pareto-favorite-discovery`: Auditable operational contract for discovering, validating, saving, and reporting a novel BTC/USDT 1d long Pareto Favorite.

### Modified Capabilities
- `favorites`: Final saved Favorite visibility, display name, description, updated backtest metrics, and trades readback must prove absence of fallback copy for the new strategy.
- `strategy-template-descriptions`: Any new strategy_name introduced by the run must have explicit public display and description mapping with focused validation.

## Impact

- Potentially affected backend files: strategy description mapping, focused unit tests, combo/favorites services only if a bug blocks the required validation.
- Potentially affected durable artifacts: `qa_artifacts/`, `docs/tradingview/`, and issue comments containing sanitized payload/evidence summaries.
- Operational systems: PostgreSQL runtime database, `/api/combos/*`, `/api/favorites/*`, `./restart`, and GitHub Project 1 card `#261`.
