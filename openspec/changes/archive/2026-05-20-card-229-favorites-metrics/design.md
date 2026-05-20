## Context

Backend metric calculation in `src/report/metrics.py` stores `total_return_pct` and `total_pnl_pct` as percentage-point values, for example `12` means `12%`. Some frontend flows use decimal ratios for similarly named fields, especially `total_return`, `win_rate`, and drawdown fields. The Favorites page already applies a magnitude heuristic for display, but the optimization-save path multiplies `total_return_pct` by 100 before sending the favorite payload.

## Goals / Non-Goals

**Goals:**
- Preserve backend percentage-point metrics when saving favorites from optimization results.
- Display Favorites percentage fields coherently with sign, unit, and rounding.
- Add regression coverage using a realistic backend payload.

**Non-Goals:**
- Recalculate historical favorite records in the database.
- Change backend metric formulas.
- Change investment claims or product positioning.

## Decisions

- Use field semantics for the save path: `total_return_pct` and `total_pnl_pct` are percentage points; `total_return` is a decimal ratio.
- Keep Favorites display tolerant of old mixed payloads, because existing saved records may contain either decimal ratios or percentage-point values.
- Add Playwright coverage on `/favorites` because the card scope asks for visual/UI evidence on the Favorites screen.

## Risks / Trade-offs

- Existing records already saved with duplicate conversion can still display as high until data is corrected or regenerated. The UI fix prevents creating new inflated records and avoids another display-side multiplication.
- Some old records may have inconsistent `total_return` and `total_return_pct`; Favorites continues to prefer `total_return_pct` where present because that is the backend explicit percentage field.
