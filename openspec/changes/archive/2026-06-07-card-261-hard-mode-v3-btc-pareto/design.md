## Context

The run is an operational strategy-discovery delivery tied to GitHub issue #261. The repo already has combo template optimization, deep combo backtests, Favorites persistence, public strategy display mappings, and TradingView artifacts. The hard requirement is not just finding a strong metric result; the final result must be a new, visible Favorite that survives novelty, anti-duplicate, non-dominance, robustness, and public-copy checks.

The current worktree has unrelated pre-existing changes, so implementation and durable artifacts run in an isolated worktree on branch `card-261-hard-mode-v3-btc-pareto` from `origin/develop`.

## Goals / Non-Goals

**Goals:**
- Preserve a complete T0 snapshot before candidate search.
- Revalidate current BTC/USDT 1d long Favorites under the same deep full-period capital/sizing invariants.
- Search materially different template families and candidates until a valid winner is saved or the configured blocker thresholds are met.
- Preserve any final Pine script, public mapping, focused tests, and report artifacts in Git.
- Keep the Project card as the evidence trail.

**Non-Goals:**
- No production release because `PROD_RELEASE=false`.
- No asset, timeframe, or direction substitution.
- No partial exits, pyramiding, leverage, scale-in, scale-out, or position residue.
- No acceptance of renamed or revalidated existing Favorites as a new strategy.
- No UI redesign unless a discovered visibility bug requires a scoped fix.

## Decisions

- Use PostgreSQL/runtime APIs instead of SQLite or synthetic fixtures for T0, benchmark, save, and visibility proof. This matches the repo runtime contract and avoids false metrics.
- Store durable evidence under repo paths only when it must survive the run. Temporary scratch data may be used for intermediate API calls, but final T0/report/Pine/mapping changes must be versioned when created.
- Treat current revalidated Favorites as the main benchmark set. `multi_ma_crossover`, `multi_ma_crossoverV2`, and buy-and-hold/reference are comparison baselines only, not sufficient victory targets.
- Recompute the Pareto set after benchmark deep validation and reject candidates dominated by any current Favorite. This prevents a single-metric improvement from passing while return/drawdown regress.
- Add explicit strategy display/description mapping and focused tests only if the saved strategy introduces a new `strategy_name`. This keeps public-name work scoped to the final saved Favorite.
- Remove rejected `tmp_quant_*` templates unless a template is intentionally kept as the promoted final strategy or needed for audit evidence.

## Risks / Trade-offs

- Runtime API or DB is unavailable -> stop before search and comment the blocker on #261.
- Deep backtest does not prove `deep_15m` or equivalent -> reject the run result and do not count it as benchmark/candidate evidence.
- Search produces strong but duplicate candidates -> continue until thresholds are met; duplicates do not count toward executed material candidates.
- A saved Favorite later shows fallback copy or stale metrics -> run the mapping/test/restart/readback loop; if still invalid, remove or explicitly mark it invalid and do not report a winner.
- Minimum blocker thresholds can require a long run -> keep cycle summaries on the card and avoid claiming failure before the configured quotas are actually satisfied.
