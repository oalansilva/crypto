## 1. Monitor Favorite Removal

- [x] 1.1 Remove Monitor-local favorite state, localStorage helpers, and `/monitor/strategy-preferences` calls.
- [x] 1.2 Remove the `Favoritos` toolbar filter, favorite count, and row favorite action from Monitor.
- [x] 1.3 Preserve read-only tier/star display and existing operational Monitor controls.

## 2. Frontend Tests

- [x] 2.1 Update Monitor E2E tests that expected favorite filter/toggle behavior.
- [x] 2.2 Add coverage that Monitor does not expose favorite controls while still showing tier stars.

## 3. Validation

- [x] 3.1 Run OpenSpec validation for `card-134-remove-monitor-favorite-concept`.
- [x] 3.2 Run focused frontend build/test validation for affected Monitor behavior.
- [x] 3.3 Register implementation evidence before moving card #134 to `Done`.

Note: use project skills when applicable: OpenSpec skills for this change and `crypto-frontend` for Monitor UI edits and validation.
