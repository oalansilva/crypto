## Why

Favorites search only checked whether the full typed string appeared inside a single field. A query like `BTC/USDT USDT multi ma crossoverV2` should locate the starred BTC/USDT strategy, but it spans symbol, quote, and strategy text.

## What Changes

- Change Favorites search to match all query terms across a combined favorite haystack.
- Normalize separators such as `/`, `_`, and `-` so symbols and strategy names are easier to find.
- Keep existing filters for tier, symbol, strategy, timeframe, direction, and crypto-only behavior.

## Capabilities

### New Capabilities

### Modified Capabilities
- `favorites`: Favorites search supports multi-term queries across symbol, quote, strategy, name, and description.

## Impact

- Frontend: Favorites search matching logic.
- Tests: focused E2E coverage for locating BTC/USDT `multi_ma_crossoverV2` with a combined query.
