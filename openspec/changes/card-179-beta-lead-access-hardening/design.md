## Context

The app already blocks public self-registration by default and supports active beta users through `/api/auth/login`. The landing prototype posts to `/api/leads`, but no native FastAPI route exists in this repo. Card #179 hardens the product-side contract so automatic lead access has a temporary-password lifecycle instead of becoming a permanent unmanaged password.

## Decisions

### D1: Store lifecycle flags on `users`

Add these nullable/defaulted fields:

- `must_change_password`: true for temporary access.
- `temporary_password_expires_at`: UTC expiry for the initial temporary password.
- `temporary_password_used_at`: set when the user successfully changes away from the temporary password.
- `password_changed_at`: support/audit timestamp for password updates.
- `access_invitation_source`: e.g. `landing`.
- `access_invitation_created_at`: when the automatic access was created.

This keeps login and profile updates simple and avoids a separate token table for the MVP.

### D2: Add a minimal audit table

Create `beta_access_audit_logs` with email, optional user id, action, result, source, metadata, and timestamp. This records whether access was created or skipped for an existing user without storing password material.

### D3: Native `POST /api/leads` creates access but never returns the temporary password

For a new email, the backend generates a random temporary password, stores only the hash, marks `must_change_password=true`, records audit, and sends the welcome email through the existing Clara/Gmail `gog gmail send` channel by default. SMTP remains an explicit fallback via `BETA_ACCESS_EMAIL_PROVIDER=smtp`. The API response returns neutral status metadata only.

For an existing email, the backend records audit and does not overwrite password or temporary-access state.

### D4: Login allows temporary password before expiry, then forces change through response flag

Login still requires valid password. If `must_change_password=true` and the temporary password is expired, login is rejected. If valid and not expired, login succeeds with `mustChangePassword=true`, and the frontend restricts navigation to `/change-password`.

### D5: Password change clears temporary state

`PUT /api/users/password` continues to require the current password. When the update succeeds, it clears `must_change_password`, clears expiry, and records `temporary_password_used_at`/`password_changed_at`.

## Risks

- The existing VPS lead capture may still be external. This change adds the product-native contract and route, but deployment routing must point `/api/leads` to the FastAPI backend for this implementation to own the live flow.
- The existing Gmail channel requires the same `gog` environment/keyring used by the landing service. The backend loads `/root/.openclaw/workspace/cripto-farol-landing/.env.leads` by default for that subprocess and must not return or log the temporary password as a fallback.

## Validation

- Unit tests for service/auth/migration behavior.
- Integration tests for lead endpoint and forced password-change flow.
- Frontend build after auth-store and routing changes.
