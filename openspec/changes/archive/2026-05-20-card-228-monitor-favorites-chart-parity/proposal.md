## Why

Monitor and Favorites can still show different chart markers for the same saved favorite. This breaks trust because the card decision can say `Venda` while the Monitor chart does not match the Favorite analysis chart.

## What Changes

- Make the Monitor chart resolve its visual data from the same favorite analysis source used by Favorites whenever the opportunity maps to a saved favorite.
- Keep current Monitor signal history as fallback only when favorite analysis data is unavailable or inaccessible.
- Add regression coverage for the real reported cases where the Monitor chart must show the same sell marker source as Favorites.
- Preserve protected-strategy redaction and existing Monitor chart controls.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `chart-visualization`: Monitor charts for saved favorites must use the same canonical trade/candle source as Favorite analysis charts.
- `monitor`: The Monitor chart modal must not silently diverge from the saved favorite's analysis markers for the same favorite.

## Impact

- Frontend Monitor chart modal and tests.
- Favorite trade/candle payload consumption from `/api/favorites/{id}/trades`.
- Browser validation path for `/monitor` and `/favorites`.
