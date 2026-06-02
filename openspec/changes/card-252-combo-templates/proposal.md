## Why

The Combo selection screen currently reports `0 strategies stored in database` even when runtime PostgreSQL contains valid strategy templates. This blocks users from selecting stored templates, running backtests, and saving favorites without recreating strategies manually.

## What Changes

- Ensure the Combo template endpoint used by `/combo/select` returns valid templates from the runtime PostgreSQL `combo_templates` table.
- Repopulate the runtime `combo_templates` table from the versioned export when it is empty.
- Preserve the existing `prebuilt`, `examples`, and `custom` response shape expected by the UI.
- Add focused regression coverage for the template listing behavior when runtime rows exist.
- Validate the fix through PostgreSQL-backed API evidence and the served Combo UI/DOM.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `database-strategy-config`: `/api/combos/templates` must return the stored runtime combo templates with display metadata whenever valid rows exist in PostgreSQL.

## Impact

- Backend: combo template listing service/route and tests.
- Frontend: Combo selection screen verification only unless implementation shows a UI-side bug.
- Runtime: PostgreSQL `combo_templates`; no SQLite operational path.
