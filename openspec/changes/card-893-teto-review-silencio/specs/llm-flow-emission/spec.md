## ADDED Requirements

### Requirement: Parent MUST NOT emit a ceiling Ask
After a Code Review wave, the parent session MUST NOT emit an operator question to authorize an extra correction Apply or to accept residual. The policy is already: extra = 1 mechanical correction Apply + 1 verify wave; leftover or new P1 = residual on Done; the card continues. Destape poke remains an order (#879) and MUST NOT be rewritten as that Ask. Extra automatic tests MUST NOT be published as the Done criterion of this silent ceiling.

#### Scenario: No authorize-extra question in the operator chat
- **WHEN** one correction Apply and one verify wave still leave P1, or the verify wave reports a new P1
- **THEN** the operator-facing message MUST NOT ask «autorizar extra / aceitar residual»
- **AND** the parent records residual on the Done handoff and the card comment
- **AND** the parent continues commit, PR, and QA

#### Scenario: Destape poke is not turned into an Ask
- **WHEN** destape fires after the verify wave
- **THEN** the followup remains an order
- **AND** the parent MUST NOT emit a question from that poke
- **AND** destape matching, sidecar path, and poke≠`concluiu?` stay #879

## MODIFIED Requirements

### Requirement: Correction list and visible block are operator-facing
P1/P2 from both reviewers SHALL be classified (mechanical versus judgment) and the **mechanical** items SHALL be emitted to the next Apply spawn as a single list in one prompt, without an operator Ask. Judgment items SHALL be emitted as residual and MUST NOT occupy that prompt. After at most one correction Apply plus one wave, remaining P1/P2 **or a new P1** SHALL be emitted as residual on the Done handoff and the card issue comment (not a third cycle, not a new column, not an Ask, not a card stuck in Code Review). The card SHALL continue (commit, PR, QA). An Apply child that returns early without a P0 SHALL produce a visible block rather than a silent extra Apply. Done of this change is the next session not interrupting with a ceiling Ask and not opening a third cycle; extra automatic tests MUST NOT be published as the Done criterion.

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
