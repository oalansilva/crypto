## Context

Card #135 asks to remove test user registrations and leave only `o.alan.silva@gmail.com` and `o2.alan.silva@gmail.com`. The system has user-owned data and admin audit logs, so physical deletion can break history or create orphaned data.

## Goals / Non-Goals

**Goals:**
- Make unauthorized beta accounts unable to access the app.
- Preserve history and auditability.
- Provide dry-run and apply modes.
- Capture before/after evidence without leaking sensitive user data.

**Non-Goals:**
- No production release.
- No physical cascading delete in this card.
- No new admin UI.

## Decisions

- Use logical cleanup (`status='banned'`, `is_banned=true`, notes) instead of deleting users.
  - Rationale: preserves records and avoids data-loss risk.
  - Alternative: delete rows. Rejected because dependent data may exist.

- Make allowed users configurable in script but default to Alan's two accounts.
  - Rationale: keeps the operation repeatable and explicit.

- Script emits masked-email evidence and counts.
  - Rationale: useful for card evidence without exposing full account list.

## Risks / Trade-offs

- [Risk] Unauthorized user rows remain in DB.
  - Mitigation: access is blocked by auth middleware and login route for `banned` users.
- [Risk] Allowed users may not exist in target DB.
  - Mitigation: script reports allowed missing as warning; it does not create users.
- [Risk] Wrong DB target.
  - Mitigation: script refuses non-PostgreSQL URLs and prints DB host/database before apply.

## Migration Plan

- Run script in dry-run mode.
- Review masked before evidence.
- Run script with `--apply`.
- Re-run dry-run/list checks.
- Keep the script for repeatable hygiene.
