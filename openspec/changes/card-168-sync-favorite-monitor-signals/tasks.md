## 1. Source Mapping

- [x] Confirm Favorite result markers/trades currently come from `result.trades`.
- [x] Confirm Monitor chart markers come from opportunity `signal_history`.
- [x] Confirm protected common users receive safe redacted `signal_history`.

## 2. Implementation

- [x] Fetch current Monitor opportunities when opening Favorites analysis.
- [x] Match the selected favorite to its current Monitor opportunity.
- [x] Convert Monitor `signal_history` to result trades/markers.
- [x] Use Monitor-derived trades when available and keep saved trades as fallback.
- [x] Preserve protected common-user hiding for parameters, indicators, MA overlays, and MA values.

## 3. Validation

- [x] Add E2E coverage for saved stale trades replaced by Monitor signal history.
- [x] Run focused Favorites E2E suite.
- [x] Run frontend build/lint.
- [x] Run OpenSpec validation for the change and global validation.
- [x] Record evidence for stale saved trade date versus current Monitor signal date.
