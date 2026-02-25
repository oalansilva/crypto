## Why

Monitor currently presents multiple views/tabs that overlap in filters and asset scope. Alan wants a single, unified mobile-first experience.

Additionally, Alan wants per-symbol timeframe selection (for Price mode) and for that preference to be persisted in the backend.

## What Changes

- Unify Monitor into a **single cards-based view** (remove separate Status/Dashboard tabs).
- Each symbol card supports:
  - a per-card toggle between **Price** and **Strategy** content
  - a per-card timeframe selector (visible in Price mode)
- Persist per-symbol preferences in the backend:
  - `in_portfolio` (existing)
  - `card_mode` (existing)
  - `price_timeframe` (new)

Default behaviors:
- Monitor defaults to filter = **In Portfolio**.
- Symbols without saved preferences appear only under **All**.
- Default `card_mode` = **price**.
- Default `price_timeframe` = **1d**.

Timeframe constraints:
- Crypto: 15m / 1h / 4h / 1d
- Stocks: 1d only (for now)

## Capabilities

### New Capabilities
- `monitor-card-timeframe-pref`: Persist per-symbol price timeframe preference.

### Modified Capabilities
- `frontend-ux`: Simplify Monitor into a single cards view and add per-card timeframe UI.
- `backend`: Extend monitor preferences schema + API to support `price_timeframe`.

## Impact

- Backend: add `price_timeframe` to monitor preferences table and API.
- Frontend: remove monitor tabs; add per-card timeframe selector.
- Tests: backend integration tests for new preference field; Playwright E2E for persistence.
