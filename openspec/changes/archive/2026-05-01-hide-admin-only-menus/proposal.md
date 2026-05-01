## Why

Common users currently see operational/admin navigation entries that are not part of their beta workflow. Hiding these menus reduces confusion and prevents users from entering screens meant for admin/support operation.

## What Changes

- Hide these navigation entries from non-admin users: Favorites, Combo, Backtest, Historico, Distribuicao, and Backfill.
- Keep the same entries visible for admin users.
- Preserve direct route authorization behavior; this change is scoped to menu visibility.

## Capabilities

### New Capabilities

### Modified Capabilities
- `frontend-ux`: navigation menu visibility must respect the authenticated user's admin role.

## Impact

- Frontend navigation/sidebar components.
- Existing authentication/user role state used by the frontend.
- No database migration, API contract change, or new dependency expected.
