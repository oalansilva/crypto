## Why

The release guard (card #422) only inventories orphan refs in the `runtime-*/rollback-*/release-post-*/sync-*/preserve/*` namespaces; branches named `change-*/card-*/release-*` are not listed, so cleanup of previous releases (2026-08-03, mai-jul) was never executed or verified (~14 refs from terminal cards remain as debt).

## What Changes

- Extend `scripts/release-guard` post/audit to inventory local and remote branches matching `change-*/card-*/release-*` and require classification (integrated/preserved/delete with authorization) in the closeout checklist.
- Add a closeout checklist item requiring deletion of the package branches after cards move to `Pronto`.
- Keep the strict gate fail-closed: unclassified `change-*/card-*/release-*` branches are blockers in `post` mode, warnings in `audit` mode.
- Update `AGENTS.md` release hygiene section with the branch inventory/deletion requirement.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `release-worktree-hygiene`: require the release guard to inventory and classify `change-*/card-*/release-*` branches (local and remote) and require package branch deletion in closeout.

## Impact

- Affected files: `scripts/release-guard`, `AGENTS.md`, `openspec/changes/release-guard-hygiene/specs/**`.
- Affected workflow: release/lote closeout, branch cleanup verification.
- No runtime API, database, or frontend behavior changes.
