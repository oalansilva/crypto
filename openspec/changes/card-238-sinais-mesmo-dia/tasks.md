## 1. Marker Utility

- [x] 1.1 Add shared frontend trade-to-marker utility for direction-aware Portuguese labels.
- [x] 1.2 Normalize same displayed candle entry/exit pairs into one combined marker.

## 2. Chart Integration

- [x] 2.1 Use the shared marker utility in Favorites/Combo result charts.
- [x] 2.2 Use the shared marker utility in Monitor chart modal.

## 3. Validation

- [x] 3.1 Add focused tests for same-candle marker behavior.
- [x] 3.2 Run OpenSpec, frontend test/build, and focused runtime validation.

## 4. Follow-up Persisting Bug

- [x] 4.1 Collapse opposite markers from different trades that resolve to the same displayed candle.
- [x] 4.2 Prevent the Monitor current-signal fallback from re-adding a Compra/Venda marker already covered by a same-candle combined marker.
- [x] 4.3 Re-run focused Playwright/build/OpenSpec validation and reintegrate in develop.

Note: use project skills when applicable; OpenSpec skills used for new, fast-forward, apply, and verify phases.
