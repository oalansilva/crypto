## Context

The product is entering closed beta and already has JWT login, user status checks, and admin-managed user creation. The gap is public self-registration: the login page advertises `Criar Conta` and `/api/auth/register` creates active users for any email.

## Goals / Non-Goals

**Goals:**
- Make the default beta access posture closed.
- Preserve login for active users that already exist in `users`.
- Keep an explicit escape hatch for configured invited emails when self-registration is needed.
- Define the primary invite/access flow as admin-created users.
- Remove public account creation from the login UI.

**Non-Goals:**
- No new invite-token table or email delivery workflow in this card.
- No password reset redesign.
- No production release/archive.

## Decisions

- Use backend config instead of a new table for self-registration exceptions.
  - Decision: `BETA_PUBLIC_REGISTRATION_ENABLED` defaults to false; `BETA_INVITED_EMAILS` allows explicit self-registration for listed emails.
  - Rationale: card asks to prevent uncontrolled public access now; config is lower-risk and does not require migration.
  - Alternative considered: invite-token table. Rejected for this card because admin user creation already exists and meets beta flow needs.

- Treat admin user creation as the closed-beta invitation path.
  - Decision: admins create active users through existing `/api/admin/users`.
  - Rationale: it already records audit evidence and lets support control status, suspension, and ban.

- Remove register mode from the login screen.
  - Decision: the page is login-only for closed beta; no visible `Criar Conta` tab.
  - Rationale: UI should not advertise a public path that the backend blocks.

## Risks / Trade-offs

- [Risk] A legitimate beta tester cannot self-register unless configured.
  - Mitigation: create the user in Admin Users or add the email to `BETA_INVITED_EMAILS`.
- [Risk] Existing local tests that rely on `/auth/register` may fail under the new default.
  - Mitigation: tests that need self-registration explicitly enable `BETA_PUBLIC_REGISTRATION_ENABLED` or use admin/user fixtures.
- [Risk] Existing active users remain able to log in.
  - Mitigation: this is intentional; revoke through status `suspended`/`banned` when access must be removed.

## Migration Plan

- Deploy backend with default closed registration.
- Set `BETA_INVITED_EMAILS` only for any explicitly approved self-registration emails.
- Use Admin Users to create beta testers as the default invite/access path.
- Rollback: set `BETA_PUBLIC_REGISTRATION_ENABLED=1` if public registration must temporarily return.

## Open Questions

- None for this card. Full invite-token/email flow can be a later card if beta process needs scalable invitations.
