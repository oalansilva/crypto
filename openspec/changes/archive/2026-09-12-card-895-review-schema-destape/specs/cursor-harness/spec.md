## ADDED Requirements

### Requirement: Parent consumes reviewer finding schema as-is
Each finding returned by `diff-reviewer` or `code-reviewer` SHALL already carry labeled fields in the child dump: `gravidade` (P0–P3), `classe` (`mecanico` | `juizo`), `conserto_obvio` (`sim` | `nao`), `conserto_proposto`, and `bloqueia_merge` (`sim` | `nao`). The Cursor parent SHALL copy those fields before any correction spawn. The parent MUST NOT reclassify `classe` by re-reading prose and MUST NOT raise the emitted `gravidade`. A `bloqueia_merge: sim` field on a P3 nit MUST NOT authorize a third cycle, MUST NOT emit an Ask, and MUST NOT stop the column. A reviewer P0 remains a column block. This requirement MUST NOT add a FSM column or event, MUST NOT reopen #884 spawn-per-task, MUST NOT reopen #879 destape matching, and MUST NOT change the #893 silent ceiling (1 mechanical correction Apply + 1 verify wave; leftover or new P1 = residual on Done; the card continues).

#### Scenario: Parent copies class and severity from the dump
- **WHEN** a Code Review wave dump contains a `FINDING` block with `gravidade: P2` and `classe: juizo`
- **THEN** the parent records that finding as P2 judgment residual
- **AND** the parent MUST NOT publish it as P1
- **AND** the parent MUST NOT spawn a correction Apply for it

#### Scenario: blocks_merge on a nit does not add a cycle
- **WHEN** a dump contains `gravidade: P3` and `bloqueia_merge: sim`
- **THEN** the parent records it as classified P3 residual
- **AND** the parent MUST NOT open a third cycle
- **AND** the parent MUST NOT ask the operator to authorize extra work

### Requirement: Destape review followup is an operator-visible table
`FOLLOWUP_REVIEW` in `scripts/process-fsm/subagent_stop.py` SHALL be an order whose destape policy is a short table of operator-visible rows, not a paragraph that tries to be a state machine. The rows SHALL be: limpo → commit; só juízo → residual, card segue (não gasta correção); mecânico → no máximo um conserto + uma verificação; após 1+1 → residual, card segue; P0 → a coluna pára. The followup MUST still wait for the pair, MUST NOT ask «autorizar extra / aceitar residual», and MUST NOT contain `concluiu?`. Destape matching, sidecar path `.cursor/tmp/awaiting-task.json`, `loop_count`, classification, and poke≠`concluiu?` stay #879. A process reviewer MUST NOT score a missing clause on that table as a finding. A table that is wrong about what the operator sees (P0 no longer stops the column) SHALL be a P1 of acceptance, not wording.

#### Scenario: Review followup lists the five destape rows
- **WHEN** destape fires for `diff-reviewer` or `code-reviewer` with matching sidecar
- **THEN** `followup_message` contains the five destape rows (limpo, só juízo, mecânico, após 1+1, P0)
- **AND** it still waits for the pair if the other reviewer has not returned
- **AND** it does not contain `concluiu?`

#### Scenario: Missing destape sentence is not a finding
- **WHEN** a process reviewer dump scores «falta esta frase» or a missing clause on the destape table
- **THEN** that item MUST NOT enter the operator-facing package
- **AND** the parent MUST NOT raise it as a new P1 on closing versus `develop`

#### Scenario: Destape table that stops stopping P0 is acceptance P1
- **WHEN** the destape table or runbook copy would let a reviewer P0 continue the column
- **THEN** that defect is P1 of acceptance
- **AND** it is not classified as copy or «frase em falta»

### Requirement: Mechanical process checklist is a parent script
Before commit after a Code Review wave, the Cursor parent SHALL run `scripts/process-fsm/review_process_checklist.py`. The script SHALL confirm: bound change `tasks.md` has no pending `- [ ]`; bound `design.md` has parseable `UI impact:` / `live_route:` / `surface:` tokens; `.cursor/tmp/review-diff.patch` exists and is non-empty; the pasted interval does not add a state, event, or `enabled_tools` to `.cursor/process-fsm.yaml`. Two reviewers in the same parent turn remains a parent session fact (already #884); the parent MUST treat a wave that was not same-turn as the same visible block. Exit non-zero SHALL print `ERROR: process-checklist failed:` plus the failed item, SHALL be a visible block, and MUST NOT commit. A failed checklist MUST NOT come back as LLM prose or as a process-reviewer finding. Extra automatic tests MUST NOT be the Done criterion of this change.

#### Scenario: Checklist failure blocks commit
- **WHEN** the parent runs the process checklist and a disk item fails (empty review interval, pending task, missing Design token, or a new FSM edge in the interval)
- **THEN** the operator-facing chat shows `ERROR: process-checklist failed:` with that item
- **AND** the parent MUST NOT commit
- **AND** the parent MUST NOT spawn the process reviewer to restate that failure as a finding

#### Scenario: Checklist pass is not re-scored by the process LLM
- **WHEN** the process checklist exits 0 and both reviewers were born in the same parent turn
- **THEN** `code-reviewer` MUST NOT report tasks-done, Design tokens, same-turn wave, pasted interval, or «no new FSM edge» as findings
- **AND** that reviewer only asks whether the diff punctures Entra/não entra of the bound change

### Requirement: Schema does not change the silent ceiling
The finding schema and destape table SHALL NOT change the #893 silent ceiling: at most one mechanical correction Apply plus one verify wave; no operator Ask; leftover or new P1/P2 = residual on Done (handoff + card comment) and the card continues; a reviewer P0 still stops the column. Deterministic QA inventory/formatting/new-file-skip stays out of the judgment-review wave. Human homologation remains once (T15). This requirement MUST NOT add a FSM column or event and MUST NOT reopen #884, #879, or #880.

#### Scenario: Schema field does not authorize a third cycle
- **WHEN** a verify wave dump still has P1/P2 after one correction Apply, including a `bloqueia_merge: sim` on a non-P0 finding
- **THEN** the parent records residual on the Done handoff and the card comment
- **AND** the parent MUST NOT spawn a third cycle
- **AND** the parent MUST NOT ask «autorizar extra / aceitar residual»

## MODIFIED Requirements

### Requirement: Wave findings are classified mechanical versus judgment
Each finding from a Code Review wave SHALL already carry `classe` (`mecanico` | `juizo`) in the reviewer dump. The Cursor parent SHALL copy that class before any correction spawn and MUST NOT reclassify by re-reading prose and MUST NOT raise the emitted `gravidade`. Mechanical (`mecanico`) means an obvious file/line/instruction fix whose severity is below architecture, product, or acceptance of the bound card. Judgment (`juizo`) means the finding would change design, change acceptance, or is robustness outside the card. Mechanical findings from that wave SHALL go together to the single correction Apply. Judgment findings SHALL go straight to residual and MUST NOT occupy the correction slot. A reviewer P0 remains a column block and MUST NOT enter the correction list. P3 remains classified residual. A `bloqueia_merge: sim` field on a P3 nit MUST NOT authorize a third cycle. This requirement MUST NOT add a FSM column or event and MUST NOT reopen #884 spawn-per-task or #879 destape matching.

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

#### Scenario: Parent does not reclassify from prose
- **WHEN** a reviewer dump labels a finding `classe: juizo` with `gravidade: P2`
- **THEN** the parent copies juízo / P2
- **AND** the parent MUST NOT re-read the summary to promote it to mechanical P1
