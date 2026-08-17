## ADDED Requirements

### Requirement: Code Review MUST run native Bugbot on the uncommitted diff versus HEAD
While `Status=Code Review` and before any implementation commit, the Cursor Agent SHALL invoke `/review-bugbot` with this exact prompt shape (no extra `Base Branch` line):

```text
Full Repository Path: <absolute worktree path>
Diff: uncommitted changes
```

The agent MUST NOT compute the git diff itself. A generic `Task` MUST NOT be the happy-path reviewer.

#### Scenario: Pre-commit Code Review
- **WHEN** a card is in `Status=Code Review` and the agent is about to commit implementation changes
- **THEN** the agent MUST run `/review-bugbot` with `Diff: uncommitted changes` and no `Base Branch` line
- **AND** it MUST wait for the subagent result before committing

#### Scenario: Generic Task is not the default reviewer
- **WHEN** `/review-bugbot` is available in the session
- **THEN** the agent MUST NOT start Code Review with a generic `generalPurpose` Task as the primary reviewer

### Requirement: Closing review MUST cover branch changes versus develop
After the implementation commit and before `Status=Done`, the agent SHALL invoke `/review-bugbot` with:

```text
Full Repository Path: <absolute worktree path>
Diff: branch changes
Base Branch: develop
```

Reuse is allowed only when that exact SHA already has this `branch changes` run. An earlier `uncommitted changes` run MUST NOT skip this requirement.

#### Scenario: Closing review versus develop
- **WHEN** the card is closing after an implementation commit
- **THEN** the agent MUST have a `/review-bugbot` result for `Diff: branch changes` and `Base Branch: develop` on the closing SHA

#### Scenario: Closing review reused
- **WHEN** the closing SHA already has a recorded `branch changes` + `Base Branch: develop` `/review-bugbot` run
- **THEN** the agent MAY reuse that result and MUST record the reuse in the Done evidence

### Requirement: Security Review MUST run on sensitive path globs
`/review-security` SHALL use the same prompt pair as Bugbot when the reviewed diff matches any of: `backend/app/api/**`, `backend/app/**/auth*`, `backend/app/**/credential*`, `backend/app/**/wallet*`, `backend/app/**/trading*`, `frontend/src/**/wallet*`, `frontend/src/**/auth*`, `**/*credentials*`, `**/.env*`.

#### Scenario: Sensitive path requires security review
- **WHEN** the reviewed diff matches one of the listed globs
- **THEN** the agent MUST also run `/review-security` with the same Diff/Base Branch pair as the Bugbot run in that stage

#### Scenario: Docs-only harness card skips security review
- **WHEN** the reviewed diff only touches `AGENTS.md`, `.cursor/`, `docs/` or `openspec/` and matches none of the sensitive globs
- **THEN** `/review-security` is not required

### Requirement: Bugbot spawn failure MUST be explicit before any generic fallback
If `/review-bugbot` fails to spawn or returns zero messages/parts, the handoff SHALL record `ERROR: subagent spawn failed/empty`. A generic Task MAY run only after that explicit error. Silent fallback is forbidden.

#### Scenario: Empty Bugbot spawn
- **WHEN** `/review-bugbot` returns 0 messages, 0 parts, missing session or a creation error
- **THEN** the Code Review stage remains incomplete until a successful native review or an explicit fallback after the error is recorded

### Requirement: Process reviewer MUST stay read-only and inherit the chat model
The versioned `.cursor/agents/code-reviewer.md` file SHALL declare `readonly: true` and `model: inherit`. During Code Review the primary session SHALL launch one `generalPurpose` Task instructed not to edit, whose prompt is that file's body plus the SHA/diff under review. It SHALL review process/contract (OpenSpec vs implementation, Design approval evidence, status non-regression). It MUST NOT duplicate Bugbot defect hunting and MUST NOT edit files.

#### Scenario: Process reviewer does not mutate
- **WHEN** the process reviewer Task runs during Code Review
- **THEN** it reports findings only
- **AND** it MUST NOT write files, commit, push or change board status

### Requirement: Principal session applies Bugbot findings
The Bugbot/Security Reviewer SHALL NOT apply fixes. The primary session SHALL fix or classify blocking findings, then re-run the native review when the uncommitted diff changed.

#### Scenario: Blocking finding
- **WHEN** `/review-bugbot` reports a blocking finding
- **THEN** the primary session MUST fix or classify it in the evidence before committing
- **AND** the reviewer MUST NOT edit the working tree

### Requirement: Done evidence MUST cite the Bugbot result
The Done evidence comment SHALL include the `/review-bugbot` outcome: findings table, `no findings`, classified residuals, or spawn-failed plus fallback.

#### Scenario: Done comment records Bugbot
- **WHEN** the card moves to `Status=Done`
- **THEN** the evidence comment MUST cite the `/review-bugbot` result for the reviewed SHA
