## ADDED Requirements

### Requirement: Automated release guard
The release workflow MUST provide a repository command that audits worktrees, branches, stashes, tracked ignored files, generated artifacts, and remote `develop`/`main` alignment.

#### Scenario: Agent audits release hygiene
- **WHEN** an agent runs the release guard in audit mode
- **THEN** the command reports detected hygiene issues without deleting or modifying repository work.

#### Scenario: Strict release gate finds hidden work
- **WHEN** an agent runs the release guard in a strict release mode and the repository has stashes, dirty worktrees, unmerged branches, or tracked ignored files
- **THEN** the command exits non-zero and lists the blocking items.

### Requirement: Remote-first release comparison
The release workflow MUST compare publication state using `origin/develop` and `origin/main` after fetching remote refs.

#### Scenario: Local main is stale
- **WHEN** local `main` differs from `origin/main`
- **THEN** the release guard uses `origin/main` for merge-state decisions and reports local `main` drift as informational or warning context.

### Requirement: Post-release cleanup gate
The release workflow MUST run a post-release guard before reporting final cleanup complete.

#### Scenario: Release merged but orphaned work remains
- **WHEN** `origin/develop` and `origin/main` are aligned but a stash, temporary worktree, unmerged branch, or tracked generated file remains
- **THEN** the post-release guard fails and requires classification or cleanup before the release is reported as clean.
