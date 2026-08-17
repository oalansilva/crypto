## Why

~33 OpenSpec changes (card-210..242, fix-*, monitor-*, release-guard-hygiene, etc., from apr-jul 2026) have all 4 artifacts done and belong to cards already in terminal states (`Pronto`/`Cancelado`), but they are still active in `openspec/changes/`. This is a hygiene failure of the archive step and it keeps `openspec validate --all` scope polluted with finished work.

## What Changes

- Run `/opsx:bulk-archive` (via `openspec archive` per change) over the completed changes belonging to terminal cards, moving them to `openspec/changes/archive/YYYY-MM-DD-<change>/` and syncing delta specs where applicable.
- Add a check in `scripts/release-guard` post/audit that detects OpenSpec changes with 4/4 artifacts done whose linked card is terminal (`Pronto`/`Cancelado`) but that are still active; report as warn in audit and blocker in post (or warn with explicit justification, per design).
- Ensure `openspec validate --all` stays green after the archive run.
- Document the "change completa de card terminal ainda ativa" rule in `AGENTS.md`/guard usage.

## Capabilities

### New Capabilities

- `openspec-archive-hygiene`: detect and enforce archiving of completed OpenSpec changes linked to terminal cards.

### Modified Capabilities

- `release-worktree-hygiene`: release guard checks for active OpenSpec changes of terminal cards with all artifacts done.

## Impact

- Affected files: `openspec/changes/` (archive moves), `openspec/changes/archive/**`, `scripts/release-guard`, `AGENTS.md`.
- Affected workflow: OpenSpec archive, release guard post/audit, `openspec validate --all`.
- No runtime API, database, or frontend behavior changes.
