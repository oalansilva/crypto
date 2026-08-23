## MODIFIED Requirements

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
