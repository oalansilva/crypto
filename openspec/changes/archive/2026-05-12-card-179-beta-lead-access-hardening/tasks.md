## 1. Backend Data Model

- [x] 1.1 Add temporary-access fields to `User` model and runtime schema migration.
- [x] 1.2 Add `BetaAccessAuditLog` model and runtime schema migration/indexes.

## 2. Backend Access Flow

- [x] 2.1 Add beta lead access service that creates new users with temporary password state and does not expose the temporary password.
- [x] 2.2 Add `POST /api/leads` route and register it in FastAPI.
- [x] 2.3 Preserve existing-user credentials and record audit instead of overwriting.

## 3. Auth And Password Lifecycle

- [x] 3.1 Add `mustChangePassword` to login, refresh, and `/auth/me` responses.
- [x] 3.2 Reject expired temporary passwords at login/refresh.
- [x] 3.3 Clear temporary state after successful password change.
- [x] 3.4 Block regular authenticated APIs server-side until temporary-access users change password.

## 4. Frontend

- [x] 4.1 Persist `mustChangePassword` in auth store.
- [x] 4.2 Force authenticated users with `mustChangePassword` to `/change-password`.
- [x] 4.3 Update change-password success behavior to clear forced state.

## 5. Validation

- [x] 5.1 Add backend tests for new lead, existing user, audit, expiry, login flag, and password update cleanup.
- [x] 5.2 Run focused backend tests, OpenSpec validation, and frontend build.
