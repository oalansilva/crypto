## ADDED Requirements

### Requirement: Happy path after the verify wave is residual and continue
After the single correction Apply and the single verify wave, remaining P1 or a **new** P1 on that wave SHALL be classified residual. The parent SHALL record that residual on the Done handoff and the card issue comment, SHALL continue (commit, closing wave versus `develop`, PR, QA), and MUST NOT open a third cycle. The parent MUST NOT ask the operator to authorize extra work or to accept residual. Homologation remains Alan's once, on the package (findings + residual + SHA). Extra automatic tests MUST NOT be the Done criterion.

#### Scenario: Leftover or new P1 does not start a third cycle
- **WHEN** the verify wave still reports P1, or reports a P1 that was not on the pre-correction list
- **THEN** the parent records residual on the Done handoff and the card comment
- **AND** the parent MUST NOT spawn another Apply or another judgment wave
- **AND** the parent MUST NOT ask «autorizar extra / aceitar residual»
- **AND** the card continues to commit, PR, and QA

#### Scenario: Clean verify wave still commits
- **WHEN** the verify wave returns `No findings.` (or only classified P3 residual)
- **THEN** the parent commits and continues the closing path
- **AND** this requirement does not invent a third cycle

## MODIFIED Requirements

### Requirement: Correction ceiling then visible block
The local reviewers SHALL NOT apply fixes. The parent SHALL NOT apply fixes in its own transcript. Each finding SHALL be classified mechanical versus judgment. Mechanical P1/P2 SHALL be collected into one list and handed to **at most one** correction Apply child for the column, followed by **one** wave on the new interval, with no operator Ask. Judgment SHALL go straight to residual and MUST NOT occupy that correction slot. Remaining P1/P2 after that cycle, **or a new P1** on the verify wave, SHALL be residual on the Done handoff and the card issue comment; the card SHALL continue (commit, PR, QA); the parent MUST NOT open a third cycle and MUST NOT ask «autorizar extra / aceitar residual». P0 from a reviewer classifies as a column block (not a correction-list cycle). P3 stays classified residual. Extra automatic tests MUST NOT be the Done criterion of the change that introduced this silent ceiling.

#### Scenario: One correction Apply then one wave
- **WHEN** either reviewer reports mechanical P1/P2
- **THEN** the parent spawns at most one Apply child with the combined mechanical list
- **AND** after that Apply returns, the parent spawns one wave in the same turn
- **AND** the parent does not re-run a single reviewer per finding as the happy path
- **AND** the parent MUST NOT ask to authorize that correction

#### Scenario: Third cycle is refused
- **WHEN** P1/P2 remain after that correction Apply and wave, or a new P1 appears on that wave
- **THEN** the parent records residual on the Done handoff and the card comment
- **AND** MUST NOT spawn another Apply or another wave for those findings
- **AND** MUST NOT ask «autorizar extra / aceitar residual»
- **AND** the card continues (commit, PR, QA) instead of remaining stuck in Code Review

### Requirement: Principal session applies reviewer findings
The local reviewers SHALL NOT apply fixes. The parent session SHALL NOT apply fixes in its own transcript. The parent SHALL classify each finding as mechanical or judgment and, for mechanical P1/P2, spawn **at most one** correction Apply child with the combined list, then **one** wave, without an operator Ask; it MUST NOT re-run the affected reviewer per finding as the happy path. Judgment MUST NOT enter that correction Apply. Remaining P1/P2 after that cycle, or a new P1 on the verify wave, stay residual on Done while the card continues. A reviewer P0 classifies as a column block.

#### Scenario: Blocking finding
- **WHEN** `diff-reviewer` or `code-reviewer` reports a blocking finding
- **THEN** the parent MUST classify it (mechanical into the correction list, judgment into residual) before committing
- **AND** the reviewer MUST NOT edit the working tree
- **AND** the parent MUST NOT implement the fix in the orchestrator transcript
- **AND** the parent MUST NOT ask the operator to authorize extra or accept residual in order to proceed
