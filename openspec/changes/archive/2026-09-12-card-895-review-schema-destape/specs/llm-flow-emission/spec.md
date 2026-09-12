## ADDED Requirements

### Requirement: Parent MUST NOT raise emitted severity or reclassify from prose
Operator-facing emission after a Code Review wave or closing wave SHALL copy `gravidade` and `classe` from each reviewer `FINDING` block. The parent session MUST NOT emit a higher severity than the child dumped and MUST NOT emit a different class obtained by re-reading the summary. Empty dumps stay the exact line `No findings.`

#### Scenario: Closing wave does not inflate a P2
- **WHEN** a closing-versus-`develop` dump contains `gravidade: P2` for a wording item
- **THEN** the operator-facing package keeps P2
- **AND** the parent MUST NOT emit it as P1

#### Scenario: Parent does not invent class from a paragraph
- **WHEN** a reviewer dump already has `classe: mecanico` or `classe: juizo` on a finding
- **THEN** the parent emission uses that class
- **AND** the chat does not show the parent re-labeling the finding after rereading prose

### Requirement: Destape completeness MUST NOT be emitted as a finding
«Falta esta frase» / a missing clause on the destape table SHALL NOT be emitted as an operator-facing finding. Destape poke emission remains an order whose policy is the destape table. Destape matching, sidecar path, and poke≠`concluiu?` stay #879.

#### Scenario: Missing destape sentence is dropped from the package
- **WHEN** a process-reviewer dump includes a finding that the destape table is missing a sentence or a branch
- **THEN** the operator-facing package does not include that finding
- **AND** the parent MUST NOT emit it as residual P1 on Done

### Requirement: Closing wave MUST NOT relitigate residual already on the card
When emitting the closing wave versus `develop`, the parent SHALL paste residual already on the card comment under `## Residual já no card`. Operator-facing emission from that wave MUST NOT reopen those items and MUST NOT raise their severity. Only a defect new relative to the pre-commit interval (or reuse of a SHA already covered) MAY enter the package.

#### Scenario: Residual on the card is not reopened
- **WHEN** the card comment already records a destape-wording residual at P2 and the closing wave dump repeats it
- **THEN** the operator-facing package does not reopen that item
- **AND** the parent MUST NOT emit it as a new P1

#### Scenario: New closing defect still enters
- **WHEN** the closing wave dump contains a `FINDING` that is not in `## Residual já no card`
- **THEN** that finding may enter the package at the dumped gravidade
- **AND** the parent still MUST NOT raise that gravidade

### Requirement: Checklist failure is a visible block not LLM prose
A failed mechanical process checklist SHALL be emitted as `ERROR: process-checklist failed:` plus the failed item. The parent MUST NOT emit that failure as a process-reviewer finding paragraph and MUST NOT commit. A passing checklist MUST NOT be re-emitted as LLM findings about tasks, Design tokens, same-turn wave, pasted interval, or FSM edges.

#### Scenario: Checklist fail is the operator-facing block
- **WHEN** the process checklist exits non-zero
- **THEN** the operator-facing message contains `ERROR: process-checklist failed:`
- **AND** it does not ask the process reviewer to rewrite that failure as P1/P2 prose
- **AND** no commit is emitted in that turn

## MODIFIED Requirements

### Requirement: Correction list and visible block are operator-facing
P1/P2 from both reviewers SHALL already carry `classe` (`mecanico` | `juizo`) in the dump. The parent SHALL copy that class: the **mechanical** items SHALL be emitted to the next Apply spawn as a single list in one prompt, without an operator Ask. Judgment items SHALL be emitted as residual and MUST NOT occupy that prompt. After at most one correction Apply plus one wave, remaining P1/P2 **or a new P1** SHALL be emitted as residual on the Done handoff and the card issue comment (not a third cycle, not a new column, not an Ask, not a card stuck in Code Review). The card SHALL continue (commit, PR, QA). An Apply child that returns early without a P0 SHALL produce a visible block rather than a silent extra Apply. A `bloqueia_merge: sim` field on a non-P0 nit MUST NOT be emitted as permission for a third cycle. Done of this change is the next session not relitigating destape-wording residual as a new P1 and not opening a third cycle; extra automatic tests MUST NOT be published as the Done criterion.

#### Scenario: List not per-finding spawn
- **WHEN** the wave returns more than one mechanical P1/P2
- **THEN** the parent spawn prompt for correction contains the whole mechanical list
- **AND** the parent does not emit one Apply Task per finding
- **AND** the parent does not emit an Ask before that spawn

#### Scenario: Residual after the correction ceiling continues the card
- **WHEN** P1/P2 remain after one correction Apply and one wave, or a new P1 appears on that wave
- **THEN** the operator-facing Done handoff and the card comment record the residual
- **AND** no third Apply or third wave is spawned for those findings
- **AND** no Ask «autorizar extra / aceitar residual» is emitted
- **AND** the card continues (commit, PR, QA)
