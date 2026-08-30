## ADDED Requirements

### Requirement: Parent closes Done in the same turn as green QA
While `Status=Code Review` or `Status=QA` and the card is bound to `card-<id>-*`, the Cursor **parent** SHALL require a pull request from `q_git` into `develop` before `process_event aceitar_sha`. Without that PR, `aceitar_sha` MUST be treated as reject `no_pr` and the parent MUST open the PR in the same turn and retry `aceitar_sha`. The parent MUST NOT treat local unit tests or `openspec validate` as Done. After `aceitar_sha` moves QA, the parent MAY spawn one isolated QA child that reads checks and MUST NOT call `process_event`. When that child returns green, or when the parent itself sees `qa-gate` success, the parent MUST call `process_event integrar_develop` in the **same turn**. A reject `qa-gate pending` MUST wait for the check and retry `integrar_develop` in that turn. A reject `sync: dirty` or `no_pr` is visible and is not the end of the turn by itself. The Agent MUST NOT `gh project item-edit` Status to QA or Done.

#### Scenario: T11 without PR is retried after opening the PR
- **WHEN** the parent is in Code Review, reviewers are accepted, and no PR from `q_git` into `develop` exists
- **THEN** `process_event aceitar_sha` rejects with `reason=no_pr`
- **AND** the parent opens the PR and retries `aceitar_sha` in the same turn
- **AND** Status is not moved via `item-edit`

#### Scenario: Green QA child is followed by T14 in the same turn
- **WHEN** the card is in QA, the QA child reports `qa-gate` success, and the canonical source is clean
- **THEN** the parent calls `process_event integrar_develop` in that turn
- **AND** the QA child does not call `process_event`

#### Scenario: Pending qa-gate retries T14
- **WHEN** `integrar_develop` returns `reason=qa-gate pending`
- **THEN** the parent waits for the check and retries `integrar_develop` in the same turn
- **AND** it does not treat the first reject as the end of the turn
