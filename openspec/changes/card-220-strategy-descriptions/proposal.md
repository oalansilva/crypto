## Why

Generated strategies are visible in product surfaces with technical or generic names that make comparison harder for common users. The same surfaces must explain the strategy purpose without exposing parameters, thresholds, formulas, indicator recipes, or implementation details that would let a user recreate the strategy outside Cripto Farol.

## What Changes

- Add a curated public identity catalog for generated strategy templates: safe display names and short product descriptions.
- Use those public names and descriptions in common-user Favorites and Monitor payloads.
- Keep technical template names, parameters, entry/exit rules, and raw descriptions available only in admin/internal surfaces already allowed to view strategy secrets.
- Preserve strategy execution, ranking, backtest, refresh, and parameter behavior.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `strategy-template-descriptions`: Public strategy identity must include safe, distinguishable names and descriptions that do not expose replicable strategy logic.
- `monitor`: Protected common-user Monitor payloads must use safe public strategy identities while keeping technical details redacted.

## Impact

- Backend public copy helpers for strategy names/descriptions.
- Backend redaction for Favorites and Monitor payloads.
- Focused tests for public copy safety and admin/common-user visibility boundaries.
- No database schema changes, no strategy parameter changes, and no backtest engine changes.
