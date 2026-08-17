# Cripto Farol — two-path workspace rule

## Durable rule

Cripto Farol must be operated locally with only two canonical source paths:

- DEV: `/srv/apps/dev/criptofarol/source`
- PROD: `/srv/apps/prod/criptofarol/source`

Do not recreate or use `/root/crypto` as a clone, social archive, implementation workspace, planning workspace, or temporary holding area.

## When temporary work appears elsewhere

1. Stop before continuing implementation.
2. Inventory the temporary path with Git status, untracked files, branch, remote, and relevant diffs.
3. Move/preserve anything that cannot be lost into the correct canonical path:
   - DEV by default.
   - PROD only for explicit production/release work.
4. Verify preservation before deletion:
   - compare file counts for the migrated tree;
   - compare checksums when possible;
   - confirm the canonical Git status shows the expected new files.
5. Delete the temporary path only after explicit Alan authorization. Verification (counts/checksums/Git) is required, but is not itself authorization to delete.
6. Commit the preserved content in DEV using the normal card/branch/Code Review/Done technical workflow.

## Git workflow pattern used successfully

- Create a GitHub issue/card for the cleanup/migration.
- Add it to Project 1.
- Move `Status=Em desenvolvimento`.
- Create a branch from DEV source, e.g. `card-<id>-migrar-materiais-sociais-dev`.
- Stage only the preserved materials and documentation.
- Run a review focused on:
  - secrets/tokens;
  - accidental `.hermes/` workspace files;
  - wrong path usage;
  - oversized files above GitHub hard limits;
  - unintended runtime changes.
- Commit and fast-forward merge into `develop`.
- Push `develop` and the branch.
- Comment evidence on the issue and move to `Done` technical.

## Important distinction

This is not a production release. After DEV preservation/integration, PROD remains untouched until Alan explicitly asks for release/publication.