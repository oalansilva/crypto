## Why

Telegram alert eligibility needs an explicit admin control. Reusing tier/star classification for alert routing is confusing because tier is a product ranking signal, while Telegram notification is an operational publication decision.

## What Changes

- Add a boolean `notify_telegram` flag to `favorite_strategies`.
- Expose `notify_telegram` through Favorites create/list/update responses.
- Let admins toggle `Notificar Telegram` in the Favorites screen.
- Make Monitor Telegram scans evaluate only catalog strategies with `notify_telegram=true`.
- Keep tier/star classification unchanged and separate from Telegram routing.

## Capabilities

### New Capabilities
- `monitor-telegram-favorite-toggle`: Admins can control whether each catalog favorite is eligible for Monitor Telegram alerts.

### Modified Capabilities

## Impact

- Backend model/schema/database startup migration for `favorite_strategies.notify_telegram`.
- Favorites API patch permissions and payloads.
- Monitor Telegram alert catalog filtering.
- Favorites UI table/mobile controls.
- Backend unit/integration tests and frontend build.
