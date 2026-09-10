# cursor-code-review Specification

## Purpose
Contrato do gate `Status=Code Review` no Cripto Farol: reviewers locais versionados (`diff-reviewer` + `code-reviewer`), comparação com `develop` na branch do card, Bugbot pago opcional.
## Requirements
### Requirement: Code Review MUST run the versioned diff reviewer on the uncommitted diff versus HEAD
While `Status=Code Review` and before any implementation commit, the Cursor Agent SHALL launch one `generalPurpose` Task with `model: inherit`, instructed not to edit, whose prompt is the body of `.cursor/agents/diff-reviewer.md` plus the uncommitted diff versus HEAD, **in the same parent turn** as the `code-reviewer` Task for that interval. The spawn MUST be self-contained and MUST NOT inherit the Design or Apply transcript. A generic Task without that file MUST NOT be the happy-path reviewer. `/review-bugbot` MUST NOT run. `/review-security` MAY run only when Alan explicitly asks. The reviewer output MUST be findings with severity or the exact line `No findings.` The parent MUST NOT wait for destape of this Task before emitting the `code-reviewer` Task.

#### Scenario: Pre-commit Code Review
- **WHEN** a card is in `Status=Code Review` and the agent is about to commit implementation changes
- **THEN** the agent MUST run the `diff-reviewer` Task against the uncommitted diff versus HEAD
- **AND** it MUST emit the `code-reviewer` Task in the same parent turn
- **AND** it MUST wait for **both** subagent results before committing
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
Cursor Bugbot (`/review-bugbot`) MUST NOT run, even if asked as a product path; the Bugbot skill file MUST NOT be shipped. `/review-security` MAY run when Alan explicitly asks. They MUST NOT start from path globs alone. Sensitive paths (auth, credentials, wallet, trading, API) SHALL still be reviewed by the local `diff-reviewer` using `.cursor/agents/diff-reviewer.md` (not `BUGBOT.md`). Local `diff-reviewer` and `code-reviewer` remain the Code Review gate.

#### Scenario: Alan requests Security Review
- **WHEN** Alan explicitly asks for `/review-security` on the card
- **THEN** the agent MAY run that skill in addition to the two local reviewers
- **AND** the local reviewers remain the Code Review gate

#### Scenario: Bugbot is not a product path
- **WHEN** Alan asks for `/review-bugbot` or Code Review runs without that ask
- **THEN** `/review-bugbot` MUST NOT run
- **AND** no `BUGBOT.md` is read
- **AND** the Bugbot skill file is not shipped in the product

#### Scenario: Docs-only harness card skips paid Bugbot
- **WHEN** Alan has not asked for Bugbot
- **THEN** `/review-bugbot` MUST NOT run

### Requirement: Reviewer spawn failure MUST be explicit before any principal-session fallback
If either local reviewer Task fails to spawn or returns zero messages/parts, the handoff SHALL record `ERROR: subagent spawn failed/empty` after one retry. The principal session MAY complete the review itself only after that explicit error. Silent fallback is forbidden.

#### Scenario: Empty reviewer spawn
- **WHEN** a `diff-reviewer` or `code-reviewer` Task returns 0 messages, 0 parts, missing session or a creation error
- **THEN** the Code Review stage remains incomplete until a successful local review or an explicit fallback after the error is recorded

### Requirement: Process reviewer MUST stay read-only and inherit the chat model
The versioned `.cursor/agents/code-reviewer.md` file SHALL declare `readonly: true` and `model: inherit`. During Code Review the primary session SHALL launch one `generalPurpose` Task instructed not to edit, whose prompt is that file's body plus the diff under review (uncommitted patch before the commit; the committed SHA after it exists), **in the same parent turn** as `diff-reviewer`. The spawn MUST NOT inherit the Design or Apply transcript. It SHALL review process/contract (OpenSpec vs implementation, Design approval evidence, status non-regression). It MUST NOT duplicate diff-reviewer defect hunting and MUST NOT edit files. It MUST NOT read `.impeccable/critique/`. The versus-`develop` comparison is owned by `diff-reviewer` after the commit and before `Status=QA`. Published output MUST be findings or `No findings.` Review constraints SHALL be in these two agent files (optional consumer `REVIEW.md` without Bugbot), not in `BUGBOT.md`.

#### Scenario: Process reviewer does not mutate
- **WHEN** the process reviewer Task runs during Code Review
- **THEN** it reports findings only
- **AND** it MUST NOT write files, commit, push or change board status
- **AND** it MUST NOT load the Impeccable snapshot

#### Scenario: Process reviewer has no parent Design chat
- **WHEN** `code-reviewer` is spawned
- **THEN** the prompt is the versioned file plus the diff
- **AND** it does not include the Design or Apply transcript
- **AND** the Task is emitted in the same parent turn as `diff-reviewer`

