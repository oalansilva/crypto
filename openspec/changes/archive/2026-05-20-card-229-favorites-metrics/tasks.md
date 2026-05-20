## 1. Investigation

- [x] 1.1 Map Favorites metric sources from optimization save payload to `/api/favorites/` response and `/favorites` rendering.
- [x] 1.2 Identify any duplicate fraction-to-percent conversion for return metrics.

## 2. Implementation

- [x] 2.1 Correct the optimization save path so backend percentage-point fields are not multiplied by 100.
- [x] 2.2 Keep Favorites display formatting coherent for percentage-point and ratio fields.

## 3. Verification

- [x] 3.1 Add or update focused Playwright coverage for Favorites percentage rendering.
- [x] 3.2 Run focused tests/build and validate OpenSpec for `card-229-favorites-metrics`.

Note: use project frontend/test/debugging skills when applicable.
