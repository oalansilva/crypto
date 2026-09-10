## ADDED Requirements

### Requirement: Parent emits the review wave as two Tasks in one turn
When Code Review starts, the parent session's emitted tool call set for that turn SHALL include both `diff-reviewer` and `code-reviewer` Tasks. The parent MUST NOT emit the second reviewer only after destape or completion of the first. Operator-facing emission MAY note that host queueing is allowed and does not fail the card. Destape remains an order/poke (#879); its followup MUST NOT be emitted as permission to skip the pair or to birth the missing reviewer. This SHALL NOT add a state, event, hook, or `enabled_tools` change to `.cursor/process-fsm.yaml`.

#### Scenario: Same-turn wave is what the operator sees
- **WHEN** the parent starts Code Review after the interval is materialized
- **THEN** that parent turn contains two reviewer Task calls
- **AND** the chat does not show Apply→review→Apply→review as the happy path

#### Scenario: Destape of one reviewer does not birth the other
- **WHEN** destape fires because one reviewer already completed
- **THEN** the parent does not spawn the other reviewer in a later turn as a substitute for the wave
- **AND** if the pair has not returned, the parent waits
- **AND** destape matching, sidecar path, and poke≠`concluiu?` stay #879

### Requirement: Correction list and visible block are operator-facing
P1/P2 from both reviewers SHALL be emitted to the next Apply spawn as a single list in one prompt. After at most one correction Apply plus one wave, remaining P1/P2 SHALL be emitted as a visible block in the operator chat (not a third cycle, not a new column). An Apply child that returns early without a P0 SHALL produce the same class of visible block rather than a silent extra Apply. Done of this change is the next session not repeating Apply and review; extra automatic tests MUST NOT be published as the Done criterion.

#### Scenario: List not per-finding spawn
- **WHEN** the wave returns more than one P1/P2
- **THEN** the parent spawn prompt for correction contains the whole list
- **AND** the parent does not emit one Apply Task per finding

#### Scenario: Visible block after the correction ceiling
- **WHEN** P1/P2 remain after one correction Apply and one wave
- **THEN** the operator-facing message records the block
- **AND** no third Apply or third wave is spawned for those findings

## MODIFIED Requirements

### Requirement: Critics inherit model, not transcript
Assessment A, Assessment B, `diff-reviewer`, and `code-reviewer` SHALL use the same model as the parent session and SHALL receive a self-contained prompt. They MUST NOT inherit the parent Design/Apply/Review transcript. Isolated critics MAY write only `.impeccable/critique/**`. They MUST NOT edit `design.md`, prototype HTML, or product code. Their return to the parent MUST be bullets, disposition, verdict, and snapshot path. For Code Review, both reviewer prompts SHALL be emitted in the same parent turn with the parent-materialized interval; reviewers return findings or `No findings.` as a list and MUST NOT instruct the parent to spawn per finding.

#### Scenario: Dual critic without parent chat
- **WHEN** Design spawns Assessment A and Assessment B
- **THEN** each child uses the parent model
- **AND** the spawn prompt does not include the parent transcript
- **AND** the child's user-visible return is bullets plus snapshot path, not the full rubric dump

#### Scenario: Reviewers without Design/Apply transcript
- **WHEN** Code Review spawns `diff-reviewer` or `code-reviewer`
- **THEN** the prompt is the versioned agent file plus the diff under review
- **AND** it MUST NOT include the Design or Apply chat
- **AND** both reviewer Tasks are present in that same parent turn
