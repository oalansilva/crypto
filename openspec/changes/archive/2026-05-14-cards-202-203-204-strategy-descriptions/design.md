## Overview

Use a central strategy-description helper so backend responses can expose the same public copy regardless of whether the source is a combo template, favorite, or monitor opportunity. Keep descriptions high level and non-promissory.

## Decisions

- `strategy_description` is the public field name added to Favorites and Monitor payloads.
- Combo templates keep using `description`, but the service normalizes it through the same public helper.
- Protected/common users may see public strategy descriptions because descriptions do not expose parameters or rules.
- `/optimize` final visualization must call `extract_trades_with_mode(...)`, not `extract_trades_from_signals(...)`, so final trades match deep-mode scoring.

## Risks

- Existing database descriptions may be technical or English. The helper provides curated copy for known templates and a safe fallback for custom templates.
- Favorites table is dense. Strategy identity remains inside the existing strategy column/card block to avoid adding width pressure.
- Deep Backtest can still fall back to fast mode when 15m coverage is insufficient; the final path must follow the same helper and fallback behavior as scoring.

## Validation

- Backend tests assert description fields and deep final extraction mode.
- Frontend build verifies TypeScript shape and rendering.
- Existing OpenSpec global validation remains required before Done.
