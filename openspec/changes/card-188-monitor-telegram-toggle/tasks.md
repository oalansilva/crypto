## 1. Backend Data And API

- [x] 1.1 Add `notify_telegram` to the favorite strategy model, schema and startup migration.
- [x] 1.2 Allow owner/admin updates of `notify_telegram` while blocking common-user updates on admin catalog rows.

## 2. Alert Filtering

- [x] 2.1 Filter Monitor Telegram catalog scans to favorites with `notify_telegram=true`.
- [x] 2.2 Preserve existing tier, dedupe, rate limit, allowlist, audit and dry-run behavior.

## 3. Favorites UI

- [x] 3.1 Add admin-only `Notificar Telegram` control in the Favorites table/mobile card.
- [x] 3.2 Keep the UI compact and consistent with existing Favorites controls.

## 4. Validation

- [x] 4.1 Add/update backend tests for the API field and alert filtering.
- [x] 4.2 Run focused backend tests, OpenSpec validation and frontend build.

Note: Use project skills when applicable for OpenSpec, frontend, tests and debugging.
