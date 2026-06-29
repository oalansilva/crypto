## Context

This card runs after `card-274-short-strategies`, which made the active Combos/Favorites/Monitor flow direction-aware for Short semantics. The current task is not to mix strategy directions; it must use only `direction=short` for BTC/USDT 1D.

## Constraints

- `SYMBOL=BTC/USDT`
- `TIMEFRAME=1d`
- `DIRECTION=short`
- `TARGET_WINNERS=5`
- `deep_backtest=true`
- `initial_capital=100`
- `entry_size_pct=100`
- `exit_size_pct=100`
- `pyramiding=0`
- `allow_partial_exits=false`
- No Long winner, Long fallback, or Long mandatory benchmark is allowed.

## Execution Design

1. Confirm governance.
   - Card #275 must exist in Project 1 and be `Status=In Progress`.
   - This OpenSpec change must be published to the issue before technical execution.
2. Capture T0.
   - Query current Short favorites, templates, public mappings/descriptions, Pine files, and the current full-period Short benchmark evidence.
3. Build benchmarks.
   - Use only same-direction favorites and compatible Short references.
   - Record incompatible references and why they were discarded.
4. Search and rank candidates.
   - Run materially different Short theses and template families.
   - Count only final deep backtests with confirmed Short direction as executed material candidates.
5. Save winners.
   - Before save, prove public name/description resolution and direction.
   - After save, re-read DB/API/trades/UI-equivalent evidence and verify no fallback display.
   - Recalibrate the chain after every winner.
6. Preserve artifacts.
   - Keep T0, candidate ranking, winner validation, and Pine Script under versioned paths.
   - Use comments on issue #275 for evidence and blockers.

## Blocking Conditions

Block only with evidence if Short execution is not technically supported, if Favorites cannot persist/display Short direction and public names, or if the full minimum search budget is exhausted without a valid next sequential winner.

## Validation Plan

- OpenSpec focused validation for this change.
- API/DB evidence for T0 and each saved favorite.
- `/api/favorites/` and individual favorite/trades readback for each winner.
- Negative fallback check for `Estratégia Cripto Farol`.
- Pine Script inspection for `strategy.short`, 100% sizing, 100 USD capital, and no pyramiding.
