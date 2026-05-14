## Why

Strategy discovery exposed existing combo templates that cannot execute because the vectorized logic parser rejects syntax already present in stored templates, including dotted MACD references, `.shift()`, and `.abs()`. This causes silent zero-trade backtests and blocks reliable template ranking.

## What Changes

- Extend combo logic evaluation to support safe pandas Series method calls used by existing templates.
- Normalize dotted indicator references beyond Bollinger aliases, including `macd.macd`, `macd.signal`, and `macd.histogram`.
- Keep parser strict for unknown identifiers and unsupported calls so invalid template logic still fails clearly.
- Add regression tests for templates that currently fail during signal generation.

## Capabilities

### New Capabilities

- `combo-template-logic-parser`: Covers supported syntax and safety behavior for combo template entry/exit logic.

### Modified Capabilities

- `combo-strategies`: Combo strategies can execute existing stored template logic that uses supported Series methods and dotted indicator references.

## Impact

- Affected code: `backend/app/strategies/combos/combo_strategy.py`.
- Affected tests: backend unit tests around combo strategy signal generation.
- No API contract change.
- No database migration.
