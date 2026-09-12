## ADDED Requirements

### Requirement: Wave findings are classified mechanical versus judgment
Each finding from a Code Review wave SHALL be classified by the Cursor parent as **mechanical** or **judgment** before any correction spawn. Mechanical means an obvious file/line/instruction fix whose severity is below architecture, product, or acceptance of the bound card. Judgment means the finding would change design, change acceptance, or is robustness outside the card. Mechanical findings from that wave SHALL go together to the single correction Apply. Judgment findings SHALL go straight to residual and MUST NOT occupy the correction slot. A reviewer P0 remains a column block and MUST NOT enter the correction list. P3 remains classified residual. This requirement MUST NOT add a FSM column or event and MUST NOT reopen #884 spawn-per-task or #879 destape matching.

#### Scenario: Mechanical findings occupy the one correction Apply without Ask
- **WHEN** a Code Review wave returns P1 findings that are mechanical
- **THEN** the parent spawns at most one correction Apply whose prompt is those mechanical items together
- **AND** the parent MUST NOT ask the operator to authorize that Apply
- **AND** judgment findings from the same wave are not in that prompt

#### Scenario: Judgment skips the correction slot
- **WHEN** a Code Review wave returns a judgment finding
- **THEN** that finding is recorded as residual
- **AND** the parent MUST NOT spend the correction Apply slot on it
- **AND** the parent MUST NOT ask whether to treat it as a correction

### Requirement: Deterministic QA failure stays out of the judgment-review wave
A deterministic `qa-gate` failure caused by test inventory, formatting (Black), or a new-file skip SHALL be handled as Apply/QA backpressure until the check is green or the correction ceiling is already consumed. The parent MUST NOT reopen a judgment-review wave (`diff-reviewer` + `code-reviewer` as product/acceptance review) for that signal. Closing review versus `develop` after the implementation commit remains **one** wave and is not this judgment wave. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry.

#### Scenario: Inventory or formatting failure does not spawn judgment review
- **WHEN** QA fails because of test inventory, formatting, or a new-file skip
- **THEN** the parent keeps the fix in Apply or QA until green or the ceiling
- **AND** the parent MUST NOT spawn a new judgment-review wave for that failure
- **AND** the parent MUST NOT ask the operator to authorize a review cycle for that signal

#### Scenario: Post-commit closing wave is unchanged
- **WHEN** the implementation commit exists and closing review versus `develop` is due
- **THEN** that closing wave still runs once
- **AND** this requirement does not treat that wave as a judgment reopen of inventory/Black/skip

## MODIFIED Requirements

### Requirement: At most one correction Apply then one wave then visible block
P1/P2 findings from a Code Review wave SHALL return to the parent as **one** list after classification. The parent MAY spawn **at most one** correction Apply child for that column, whose prompt contains the **mechanical** items of the list, then **one** wave on the updated interval. The parent MUST NOT spawn one Apply per finding. The parent MUST NOT ask the operator to authorize an extra Apply or to accept residual. After that correction Apply + wave, remaining P1/P2 **or a new P1** SHALL be residual on the Done handoff **and** the card issue comment; the card SHALL continue (commit, PR, QA). The parent MUST NOT open a third Apply+review cycle. Closing review after the implementation commit remains **one** wave and is not this pingue-pongue. The parent MUST NOT fix findings in its own transcript. This requirement MUST NOT add a FSM column or event. Extra automatic tests MUST NOT be the Done criterion of the change that introduced this silent ceiling.

#### Scenario: Correction is one Apply with the list
- **WHEN** a Code Review wave returns mechanical P1/P2 findings
- **THEN** the parent spawns at most one Apply child whose prompt is the mechanical list
- **AND** after that child returns, the parent spawns one wave in the same turn
- **AND** the parent does not spawn one Apply per finding
- **AND** the parent MUST NOT ask to authorize that correction

#### Scenario: Residual P1/P2 after one correction cycle follows to Done
- **WHEN** the correction Apply and the following wave still leave P1/P2 open, or that wave reports a new P1
- **THEN** the parent MUST NOT spawn another Apply or another wave for those findings
- **AND** the parent MUST NOT ask «autorizar extra / aceitar residual»
- **AND** the residual is recorded on the Done handoff and the card issue comment
- **AND** the card continues (commit, PR, QA) without remaining stuck in Code Review
- **AND** Status is not moved by inventing a third column
