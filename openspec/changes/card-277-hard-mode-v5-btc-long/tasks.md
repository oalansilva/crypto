## 1. Governance

- [x] 1.1 Create and configure GitHub issue/card #277 in Project 1 with `Status=In Progress` and the goal contract.
- [x] 1.2 Create branch `card-277-hard-mode-v5-btc-long` from updated `develop`.
- [x] 1.3 Publish OpenSpec artifacts to the card before implementation/search evidence is finalized.

## 2. T0 And Benchmarks

- [x] 2.1 Capture timestamped T0 snapshot for BTC/USDT 1d Long Favorites, direction counts, templates, public mappings, related Pine files, and runtime/API availability.
- [x] 2.2 Revalidate existing same-direction Favorites with Deep Backtest, capital 100 USD, 100% in/out, no partial exits, and no pyramiding when they exist.
- [x] 2.3 Determine `COLD_START_MODE`, same-direction benchmarks, initial Pareto set, compatible references, and discarded incompatible references.

## 3. Search And Save Winners

- [x] 3.1 Execute material Long-only candidate cycles for Winner 1 with novelty, robustness, anti-duplicate, anti-fallback, and full-period gates.
- [x] 3.2 Save and validate Winner 1, then recalibrate the chain benchmark set.
- [x] 3.3 Execute, save, validate, and recalibrate Winner 2 against Winner 1.
- [x] 3.4 Execute, save, validate, and recalibrate Winner 3 against Winners 1-2.
- [x] 3.5 Execute, save, validate, and recalibrate Winner 4 against Winners 1-3.
- [x] 3.6 Execute, save, validate, and recalibrate Winner 5 against Winners 1-4.

## 4. Versioned Evidence

- [x] 4.1 Generate TradingView Pine Script for each valid winner with Long entry, initial capital 100, percent-of-equity sizing, and no pyramiding.
- [x] 4.2 Save final report and evidence artifacts in versioned repo paths.
- [x] 4.3 Clean up or document temporary templates and scratch artifacts.

## 5. Validation And Closeout

- [x] 5.1 Validate this OpenSpec change and any affected focused tests.
- [x] 5.2 Run Codex review on the exact diff before commit.
- [ ] 5.3 Commit/integrate into `develop`, run `./restart`, and re-read served Favorites/API evidence if 5/5 succeeds or a product fix was required.
- [ ] 5.4 Move card to `Status=Done` only after technical validation, integration into `develop`, runtime proof, and evidence comment; never move to `Homologado` without Alan approval.
