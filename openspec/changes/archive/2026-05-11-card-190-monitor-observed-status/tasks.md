## 1. Data Model

- [x] 1.1 Add `MonitorObservedStatus` model and runtime migration table/indexes.
- [x] 1.2 Add helper functions to read and upsert observed status by `symbol + timeframe`.

## 2. Alert Logic

- [x] 2.1 Use observed previous status in `build_monitor_alert_candidate`.
- [x] 2.2 Suppress alerts when current status equals latest observed status.
- [x] 2.3 Persist observed status for sendable and non-sendable scan results.

## 3. Validation

- [x] 3.1 Add unit tests for first observation, unchanged suppression, silent-to-sendable transition, and non-sendable update.
- [x] 3.2 Run focused backend tests, Black check, and OpenSpec validation.
