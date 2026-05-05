## Context

Card #128 targets the Favorites page filter UX. The existing `getFavoriteStrategyName` helper intentionally cleans favorite names for display, but a filter named Strategy should not depend on free-form favorite names.

## Decision

Use `getFavoriteStrategyLabel` as the canonical Strategy filter value. It is derived from the actual strategy/template label and does not include symbol or timeframe. Keep `getFavoriteStrategyName` for row/card title display.

## UI/UX

No layout changes. The existing compact Favorites filters remain unchanged:
- `Symbol` filters symbols.
- `Strategy` filters strategy labels only.
- `Time` filters timeframe/hours.

## Testing

Update the existing Favorites E2E test to assert:
- Strategy filter contains `ema rsi`.
- Strategy filter does not contain favorite nicknames, symbols, or timeframes.
- Time filter still contains `1h` and `4h`.
- Selecting `ema rsi` keeps both rows that use that strategy.
