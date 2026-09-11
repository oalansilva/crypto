## ADDED Requirements

### Requirement: Reviewer dump SHALL emit finding schema
The versioned files `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md` SHALL instruct each child to emit every finding as a labeled `FINDING` block with `gravidade` (P0–P3), `classe` (`mecanico` | `juizo`), `conserto_obvio` (`sim` | `nao`), `conserto_proposto`, `bloqueia_merge` (`sim` | `nao`), `file`, and `summary`. If there are no findings the dump MUST be exactly `No findings.` The dump MUST NOT be a free paragraph that the parent has to classify. This SHALL NOT add a third reviewer and SHALL NOT be a JSON API schema.

#### Scenario: Wave dump carries class and obvious-fix
- **WHEN** `diff-reviewer` or `code-reviewer` finishes with at least one finding on a materialized interval
- **THEN** each finding in the dump includes `gravidade`, `classe`, and `conserto_obvio`
- **AND** the parent does not have to infer class from prose

#### Scenario: Empty dump stays No findings
- **WHEN** either reviewer has nothing to report
- **THEN** the dump is `No findings.`
- **AND** it does not invent a destape-completeness finding to fill the dump

### Requirement: Stable severity rubric for harness review
Both local reviewers SHALL use this observable rubric: P3 = copy / needle / Apply detail; P2 = incomplete contract that does **not** change acceptance; P1 = the patch **breaks** observable acceptance (Ask in the middle of the column, a third cycle, DEV talking to a PROD bot); P0 = the column stops. A destape «falta esta frase» item is not a finding. A destape table that is wrong about operator-visible behavior (P0 no longer stops the column) is P1 of acceptance.

#### Scenario: Copy nit is P3 and broken acceptance is P1
- **WHEN** one finding is a needle/copy tweak and another is that the patch would emit an Ask or a third cycle
- **THEN** the copy nit is dumped as P3
- **AND** the broken acceptance is dumped as P1

#### Scenario: Missing destape sentence is not scored
- **WHEN** the destape table is present with the five operator-visible rows
- **THEN** `code-reviewer` MUST NOT dump «falta esta frase» as P1/P2/P3
- **AND** completeness of that paragraph is not a finding

### Requirement: Process reviewer MUST NOT recaça the mechanical checklist
After the parent mechanical process checklist has run (or as part of the same Code Review turn), `.cursor/agents/code-reviewer.md` SHALL instruct the process reviewer not to re-score: tasks all done, Design tokens present, two reviewers in the same turn, pasted interval, or board state machine with no new edge. The process reviewer SHALL only ask whether the supplied diff punctures Entra/não entra of the bound change. Split of roles remains: `diff-reviewer` hunts defects in the interval; `code-reviewer` hunts contract. Independence still holds. This requirement MUST NOT merge the two reviewers.

#### Scenario: Checklist items are not process findings
- **WHEN** `code-reviewer` reviews a harness diff whose tasks, Design tokens, same-turn wave, pasted interval, and process-fsm.yaml edge are already confirmed
- **THEN** those items are not dumped as findings
- **AND** the dump either is `No findings.` or only Entra/não entra punctures with schema fields

#### Scenario: Roles stay split
- **WHEN** Code Review runs
- **THEN** `diff-reviewer` still hunts defects in the interval
- **AND** `code-reviewer` still hunts contract
- **AND** the parent MUST NOT fuse them into one Task

### Requirement: Closing review MUST NOT relitigate residual nor raise its severity
Closing review versus `develop` SHALL hunt only a defect new relative to the pre-commit interval, or reuse the SHA when that exact SHA already has this versus-`develop` run. The parent SHALL paste residual already on the card comment under `## Residual já no card`. Reviewers MUST NOT re-emit those items and MUST NOT raise their `gravidade`. The parent MUST NOT inflate dumped severity on that wave. This requirement MUST NOT add a third cycle and MUST NOT reopen #893's silent ceiling.

#### Scenario: Residual on the card is not re-emitted as a new P1
- **WHEN** closing review runs and `## Residual já no card` lists a destape-wording P2
- **THEN** the reviewer dump MUST NOT reopen that item
- **AND** MUST NOT dump it as P1

#### Scenario: New closing defect is allowed
- **WHEN** closing review finds a defect that is not in `## Residual já no card` and is new versus the pre-commit interval
- **THEN** the dump MAY include it as a `FINDING` at the rubric gravidade
- **AND** the parent still MUST NOT raise that gravidade

### Requirement: blocks_merge on a nit MUST NOT authorize a third cycle
A `bloqueia_merge: sim` field on a P3 or other non-P0 finding SHALL be residual for the T15 package. It MUST NOT authorize a third Apply+review cycle, MUST NOT emit an Ask, and MUST NOT override the #893 ceiling. A reviewer P0 still stops the column.

#### Scenario: Nit with blocks_merge still follows the ceiling
- **WHEN** a verify wave dumps `gravidade: P3` with `bloqueia_merge: sim` after the one correction cycle
- **THEN** the parent records it as residual
- **AND** MUST NOT spawn another Apply or wave for it
- **AND** MUST NOT ask «autorizar extra / aceitar residual»

## MODIFIED Requirements

### Requirement: Correction ceiling then visible block
The local reviewers SHALL NOT apply fixes. The parent SHALL NOT apply fixes in its own transcript. Each finding SHALL already carry `classe` (`mecanico` | `juizo`) in the dump; the parent SHALL copy that class and MUST NOT reclassify by re-reading prose. Mechanical P1/P2 SHALL be collected into one list and handed to **at most one** correction Apply child for the column, followed by **one** wave on the new interval, with no operator Ask. Judgment SHALL go straight to residual and MUST NOT occupy that correction slot. Remaining P1/P2 after that cycle, **or a new P1** on the verify wave, SHALL be residual on the Done handoff and the card issue comment; the card SHALL continue (commit, PR, QA); the parent MUST NOT open a third cycle and MUST NOT ask «autorizar extra / aceitar residual». P0 from a reviewer classifies as a column block (not a correction-list cycle). P3 stays classified residual. A `bloqueia_merge: sim` field on a non-P0 nit MUST NOT authorize a third cycle. Extra automatic tests MUST NOT be the Done criterion of the change that introduced this silent ceiling.

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
The local reviewers SHALL NOT apply fixes. The parent session SHALL NOT apply fixes in its own transcript. The parent SHALL copy each finding's dumped `classe` and `gravidade` and MUST NOT reclassify by re-reading prose and MUST NOT raise severity. For mechanical P1/P2, the parent SHALL spawn **at most one** correction Apply child with the combined list, then **one** wave, without an operator Ask; it MUST NOT re-run the affected reviewer per finding as the happy path. Judgment MUST NOT enter that correction Apply. Remaining P1/P2 after that cycle, or a new P1 on the verify wave, stay residual on Done while the card continues. A reviewer P0 classifies as a column block.

#### Scenario: Blocking finding
- **WHEN** `diff-reviewer` or `code-reviewer` reports a blocking finding
- **THEN** the parent MUST copy its dumped class (mechanical into the correction list, judgment into residual) before committing
- **AND** the reviewer MUST NOT edit the working tree
- **AND** the parent MUST NOT implement the fix in the orchestrator transcript
- **AND** the parent MUST NOT ask the operator to authorize extra or accept residual in order to proceed
- **AND** the parent MUST NOT raise the dumped gravidade
