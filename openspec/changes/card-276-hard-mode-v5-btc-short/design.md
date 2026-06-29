## Context

The run is operational but produces durable evidence and likely TradingView artifacts. It must therefore follow the repo workflow before any T0 snapshot, search, Favorite save, or versioned file generation. The target execution is explicitly `DIRECTION=short`; long Favorites, long passive baselines, and long-only references may be observed for exclusion but cannot become mandatory benchmarks or winners.

## Decisions

- Use card #276 as the sole evidence trail for decisions, blockers, saved Favorites, validation, commits, and final status.
- Use `card-276-hard-mode-v5-btc-short` as the work branch and OpenSpec change.
- Treat the existing `btc-pareto-favorite-discovery` spec as the source capability and apply a direction-aware SHORT delta rather than creating a separate duplicate capability.
- Capture T0 before any search-side mutation:
  - current BTC/USDT 1d Favorites split by direction;
  - current SHORT Favorites with IDs, names, strategy keys, public fields, parameters, metrics, date span, and refresh metadata;
  - current compatible templates;
  - public strategy display/description mappings and their source;
  - existing related Pine scripts;
  - API/tela metrics where available.
- If no valid SHORT Favorites exist at T0, set `COLD_START_MODE=true`, register that in #276, and proceed; this is not a blocker.
- Revalidate any existing SHORT Favorites with deep backtest, 100 USD capital, 100% entry/exit, no partial exits, no pyramiding, and full-period coverage before using them as benchmarks.
- Only count a candidate as executed if it has a final deep backtest in the selected direction and is materially unique.
- Before saving any winner, validate the public-name contract through the same resolver/payload path used by the API/tela. If the resolver would fall back to `Estratégia Cripto Farol` or generic copy, stop and fix the product path via the governed branch/OpenSpec flow before saving.
- After each accepted winner, re-read `/api/favorites/`, the individual Favorite endpoint, trades, and served/tela data when available; then recalibrate the chain before searching the next winner.
- Save Pine scripts only for accepted winners, in a versioned repo path, and require `strategy.entry(..., strategy.short)`.

## Validation Strategy

- Board validation: GraphQL readback proving #276 is in Project 1 with `Status=In Progress`, `Tipo=Codigo`, `Frente=Backtest`, `Responsavel=Codex`, and `Prioridade=P1`.
- OpenSpec validation: `openspec status --change card-276-hard-mode-v5-btc-short --json` and focused validation for changed specs before Done.
- T0 validation: timestamped snapshot with DB/API/template/mapping/Pine evidence.
- Runtime validation: live API readbacks for Favorites and trades, with `execution_mode=deep_15m` or equivalent deep proof.
- Naming validation: resolver/test/API proof that none of the new Favorites returns fallback or generic public copy.
- Sequential validation: final metrics prove WINNER_N is not dominated and satisfies the required improvement against every prior winner.
- If code changes occur: focused tests, Codex review before commit, integration into `develop`, `./restart`, and served API/tela validation before `Status=Done`.

## Risks

- The current engine may not support true SHORT execution under the required capital/sizing/deep constraints. If proven, this is a real blocker before any winner is counted.
- Existing public-name mapping may not support new strategy keys without backend changes. If so, fix before saving, not by editing final DB rows manually.
- Search quotas are large. Partial progress cannot be reported as success with fewer than five valid winners.
