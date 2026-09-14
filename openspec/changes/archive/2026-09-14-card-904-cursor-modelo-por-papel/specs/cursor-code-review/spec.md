## MODIFIED Requirements

### Requirement: Code Review MUST run the versioned diff reviewer on the uncommitted diff versus HEAD
While `Status=Code Review` and before any implementation commit, the Cursor **parent** SHALL materialize the uncommitted interval versus HEAD (`git diff HEAD` plus untracked files from `git ls-files --others --exclude-standard` as new-file hunks) into `.cursor/tmp/review-diff.patch` and SHALL launch one Task with `model: composer-2.5`, instructed not to edit, whose prompt is the body of `.cursor/agents/diff-reviewer.md` plus `review_diff_path:` pointing at that file (bytes under `## Diff` MAY also be inlined). The parent MAY spawn that reviewer as `generalPurpose` with the agent-file body **or** as named `subagent_type` `diff-reviewer`; destape matcher covers both. The spawn MUST still include `review_diff_path:` and the exact Task `description` in the awaiting sidecar. The spawn MUST be self-contained and MUST NOT inherit the Design or Apply transcript. The spawn MUST NOT inherit the parent picker. The child MUST NOT be instructed to compute the interval with git. A generic Task without that file MUST NOT be the happy-path reviewer. `/review-bugbot` MUST NOT run. `/review-security` MAY run only when Alan explicitly asks. The reviewer output MUST be findings with severity or the exact line `No findings.`

#### Scenario: Pre-commit Code Review
- **WHEN** a card is in `Status=Code Review` and the agent is about to commit implementation changes
- **THEN** the parent MUST materialize the uncommitted diff versus HEAD before spawn
- **AND** the agent MUST run the `diff-reviewer` Task with that materialized interval in the prompt
- **AND** that Task `model` is `composer-2.5`
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

### Requirement: Process reviewer MUST stay read-only and use Composer execução model
The versioned `.cursor/agents/code-reviewer.md` file SHALL declare `readonly: true` and `model: composer-2.5` (redundant pin). During Code Review the primary session SHALL materialize the interval under review (uncommitted patch versus HEAD before the commit; `origin/<integration_branch>...HEAD` after it exists) and SHALL launch one Task with `model: composer-2.5` instructed not to edit, whose prompt is that file's body plus `review_diff_path:` (and optional `## Diff` bytes). The parent MAY spawn that reviewer as `generalPurpose` with the agent-file body **or** as named `subagent_type` `code-reviewer`; destape matcher covers both. The spawn MUST still include `review_diff_path:` and the exact Task `description` in the awaiting sidecar. The spawn MUST NOT inherit the Design or Apply transcript. The spawn MUST NOT inherit the parent picker and MUST NOT use Grok or `composer-2.5-fast`. The child MUST NOT run git to obtain the interval. It SHALL review process/contract (OpenSpec vs implementation, Design approval evidence, status non-regression). It MUST NOT duplicate diff-reviewer defect hunting and MUST NOT edit files. It MUST NOT read `.impeccable/critique/`. The versus-`develop` comparison is owned by `diff-reviewer` after the commit and before `Status=QA`. Published output MUST be findings or `No findings.` Review constraints SHALL be in these two agent files (optional consumer `REVIEW.md` without Bugbot), not in `BUGBOT.md`. The law is the Task `model` parameter on both spawn paths.

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
- **AND** the Task `model` is `composer-2.5`

### Requirement: Reviewer child MUST NOT fetch the interval via git or transcripts
The versioned files `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md` SHALL remain `readonly: true` and SHALL declare `model: composer-2.5` instead of `inherit`. Their bodies SHALL forbid the child from running git, from listing or Globbing `agent-transcripts` (or any agent transcript path), and from inventing the review interval by reading the working tree. The parent session SHALL materialize the interval before spawn and SHALL pass `model: composer-2.5` on both spawn paths. Grelha, Apply, and QA MUST NOT receive this diff-paste contract.

#### Scenario: Reviewer does not run git
- **WHEN** `diff-reviewer` or `code-reviewer` runs with a materialized interval in the prompt
- **THEN** the child MUST NOT invoke git
- **AND** it MUST NOT Glob or list agent transcripts
- **AND** it reports findings or `No findings.` from the supplied interval only

#### Scenario: Diff contract is Code Review only
- **WHEN** the parent spawns grill, Apply, or QA
- **THEN** those children are not required to receive `review_diff_path` or `## Diff`
- **AND** this requirement does not apply to them

#### Scenario: Agent header pins role model not inherit
- **WHEN** the two agent files are read
- **THEN** each declares `readonly: true`
- **AND** each declares `model: composer-2.5`
- **AND** neither declares `model: inherit`
