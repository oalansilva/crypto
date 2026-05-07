## 1. Data Source Mapping

- [x] Confirm current Favorites, Monitor, and `/combo/results` candle source paths.
- [x] Identify stale saved candle fallback behavior and protected-user constraints.

## 2. Implementation

- [x] Add Favorites analysis current-candle loading through the shared market candles endpoint.
- [x] Keep saved favorite trades/metrics untouched while replacing only chart candles.
- [x] Preserve protected common-user redaction for overlays, MA values, indicators, and parameters.
- [x] Keep saved `analysis_candles` as fallback when current candles fail or are empty.

## 3. Validation

- [x] Add/adjust E2E coverage for stale saved candles replaced by current market candles.
- [x] Run focused frontend validation.
- [x] Run OpenSpec validation for the change.
- [x] Record before/after evidence for BTC/USDT 1d latest candle alignment.
