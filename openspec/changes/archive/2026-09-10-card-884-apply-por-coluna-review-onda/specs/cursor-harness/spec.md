## ADDED Requirements

### Requirement: One Apply child per Em desenvolvimento column until done or visible P0
On first entry to `Status=Em desenvolvimento` (after `iniciar_apply`) the Cursor parent SHALL spawn **one** Apply-column child. That child SHALL loop tasks internally until every task is done or a visible P0 blocks the column. It MUST NOT return control to the parent between tasks. The parent MUST NOT spawn one Apply child per task. If the Apply child returns with remaining tasks and no visible P0, the parent MUST emit a visible block to the operator and MUST NOT open Code Review and MUST NOT spawn a second Apply. Nested spawn remains forbidden: the Apply child MUST NOT spawn reviewers. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry. Automatic tests added by this change MUST NOT be the Done criterion.

#### Scenario: Single Apply child finishes the column
- **WHEN** Em desenvolvimento starts with `Status=Pronto para Dev`
- **THEN** the parent spawns one Apply child
- **AND** that child keeps per-task sliced reads inside itself until all tasks are done or a P0 is visible
- **AND** the parent does not spawn another Apply for the next task

#### Scenario: Early Apply return is a visible block
- **WHEN** the Apply child returns with remaining tasks and no visible P0
- **THEN** the parent MUST NOT treat destape as license to start Code Review
- **AND** the parent MUST NOT spawn a second Apply
- **AND** the operator-facing chat shows a visible block

### Requirement: Code Review wave is two Tasks in the same parent turn
While `Status=Code Review`, after the parent has materialized the interval, the parent SHALL emit **two** Task invocations in the **same** assistant turn: `diff-reviewer` and `code-reviewer`, both with `review_diff_path:` for that interval. The clock that counts is the slower child. Host queueing of those Tasks MUST NOT fail this requirement. Destape of the first reviewer MUST NOT birth the second (already spawned) and MUST NOT skip it. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry and MUST NOT reopen destape matching (#879).

#### Scenario: Both reviewers born in one parent turn
- **WHEN** Code Review starts and the interval is already materialized
- **THEN** the parent message that spawns review contains both `diff-reviewer` and `code-reviewer` Tasks
- **AND** both prompts point at the same parent-materialized interval
- **AND** the parent does not wait for destape of the first before spawning the second

#### Scenario: Host queue does not fail the wave
- **WHEN** the host runs those two Tasks one after another instead of overlapping
- **THEN** the wave still satisfies this requirement
- **AND** the session MUST NOT treat that queue as a card failure

### Requirement: At most one correction Apply then one wave then visible block
P1/P2 findings from a Code Review wave SHALL return to the parent as **one** list. The parent MAY spawn **at most one** correction Apply child for that column, whose prompt contains the whole list, then **one** wave on the updated interval. The parent MUST NOT spawn one Apply per finding. After that correction Apply + wave, remaining P1/P2 SHALL stay a visible operator block; the parent MUST NOT open a third Apply+review cycle. Closing review after the implementation commit remains **one** wave and is not this pingue-pongue. The parent MUST NOT fix findings in its own transcript. This requirement MUST NOT add a FSM column or event.

#### Scenario: Correction is one Apply with the list
- **WHEN** a Code Review wave returns P1/P2 findings
- **THEN** the parent spawns at most one Apply child whose prompt is the full list
- **AND** after that child returns, the parent spawns one wave in the same turn
- **AND** the parent does not spawn one Apply per finding

#### Scenario: Residual P1/P2 after one correction cycle blocks visibly
- **WHEN** the correction Apply and the following wave still leave P1/P2 open
- **THEN** the parent MUST NOT spawn another Apply or another wave for those findings
- **AND** the operator-facing chat records a visible block
- **AND** Status is not moved by inventing a third column

## MODIFIED Requirements

### Requirement: Activity children do not inherit parent transcript
Grill, Design-author, Apply-column, QA, Assessment A/B, `diff-reviewer`, and `code-reviewer` SHALL receive a self-contained prompt and MUST NOT inherit the parent transcript. Apply-column SHALL keep per-task sliced reads **inside** that child and SHALL NOT yield to the parent between tasks except when all tasks are done or a visible P0 blocks the column. Grill MUST bind on `Status=Em Refinamento` plus issue id in the prompt, not on git branch `card-<id>-*`. Nested spawn is forbidden (Design child MUST NOT spawn A/B; Apply child MUST NOT spawn reviewers). The Apply child's self-contained prompt SHALL state it is the sole Apply child of the column. The Code Review spawn prompt SHALL state both reviewers are born in the same parent turn over the pasted interval.

#### Scenario: Apply column child slices internally
- **WHEN** Em desenvolvimento starts with `Status=Pronto para Dev`
- **THEN** the parent spawns one Apply child
- **AND** that child loads one task + matching spec + short `design.md` apply sections per task
- **AND** the parent does not implement product code
- **AND** the Apply child MUST NOT run `process_event`, commit, push, or spawn reviewers
- **AND** it returns task status only when all tasks are done or a P0 is visible, so the parent can git + `pedir_review` and spawn the review wave in the same turn

#### Scenario: Grill child binds without a card branch
- **WHEN** Alan asks to grill and Project Status is `Em Refinamento`
- **THEN** the parent spawns `grill-card` with the issue id in the prompt even if `q_git` is `develop`
- **AND** the child writes the issue body
- **AND** the parent does not write the issue body itself
