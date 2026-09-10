## ADDED Requirements

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
The local reviewers SHALL NOT apply fixes. The parent SHALL NOT apply fixes in its own transcript. P1/P2 SHALL be collected into one list and handed to **at most one** correction Apply child for the column, followed by **one** wave on the new interval. Remaining P1/P2 after that cycle SHALL be a visible operator block; the parent MUST NOT open a third cycle. P3 stays classified residual. Extra automatic tests MUST NOT be the Done criterion of the change that introduced this ceiling.

#### Scenario: One correction Apply then one wave
- **WHEN** either reviewer reports P1/P2
- **THEN** the parent spawns at most one Apply child with the combined list
- **AND** after that Apply returns, the parent spawns one wave in the same turn
- **AND** the parent does not re-run a single reviewer per finding as the happy path

#### Scenario: Third cycle is refused
- **WHEN** P1/P2 remain after that correction Apply and wave
- **THEN** the parent records a visible block
- **AND** MUST NOT spawn another Apply or another wave for those findings

## MODIFIED Requirements

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

### Requirement: Principal session applies reviewer findings
The local reviewers SHALL NOT apply fixes. The parent session SHALL NOT apply fixes in its own transcript. The parent SHALL classify blocking findings and, for P1/P2, spawn **at most one** correction Apply child with the combined list, then **one** wave; it MUST NOT re-run the affected reviewer per finding as the happy path. Remaining P1/P2 after that cycle stay a visible block.

#### Scenario: Blocking finding
- **WHEN** `diff-reviewer` or `code-reviewer` reports a blocking finding
- **THEN** the parent MUST collect it into the correction list (or classify it) before committing
- **AND** the reviewer MUST NOT edit the working tree
- **AND** the parent MUST NOT implement the fix in the orchestrator transcript
