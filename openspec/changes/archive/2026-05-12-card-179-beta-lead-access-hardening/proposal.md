## Why

The landing access flow can create beta users automatically, but the current product contract does not formally track temporary access, expiry, first-login password change, or invite audit evidence. This leaves beta access dependent on operational convention instead of enforceable app behavior.

## What Changes

- Add first-access password hardening for beta users created from landing leads.
- Add temporary password expiry and mandatory password change flags on user records.
- Add a native `POST /api/leads` backend path that creates access for new leads without exposing temporary passwords in API responses or logs.
- Preserve existing users without overwriting their passwords.
- Record minimal audit events for lead access creation or existing-user detection.
- Extend auth responses with `mustChangePassword` so the frontend can force the user to `/change-password`.
- Clear the temporary-password state only after a successful password update.

## Capabilities

### New Capabilities
- `beta-lead-access-hardening`: Secure automatic beta access created from landing leads, including temporary password lifecycle and audit events.

### Modified Capabilities
- `closed-beta-access-control`: Active beta authentication now exposes and respects required password-change state for temporary access.

## Impact

- Backend models and startup schema migrations for user temporary-access fields and audit table.
- Backend auth routes, user password route, and a new leads route.
- Frontend auth store, protected layout, and change password behavior.
- Unit/integration tests for lead creation, existing users, expiry, login flag, and password-change cleanup.
