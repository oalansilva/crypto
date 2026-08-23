# cursor-code-review Specification

## Purpose
Contrato do gate `Status=Code Review` no Cripto Farol: reviewers locais versionados (`diff-reviewer` + `code-reviewer`), comparação com `develop` na branch do card, Bugbot pago opcional.

## Requirements

### Requirement: Code Review MUST run the versioned diff reviewer on the uncommitted diff versus HEAD
While `Status=Code Review` and before any implementation commit, the Cursor Agent SHALL launch one `generalPurpose` Task with `model: inherit`, instructed not to edit, whose prompt is the body of `.cursor/agents/diff-reviewer.md` plus the uncommitted diff versus HEAD. The spawn MUST be self-contained and MUST NOT inherit the Design or Apply transcript. A generic Task without that file MUST NOT be the happy-path reviewer. `/review-bugbot` MUST NOT be required. The reviewer output MUST be findings with severity or the exact line `No findings.`

#### Scenario: Pre-commit Code Review
- **WHEN** a card is in `Status=Code Review` and the agent is about to commit implementation changes
- **THEN** the agent MUST run the `diff-reviewer` Task against the uncommitted diff versus HEAD
- **AND** it MUST wait for the subagent result before committing
- **AND** the spawn prompt MUST NOT include the Design or Apply chat

#### Scenario: Generic Task is not the default reviewer
- **WHEN** Code Review starts
- **THEN** the agent MUST NOT start with a generic `generalPurpose` Task that lacks the versioned `diff-reviewer` and `code-reviewer` prompts

#### Scenario: Reviewer output is findings or No findings
- **WHEN** `diff-reviewer` finishes
- **THEN** the published result is findings with severity, or `No findings.`
- **AND** it MUST NOT paste Design Impeccable prose

### Requirement: Closing review MUST cover branch changes versus develop on the card branch
After the implementation commit and before `Status=QA`, the agent SHALL run the `diff-reviewer` Task against `origin/develop...HEAD` while still on the card branch. The agent MUST NOT run this comparison after squash/merge into `develop` (empty diff). Reuse is allowed only when that exact SHA already has this versus-`develop` run.

#### Scenario: Closing review versus develop
- **WHEN** the card is closing after an implementation commit
- **THEN** the agent MUST have a `diff-reviewer` result for `origin/develop...HEAD` on the closing SHA while still on the card branch

#### Scenario: Closing review reused
- **WHEN** the closing SHA already has a recorded `diff-reviewer` versus-`develop` run
- **THEN** the agent MAY reuse that result and MUST record the reuse in the Done evidence

### Requirement: Native Bugbot and Security Review MAY run only when Alan asks
`/review-bugbot` and `/review-security` SHALL remain optional. They MUST NOT start from path globs alone. Sensitive paths (auth, credentials, wallet, trading, API) SHALL still be reviewed by the local `diff-reviewer` using `.cursor/BUGBOT.md`.

#### Scenario: Alan requests Bugbot
- **WHEN** Alan explicitly asks for `/review-bugbot` or `/review-security` on the card
- **THEN** the agent MAY run those skills in addition to the two local reviewers
- **AND** the local reviewers remain the Code Review gate

#### Scenario: Docs-only harness card skips paid Bugbot
- **WHEN** Alan has not asked for Bugbot
- **THEN** `/review-bugbot` and `/review-security` MUST NOT run

### Requirement: Reviewer spawn failure MUST be explicit before any principal-session fallback
If either local reviewer Task fails to spawn or returns zero messages/parts, the handoff SHALL record `ERROR: subagent spawn failed/empty` after one retry. The principal session MAY complete the review itself only after that explicit error. Silent fallback is forbidden.

#### Scenario: Empty reviewer spawn
- **WHEN** a `diff-reviewer` or `code-reviewer` Task returns 0 messages, 0 parts, missing session or a creation error
- **THEN** the Code Review stage remains incomplete until a successful local review or an explicit fallback after the error is recorded

### Requirement: Process reviewer MUST stay read-only and inherit the chat model
The versioned `.cursor/agents/code-reviewer.md` file SHALL declare `readonly: true` and `model: inherit`. During Code Review the primary session SHALL launch one `generalPurpose` Task instructed not to edit, whose prompt is that file's body plus the diff under review (uncommitted patch before the commit; the committed SHA after it exists). The spawn MUST NOT inherit the Design or Apply transcript. It SHALL review process/contract (OpenSpec vs implementation, Design approval evidence, status non-regression). It MUST NOT duplicate diff-reviewer defect hunting and MUST NOT edit files. It MUST NOT read `.impeccable/critique/`. The versus-`develop` comparison is owned by `diff-reviewer` after the commit and before `Status=QA`. Published output MUST be findings or `No findings.`

#### Scenario: Process reviewer does not mutate
- **WHEN** the process reviewer Task runs during Code Review
- **THEN** it reports findings only
- **AND** it MUST NOT write files, commit, push or change board status
- **AND** it MUST NOT load the Impeccable snapshot

#### Scenario: Process reviewer has no parent Design chat
- **WHEN** `code-reviewer` is spawned
- **THEN** the prompt is the versioned file plus the diff
- **AND** it does not include the Design or Apply transcript

### Requirement: Principal session applies reviewer findings
The local reviewers SHALL NOT apply fixes. The primary session SHALL fix or classify blocking findings, then re-run the affected reviewer when the uncommitted diff changed.

#### Scenario: Blocking finding
- **WHEN** `diff-reviewer` or `code-reviewer` reports a blocking finding
- **THEN** the primary session MUST fix or classify it in the evidence before committing
- **AND** the reviewer MUST NOT edit the working tree

### Requirement: Done evidence MUST cite the local reviewers
The Done evidence comment SHALL include the `diff-reviewer` outcome (uncommitted and versus `develop`) and the `code-reviewer` outcome: findings, `no findings`, classified residuals, or spawn-failed plus fallback.

#### Scenario: Done comment records local reviewers
- **WHEN** the card moves to `Status=Done`
- **THEN** the evidence comment MUST cite both local reviewers for the reviewed SHA
- **AND** it MUST NOT require a `/review-bugbot` line unless Alan asked for that run