### Requirement: Pre-commit reviewers are a same-turn wave
While `Status=Code Review` and before any implementation commit, after the parent has materialized the uncommitted interval, the parent SHALL launch `diff-reviewer` and `code-reviewer` in the **same** parent turn, both read-only, both with `review_diff_path:` (optional `## Diff` bytes). MAY spawn each as `generalPurpose` with the agent-file body **or** as named `subagent_type`. Host serialization of the two Tasks MUST NOT fail this requirement. Destape of the first MUST NOT spawn the second. Closing review versus `develop` after the commit remains **one** wave and is outside this card's pingue-pongue. This requirement MUST NOT change `process-fsm.yaml` and MUST NOT reopen destape matching (#879).

#### Scenario: Wave not series
- **WHEN** pre-commit Code Review starts
- **THEN** the parent turn includes both reviewer Tasks
- **AND** the happy path is not Apply→review→Apply→review
- **AND** both children receive the same materialized interval

#### Scenario: First destape does not skip the pair
- **WHEN** destape fires after `diff-reviewer` completes and `code-reviewer` has already been spawned in that wave
- **THEN** the parent waits for the second child
- **AND** MUST NOT commit before both have returned
- **AND** MUST NOT spawn a duplicate `code-reviewer`

### Requirement: Correction ceiling then visible block
The local reviewers SHALL NOT apply fixes. The parent SHALL NOT apply fixes in its own transcript. P1/P2 SHALL be collected into one list and handed to **at most one** correction Apply child for the column, followed by **one** wave on the new interval. Remaining P1/P2 after that cycle SHALL be a visible operator block; the parent MUST NOT open a third cycle. P0 from a reviewer classifies as a column block (not a correction-list cycle). P3 stays classified residual. Extra automatic tests MUST NOT be the Done criterion of the change that introduced this ceiling.

#### Scenario: One correction Apply then one wave
- **WHEN** either reviewer reports P1/P2
- **THEN** the parent spawns at most one Apply child with the combined list
- **AND** after that Apply returns, the parent spawns one wave in the same turn
- **AND** the parent does not re-run a single reviewer per finding as the happy path

#### Scenario: Third cycle is refused
- **WHEN** P1/P2 remain after that correction Apply and wave
- **THEN** the parent records a visible block
- **AND** MUST NOT spawn another Apply or another wave for those findings

### Requirement: Principal session applies reviewer findings
The local reviewers SHALL NOT apply fixes. The parent session SHALL NOT apply fixes in its own transcript. The parent SHALL classify blocking findings and, for P1/P2, spawn **at most one** correction Apply child with the combined list, then **one** wave; it MUST NOT re-run the affected reviewer per finding as the happy path. Remaining P1/P2 after that cycle stay a visible block. A reviewer P0 classifies as a column block.

#### Scenario: Blocking finding
- **WHEN** `diff-reviewer` or `code-reviewer` reports a blocking finding
- **THEN** the parent MUST collect it into the correction list (or classify it) before committing
- **AND** the reviewer MUST NOT edit the working tree
- **AND** the parent MUST NOT implement the fix in the orchestrator transcript

### Requirement: Done evidence MUST cite the local reviewers
The Done evidence comment SHALL include the `diff-reviewer` outcome (uncommitted and versus `develop`) and the `code-reviewer` outcome: findings, `no findings`, classified residuals, or spawn-failed plus fallback. It MUST NOT require a `/review-bugbot` line. It MAY cite `/review-security` only when Alan asked for that run.

#### Scenario: Done comment records local reviewers
- **WHEN** the card moves to `Status=Done`
- **THEN** the evidence comment MUST cite both local reviewers for the reviewed SHA
- **AND** it MUST NOT require a `/review-bugbot` line

### Requirement: dsh this-class reasoning-effort 400 MUST NOT consume the empty-spawn retry
On the dsh client, after the first this-class reasoning-effort rejection (400 / `INVALID_REQUEST` sending effort off / `none`) on an isolated Apply or reviewer **child** in the turn, the runtime root MUST NOT spawn another `subagent` / `subagent_fork` with the same preset, including the one-retry empty-spawn path from #518. The handoff SHALL record `ERROR: subagent spawn failed/empty` and the root MAY finish the step with an explicit residual. Silent fallback remains forbidden. Happy path remains: each isolated Apply and each of `diff-reviewer` and `code-reviewer` enters `turn/start`, runs at least one tool, and leaves a closing message, with zero this-class rejections on that spawn. Cursor and Grok keep the existing one-retry empty-spawn rule unchanged. This requirement MUST NOT reopen #518 / #569 as work, MUST NOT deny every `subagent`, and MUST NOT change `process-fsm.yaml`.

#### Scenario: First dead dsh reviewer does not birth the pair via retry
- **WHEN** the dsh root's first isolated Apply or reviewer child in the turn dies from this-class reasoning-effort 400
- **THEN** the root MUST NOT spawn a retry of that child or the other reviewer with the same preset
- **AND** the handoff records `ERROR: subagent spawn failed/empty`
- **AND** the root MAY complete the review itself only after that explicit residual

#### Scenario: Cursor empty-spawn retry is unchanged
- **WHEN** the client is Cursor or Grok and a reviewer Task returns 0 messages or 0 parts without this-class reasoning-effort 400
- **THEN** the existing one-retry empty-spawn rule still applies
- **AND** this requirement does not alter that path

