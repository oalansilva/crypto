## Context

The live `crypto_app.users` table was observed with zero rows, causing `POST /api/auth/login` to return `Invalid credentials` for existing accounts. A previous user-backup artifact from 2026-05-22 shows this class of failure has happened before.

The existing closed-beta cleanup spec says unauthorized accounts should be marked banned/inactive while preserving user-owned history. The implementation also exposes a `--delete` mode that runs `DELETE FROM users`, and the admin route can physically delete a selected user. Those paths create a high-impact failure mode for runtime authentication.

## Goals / Non-Goals

**Goals:**
- Make normal runtime physical deletion of `public.users` impossible.
- Keep safe access cleanup available through `status='banned'` and `is_banned=true`.
- Ensure attempted `DELETE` or `TRUNCATE` fails loudly instead of silently removing accounts.
- Preserve audit and user-owned history for future investigation or migration.

**Non-Goals:**
- Restore historical user rows without Alan deciding which old/test accounts should come back.
- Redesign the full admin support panel.
- Add a new external audit/logging dependency.

## Decisions

- Add a PostgreSQL trigger installed by Alembic to block `DELETE` and `TRUNCATE` on `public.users`.
  - Rationale: database-level protection covers scripts, app code, psql, and future accidental routines.
  - Alternative considered: only remove script delete mode. That leaves direct SQL and admin physical delete paths open.
- Remove the cleanup script's physical delete mode.
  - Rationale: the documented card #135 behavior is banning/inactivation, not deletion.
  - Alternative considered: keep `--delete` behind a confirmation env var. That still normalizes a dangerous operation in runtime.
- Treat admin deletion as unsafe while the guard is active.
  - Rationale: support can ban/suspend/reactivate; preserving rows is safer than removing identities during beta.

## Risks / Trade-offs

- [Risk] Existing admin delete endpoint will fail if used against runtime PostgreSQL. -> Mitigation: use ban/suspend/reactivate flows and update the contract/tests to reflect row preservation.
- [Risk] A future legitimate hard-delete maintenance task needs an exception. -> Mitigation: require an explicit audited migration or one-off maintenance procedure that temporarily removes the guard with a backup and Alan approval.
- [Risk] Existing old users may remain missing. -> Mitigation: keep restoration separate and curate from backups to avoid restoring QA/test accounts blindly.

## Migration Plan

1. Install the database trigger in Alembic and apply it to `crypto_app`.
2. Remove cleanup-script delete behavior and update tests.
3. Validate that `DELETE FROM users` and `TRUNCATE users` fail, while cleanup apply-ban still works.
4. Leave restore of missing historical users as a separate curated operation.
