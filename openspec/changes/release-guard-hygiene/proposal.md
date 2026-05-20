## Why

Release cleanup still depends on manual discipline, so stale stashes, local branch drift, tracked generated files, and orphan worktrees can survive after a release even when `develop` and `main` are already aligned.

This change adds a repeatable guard so release inventory and cleanup become a blocking check instead of a conversational checklist.

## What Changes

- Add a versioned `scripts/release-guard` command with `pre`, `post`, and `audit` modes.
- Update the release/worktree rules in `AGENTS.md` to require the guard before and after release closure.
- Extend the release-worktree hygiene spec to cover automated detection of orphaned work.
- Stop tracking generated/local-only files already covered by `.gitignore`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `release-worktree-hygiene`: require automated guard checks for release inventory, orphan work, stale stashes, tracked ignored files, and remote-first `develop`/`main` comparison.

## Impact

- Affected files: `AGENTS.md`, `scripts/release-guard`, `openspec/changes/release-guard-hygiene/**`, and Git index entries for local/generated files.
- Affected workflow: release/lote closure, worktree cleanup, branch cleanup, and post-release verification.
- No runtime API, database, or frontend behavior changes.
