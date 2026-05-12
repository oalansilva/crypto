## Why

Alan could not find a way to delete a user from the admin user management screen. The admin flow already supports create, edit, suspend, ban, and reactivate, but deletion is missing for cleanup cases.

## What Changes

- Add an admin-only user deletion endpoint.
- Require a deletion reason and record an admin audit action before deleting the user row.
- Block admins from deleting their own logged-in account.
- Add a delete action to the Admin Users screen with confirmation and post-delete refresh.

## Capabilities

### New Capabilities
- `admin-user-management`: Admin user management operations, including deletion.

### Modified Capabilities
- `beta-user-access-hygiene`: Admin cleanup can remove a selected user while preserving audit evidence for the action.

## Impact

- Backend API: `backend/app/routes/admin_users.py`.
- Backend tests: `backend/tests/unit/test_admin_user_management_routes.py`.
- Frontend UI: `frontend/src/pages/AdminUsersPage.tsx`.
- No database migration expected; audit action uses the existing `admin_action_logs` table.
