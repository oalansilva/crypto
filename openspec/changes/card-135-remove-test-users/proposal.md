## Why

The closed beta must not retain test accounts after public registration was blocked. Keeping only the two authorized Alan accounts reduces access risk before beta validation.

## What Changes

- Add an operational cleanup script for beta user access hygiene.
- Identify all current users and classify allowed vs unauthorized test accounts.
- Deactivate/ban unauthorized users instead of physically deleting rows, preserving audit/history and avoiding orphaned user-owned data.
- Record before/after evidence with counts and masked emails.
- Validate that only `o.alan.silva@gmail.com` and `o2.alan.silva@gmail.com` remain active.

## Capabilities

### New Capabilities
- `beta-user-access-hygiene`: Operational rules for cleaning unauthorized beta users while preserving evidence.

### Modified Capabilities
- `admin-user-management`: Closed-beta user lifecycle must support audit-safe cleanup of unauthorized users.
- `maintenance`: Maintenance operations must include access hygiene checks for closed beta.

## Impact

- Backend operational script under `backend/scripts`.
- Local/runtime PostgreSQL `users` table.
- Evidence captured in OpenSpec tasks and issue comment.
- No frontend/API behavior change expected.
