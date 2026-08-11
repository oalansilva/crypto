## Why

The ADA/USDT daily strategy chart can show `Compra` and `Venda` on the same day without a clear relationship to the trade list or current state. This creates an ambiguous operational signal and weakens trust in Favorites and Monitor charts.

## What Changes

- Normalize chart marker generation so entry/exit markers for the same trade share one coherent candle anchor and cannot appear as unrelated contradictory signals.
- Preserve valid same-day entry/exit trades by representing them as an explicit same-candle round trip instead of two ambiguous independent recommendations.
- Keep Favorites and Monitor chart paths aligned when they render the same favorite strategy.
- Add focused backend/frontend tests for same-day buy/sell marker coherence.

## Capabilities

### New Capabilities

- `same-candle-signal-coherence`: Covers coherent rendering and payload normalization when a trade has entry and exit signals in the same candle/day.

### Modified Capabilities

- `chart-visualization`: Chart surfaces must render same-candle trade signals without making them look like contradictory simultaneous recommendations.
- `favorites-trade-regeneration`: Favorite trade payloads must expose normalized trade timing metadata usable by chart marker builders.

## Impact

- Affected frontend chart marker utilities and shared chart consumers.
- Affected favorite trade payload normalization if backend returns entry/exit date shapes inconsistently.
- No database migration expected.
- No change to strategy math unless investigation proves the duplicate signal comes from invalid trade generation.
