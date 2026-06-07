## 1. Governance And Preflight

- [x] 1.1 Confirm AGENTS.md, rules.md, alan-workflow, and crypto-btc-favorite-search were used for the run.
- [x] 1.2 Keep issue #261 as the evidence trail and comment every material decision, blocker, artifact, and validation.
- [x] 1.3 Preserve versionable artifacts on branch `card-261-hard-mode-v3-btc-pareto` and avoid production release because `PROD_RELEASE=false`.
- [x] 1.4 Use project skills when applicable for OpenSpec, debugging, tests, frontend/UI validation, and code review.

## 2. T0 Snapshot And Benchmarks

- [x] 2.1 Capture timestamped T0 snapshot before any optimization or exploratory candidate backtest.
- [x] 2.2 Include BTC/USDT 1d long Favorites, templates, public mappings, related Pine scripts, and API-visible metrics in T0.
- [x] 2.3 Revalidate all current BTC/USDT 1d long Favorites full-period with deep backtest, 100 USD, 100% entry, 100% exit, no partials, and no pyramiding.
- [x] 2.4 Define BENCHMARK_RETURN, BENCHMARK_DD, BENCHMARK_SHARPE, BENCHMARK_PF, and current Pareto set.
- [x] 2.5 Compare baselines against multi_ma_crossover, multi_ma_crossoverV2, and buy-and-hold/reference when available.

## 3. Candidate Search And Robustness

- [x] 3.1 Execute adaptive cycles using materially distinct theses and template families against the revalidated Pareto set.
- [x] 3.2 Count only unique final deep backtests that satisfy the hard invariants as executed material candidates.
- [x] 3.3 Reject duplicates, renames, revalidations, dominated candidates, fragile candidates, and overfit candidates before final ranking.
- [x] 3.4 Stress at least six non-duplicate finalists when enough finalists survive preliminary gates.
- [x] 3.5 Continue until a valid winner exists or the configured blocker thresholds are met with evidence.

## 4. Save, Visibility, And Artifacts

- [ ] 4.1 Save only a new non-dominated Pareto winner that passes full-period, OOS, stress, novelty, anti-duplicate, and superation gates.
- [ ] 4.2 Verify the saved Favorite through PostgreSQL, `/api/favorites/`, and trades/equivalent endpoint by new id and metrics.
- [x] 4.3 Add explicit public display and description mapping plus focused validation if the final `strategy_name` is new.
- [x] 4.4 Generate a TradingView Pine script for the saved strategy with 100 USD, 100% equity, no pyramiding, and no partial exits.
- [ ] 4.5 Remove rejected `tmp_quant_*` templates or document why any template remains.

## 5. Closeout

- [x] 5.1 Run focused tests and OpenSpec validation for this change.
- [x] 5.2 Move the card to Code Review, run Codex review over the exact diff, and fix or classify findings before commit.
- [ ] 5.3 Commit the versioned artifacts/code on the branch, integrate into `develop`, run `./restart`, and verify served API/runtime if versioned changes were made.
- [ ] 5.4 Move issue #261 to Done tecnico with final evidence, or leave it In Progress/Blocked with the configured blocker report if completion criteria are not met.
