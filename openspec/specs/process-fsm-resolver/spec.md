# process-fsm-resolver Specification

## Purpose
Resolver de sessão `(q, bound_card, q_git)` a partir do worktree do path, sem GitHub. Consumido pelo Guard Write (#611).

## Requirements

### Requirement: Resolver returns session binding from the file worktree
`scripts/process-fsm/` SHALL expose a resolver that, given cwd, file path, optional issue id, and optional status, returns `q`, `q_git`, and `bound_card`. `q_git` MUST be the `git rev-parse --abbrev-ref HEAD` of the worktree that contains the **file path** (verbatim), not cwd. `q` MUST be the injected `status` argument or `None` (no GitHub in this card). `bound_card` MUST be the `card-<id>` parsed from the **path** branch, or the canonical string `⊥` when: path is not `card-<id>-*`; cwd is on a **different** `card-<id>` than path; or `issue_id` is set and differs from the path id. Cwd on `develop`/`main` with path on `card-<id>-*` SHALL bind `bound_card` to that path id.

#### Scenario: Path in another card worktree
- **WHEN** cwd is `card-605-*` and path is inside a `card-610-*` worktree
- **THEN** `bound_card` is `⊥`
- **AND** `q_git` is the path worktree branch, not cwd

#### Scenario: Session on develop editing a card worktree file
- **WHEN** cwd is `develop` and path is inside `card-610-*`
- **THEN** `bound_card` is `610`
- **AND** `q_git` is the path worktree branch

#### Scenario: develop or main
- **WHEN** the file path worktree is on `develop` or `main`
- **THEN** `q_git` is `develop` or `main`
- **AND** `bound_card` is `⊥`

#### Scenario: unbound
- **WHEN** no issue id is given and the path branch is not `card-<id>-*`
- **THEN** `bound_card` is `⊥`

#### Scenario: issue id conflicts with path card
- **WHEN** path is `card-610-*` and `issue_id` is `605`
- **THEN** `bound_card` is `⊥`

#### Scenario: git missing or detached
- **WHEN** the path is not in a git worktree or HEAD is detached
- **THEN** `q_git` is `⊥` and `bound_card` is `⊥`

### Requirement: Resolver tests do not call GitHub
Fixtures MUST cover cwd card mismatch, cwd develop + path card, `develop`/`main` path, unbound, detached, and diverging `issue_id` without `gh`, hooks, or the Project board.

#### Scenario: Pytest without GitHub
- **WHEN** `pytest scripts/process-fsm -q` runs
- **THEN** resolver fixtures execute with fake worktrees or stubs
- **AND** no network call to GitHub is made
