## Context

Admin user management already has authenticated admin routes and UI actions for create, edit, suspend, ban, reactivate, and action logs. Deletion must fit that same route and screen instead of introducing a separate cleanup tool.

## Goals / Non-Goals

**Goals:**
- Let an admin delete a selected user from the existing Admin Users screen.
- Require an explicit reason and preserve an audit action before deletion.
- Prevent the logged-in admin from deleting their own account.
- Keep the UI compact and consistent with existing admin actions.

**Non-Goals:**
- Bulk deletion.
- Hard deletion of historical audit or trading data owned by the removed user.
- New role/permission system.

## Decisions

- Add `DELETE /api/admin/users/{user_id}` to `admin_users.py`.
  Rationale: keeps user lifecycle operations in the same API module and authorization path.

- Require a small JSON body with `reason`.
  Rationale: deletion is destructive and should have an operator explanation in the audit log.

- Write `user_deleted` to `admin_action_logs` before deleting the `users` row.
  Rationale: the deleted row will no longer be available for lookups, so the log metadata stores email/name/status evidence.

- Leave historical user-owned rows in place.
  Rationale: the current schema does not enforce foreign keys for most user-owned data, and preserving history avoids accidental data loss beyond the explicit user row deletion.

## Risks / Trade-offs

- [Risk] Deleted user-owned rows may remain orphaned. -> Mitigation: preserve them intentionally for MVP audit/history; add a separate purge/export feature if full erasure becomes required.
- [Risk] Admin deletes wrong account. -> Mitigation: require reason and a browser confirmation using the selected user's email.
