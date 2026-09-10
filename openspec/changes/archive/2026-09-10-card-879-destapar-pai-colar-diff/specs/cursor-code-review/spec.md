## ADDED Requirements

### Requirement: Reviewer child MUST NOT fetch the interval via git or transcripts
The versioned files `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md` SHALL remain `readonly: true` and `model: inherit`. Their bodies SHALL forbid the child from running git, from listing or Globbing `agent-transcripts` (or any agent transcript path), and from inventing the review interval by reading the working tree. The parent session SHALL materialize the interval before spawn. Grelha, Apply, and QA MUST NOT receive this diff-paste contract.

#### Scenario: Reviewer does not run git
- **WHEN** `diff-reviewer` or `code-reviewer` runs with a materialized interval in the prompt
- **THEN** the child MUST NOT invoke git
- **AND** it MUST NOT Glob or list agent transcripts
- **AND** it reports findings or `No findings.` from the supplied interval only

#### Scenario: Diff contract is Code Review only
- **WHEN** the parent spawns grill, Apply, or QA
- **THEN** those children are not required to receive `review_diff_path` or `## Diff`
- **AND** this requirement does not apply to them

### Requirement: Missing review interval MUST fail visibly and stop
If a Code Review spawn prompt contains neither a readable non-empty path after `review_diff_path:` nor non-empty bytes under a `## Diff` heading, the reviewer child SHALL print exactly `ERROR: review-diff missing` and SHALL stop. It MUST NOT continue the review by reading the repository, running git, or listing transcripts. Silent improvisation is forbidden.

#### Scenario: Spawn without interval stops
- **WHEN** `diff-reviewer` or `code-reviewer` starts without `review_diff_path` and without `## Diff` bytes
- **THEN** the child output contains `ERROR: review-diff missing`
- **AND** the review does not proceed
- **AND** the child does not read the working tree as a substitute interval

## MODIFIED Requirements

### Requirement: Code Review MUST run the versioned diff reviewer on the uncommitted diff versus HEAD
While `Status=Code Review` and before any implementation commit, the Cursor **parent** SHALL materialize the uncommitted interval versus HEAD (`git diff HEAD` plus untracked files from `git ls-files --others --exclude-standard` as new-file hunks) into `.cursor/tmp/review-diff.patch` and SHALL launch one Task with `model: inherit`, instructed not to edit, whose prompt is the body of `.cursor/agents/diff-reviewer.md` plus `review_diff_path:` pointing at that file (bytes under `## Diff` MAY also be inlined). The parent MAY spawn that reviewer as `generalPurpose` with the agent-file body **or** as named `subagent_type` `diff-reviewer`; destape matcher covers both. The spawn MUST still include `review_diff_path:` and the exact Task `description` in the awaiting sidecar. The spawn MUST be self-contained and MUST NOT inherit the Design or Apply transcript. The child MUST NOT be instructed to compute the interval with git. A generic Task without that file MUST NOT be the happy-path reviewer. `/review-bugbot` MUST NOT run. `/review-security` MAY run only when Alan explicitly asks. The reviewer output MUST be findings with severity or the exact line `No findings.`

#### Scenario: Pre-commit Code Review
- **WHEN** a card is in `Status=Code Review` and the agent is about to commit implementation changes
- **THEN** the parent MUST materialize the uncommitted diff versus HEAD before spawn
- **AND** the agent MUST run the `diff-reviewer` Task with that materialized interval in the prompt
- **AND** it MUST wait for the subagent result before committing
- **AND** the spawn prompt MUST NOT include the Design or Apply chat
- **AND** the spawn MUST NOT ask the child to run git

#### Scenario: Generic Task is not the default reviewer
- **WHEN** Code Review starts
- **THEN** the agent MUST NOT start with a generic `generalPurpose` Task that lacks the versioned `diff-reviewer` and `code-reviewer` prompts

#### Scenario: Reviewer output is findings or No findings
- **WHEN** `diff-reviewer` finishes with a materialized interval
- **THEN** the published result is findings with severity, or `No findings.`
- **AND** it MUST NOT paste Design Impeccable prose

### Requirement: Closing review MUST cover branch changes versus develop on the card branch
After the implementation commit and before `Status=QA`, the **parent** SHALL materialize `origin/<integration_branch>...HEAD` (overlay `integration_branch`, Cripto: `develop`) into `.cursor/tmp/review-diff.patch` and SHALL run the `diff-reviewer` Task with that interval in the prompt while still on the card branch. The agent MUST NOT run this comparison after squash/merge into `develop` (empty diff). The child MUST NOT compute that interval with git. Reuse is allowed only when that exact SHA already has this versus-`develop` run.

#### Scenario: Closing review versus develop
- **WHEN** the card is closing after an implementation commit
- **THEN** the parent MUST materialize `origin/develop...HEAD` before spawn
- **AND** the agent MUST have a `diff-reviewer` result for that interval on the closing SHA while still on the card branch

#### Scenario: Closing review reused
- **WHEN** the closing SHA already has a recorded `diff-reviewer` versus-`develop` run
- **THEN** the agent MAY reuse that result and MUST record the reuse in the Done evidence

### Requirement: Process reviewer MUST stay read-only and inherit the chat model
The versioned `.cursor/agents/code-reviewer.md` file SHALL declare `readonly: true` and `model: inherit`. During Code Review the primary session SHALL materialize the interval under review (uncommitted patch versus HEAD before the commit; `origin/<integration_branch>...HEAD` after it exists) and SHALL launch one Task instructed not to edit, whose prompt is that file's body plus `review_diff_path:` (and optional `## Diff` bytes). The parent MAY spawn that reviewer as `generalPurpose` with the agent-file body **or** as named `subagent_type` `code-reviewer`; destape matcher covers both. The spawn MUST still include `review_diff_path:` and the exact Task `description` in the awaiting sidecar. The spawn MUST NOT inherit the Design or Apply transcript. The child MUST NOT run git to obtain the interval. It SHALL review process/contract (OpenSpec vs implementation, Design approval evidence, status non-regression). It MUST NOT duplicate diff-reviewer defect hunting and MUST NOT edit files. It MUST NOT read `.impeccable/critique/`. The versus-`develop` comparison is owned by `diff-reviewer` after the commit and before `Status=QA`. Published output MUST be findings or `No findings.` Review constraints SHALL be in these two agent files (optional consumer `REVIEW.md` without Bugbot), not in `BUGBOT.md`.

#### Scenario: Process reviewer does not mutate
- **WHEN** the process reviewer Task runs during Code Review
- **THEN** it reports findings only
- **AND** it MUST NOT write files, commit, push or change board status
- **AND** it MUST NOT load the Impeccable snapshot

#### Scenario: Process reviewer has no parent Design chat
- **WHEN** `code-reviewer` is spawned
- **THEN** the prompt is the versioned file plus the parent-materialized interval
- **AND** it does not include the Design or Apply transcript
- **AND** it MUST NOT ask the child to run git
