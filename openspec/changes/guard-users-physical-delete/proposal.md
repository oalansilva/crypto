## Why

Runtime login failed because the `users` table was found empty, and local evidence shows this is a recurring failure mode. Closed-beta cleanup and admin support flows must not physically remove authentication rows in normal runtime, because that destroys access and user-owned history.

## What Changes

- Block physical `DELETE` and `TRUNCATE` operations on `public.users` in runtime PostgreSQL.
- Remove the dangerous cleanup-script mode that physically deletes unauthorized beta users.
- Keep the intended cleanup behavior: unauthorized beta users are banned/inactivated and history remains preserved.
- Change admin user deletion semantics from physical removal to a safe blocked/destructive operation policy, favoring ban/inactivation for runtime support.
- Add focused validation proving the guard blocks physical deletion and cleanup still bans users.

## Capabilities

### New Capabilities

### Modified Capabilities
- `beta-user-access-hygiene`: cleanup must never physically delete user rows in runtime.
- `admin-user-management`: admin destructive user operations must preserve user rows and audit evidence.

## Impact

- Affected code: `backend/scripts/cleanup_beta_test_users.py`, admin user-management route/tests if needed, Alembic migration.
- Affected systems: runtime PostgreSQL database `crypto_app`, user login, beta access cleanup, admin support panel.
- Operational impact: physical delete attempts fail with an explicit database error; support must ban/inactivate users instead.
