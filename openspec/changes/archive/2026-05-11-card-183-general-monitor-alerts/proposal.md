## Why

Monitor Telegram alerts are for a general MVP group, so alert coverage cannot depend on which user triggered the scan or which strategies a user marked as liked/favorite in the UI.
Alan needs every relevant curated Monitor strategy to be eligible for shared entry/exit alerts, with exclusion handled intentionally by configuration/catalog management.

## What Changes

- Change Monitor Telegram alert scans to use the general curated Monitor catalog instead of user-scoped opportunity selection.
- Keep user Monitor preferences and liked/starred strategy preferences out of the alert source.
- Keep tier/config filtering as the intentional way to scope or exclude alertable strategies for MVP.
- Add tests proving the scan reads admin/catalog strategies even when the admin caller has no matching personal/user-selected rows.

## Capabilities

### New Capabilities
- `monitor-telegram-general-alerts`: General Monitor Telegram alerts use the curated Monitor catalog and are independent from per-user favorite/liked state.

### Modified Capabilities

## Impact

- Backend alert service: `backend/app/services/monitor_telegram_alerts.py`
- Backend opportunity source: `backend/app/services/opportunity_service.py`
- Backend tests for alert source and catalog selection.
- No frontend change expected.
