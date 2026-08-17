## ADDED Requirements

### Requirement: Pre classifies preserved and merged worktrees and local branches without GraphQL
`scripts/release-guard pre` SHALL NOT treat an extra worktree as a blocker when its branch name is listed in `PRESERVED_BRANCHES` (trim, exact match), and SHALL NOT treat a dirty worktree as a blocker when that branch is listed (warn instead). `pre` SHALL NOT emit the unmerged local-branch blocker when the branch name is listed in `PRESERVED_BRANCHES`. `pre` SHALL NOT treat a dirty worktree as a blocker when the branch is merged into `origin/develop` (`branch_merged`) and every dirty/untracked path is exactly `docs/release-${RELEASE_DATE}.md`; porcelain rename lines MUST be blockers. An extra worktree whose branch is merged into `origin/develop` SHALL be a warning to remove at closeout, not a blocker, and MUST NOT require an empty commit. `pre` MUST NOT load a Project snapshot (`item-list`) or classify preserve via board Status. Unclassified extra worktrees, unclassified unmerged local branches, and other dirty paths remain blockers. The guard remains read-only.

#### Scenario: In-flight worktree listed in PRESERVED_BRANCHES
- **WHEN** `pre` runs with an extra worktree on `card-569-code-review-bugbot`
- **AND** `PRESERVED_BRANCHES` contains `card-569-code-review-bugbot`
- **THEN** the extra worktree is not a blocker
- **AND** if that worktree is dirty, the guard emits a warning rather than a blocker
- **AND** `pre` performs zero Project `item-list` calls

#### Scenario: In-flight local branch listed in PRESERVED_BRANCHES
- **WHEN** `pre` runs and a local branch `card-569-code-review-bugbot` is not merged into `origin/develop` or `origin/main`
- **AND** `PRESERVED_BRANCHES` contains `card-569-code-review-bugbot`
- **THEN** the guard MUST NOT emit `local branch not merged...` for that branch
- **AND** `pre` performs zero Project `item-list` calls

#### Scenario: Extra worktree or local branch without classification
- **WHEN** `pre` runs with an extra worktree or unmerged local branch whose name is not in `PRESERVED_BRANCHES` and is not merged into `origin/develop`
- **THEN** the guard emits the current blocker requiring classification or merge

#### Scenario: Merged card worktree with rollout checklist only
- **WHEN** `pre` runs with a worktree whose branch is merged into `origin/develop`
- **AND** the only dirty/untracked path is `docs/release-${RELEASE_DATE}.md`
- **THEN** the worktree is not a dirty blocker
- **AND** an extra worktree in that state is a warning to remove at closeout, not a blocker

#### Scenario: Merged card worktree dirty with other files
- **WHEN** a merged-branch worktree is dirty with any path other than `docs/release-${RELEASE_DATE}.md`
- **THEN** the guard emits a dirty-worktree blocker

#### Scenario: Pre does not query the board
- **WHEN** `pre` classifies worktrees or local branches
- **THEN** it uses `PRESERVED_BRANCHES` and local git merge state only
- **AND** it MUST NOT call `ensure_board_snapshot` or Project `item-list`
