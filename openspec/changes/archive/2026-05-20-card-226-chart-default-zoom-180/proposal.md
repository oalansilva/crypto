## Why

The unified chart opens fitted to the full available history, which can make recent context too compressed when there are many candles. Alan requested the graph to open by default focused on 180 candles.

## What Changes

- Set the shared strategy chart surface initial visible range to 180 candles when enough data exists.
- Keep the same behavior for Favorites and Monitor because both use the shared chart surface.
- Preserve zoom in, zoom out, reset and mouse-wheel zoom behavior.
- Add shared Favorites-style metrics and trade list information to the Monitor chart modal when favorite trade data is available.
- Reuse the same trade table component in the Favorites result page so both graph flows render the same trade details.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `chart-visualization`: Strategy chart surfaces open with a default 180-candle visible range when candle history has at least 180 bars, and Monitor/Favorites graph details share the Favorites-style metrics/trade list component when data is available.

## Impact

- Shared frontend chart components.
- Monitor chart modal.
- Focused chart E2E coverage.
