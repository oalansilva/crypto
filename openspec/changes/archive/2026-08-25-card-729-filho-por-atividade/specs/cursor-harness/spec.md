## MODIFIED Requirements

### Requirement: Design gate is process-based
While `Status=Design`, the **parent** session SHALL spawn an isolated Design-author child (same model, no parent transcript) to write OpenSpec artifacts and a navigable prototype when UI-impacting. After those artifacts exist, the parent SHALL spawn Assessment A and B as a wave (MUST NOT nest A/B inside the Design child). Isolated critics MUST NOT edit product code, `design.md`, or prototype files. They MAY write only `.impeccable/critique/**`. The parent MUST NOT author OpenSpec proposal/specs/tasks, prototype files, or `design.md` **except** that after A/B return with zero open P0/P1 the parent MUST write only the `## Design Critique` section (bullets, disposition, verdict, snapshot path). Open P0/P1 SHALL re-spawn the Design-author child with those findings in the prompt; the parent MUST NOT polish. `process_event submeter_design` SHALL stay on the parent. The agent MUST NOT implement product code until `Status=Pronto para Dev`.

#### Scenario: Isolated critique
- **WHEN** Design evidence is ready
- **THEN** Assessment uses a separate Task that MUST NOT edit product, `design.md`, or prototype files
- **AND** the Task MAY write only `.impeccable/critique/**`
- **AND** missing critique or empty snapshot keeps the verdict `BLOCKED`

#### Scenario: Parent does not author Design
- **WHEN** `Status=Design` and OpenSpec/prototype need to be written
- **THEN** a Design-author child writes those files
- **AND** the parent transcript does not implement `/opsx:new` / `/opsx:ff` or patch the prototype itself
- **AND** after A/B return, the parent MAY write only the `## Design Critique` section of `design.md`
- **AND** `process_event submeter_design` stays on the parent
- **AND** open P0/P1 causes a re-spawn of the Design-author child, not parent polish

#### Scenario: No OpenCode lock machine
- **WHEN** Design runs in Cursor
- **THEN** the flow MUST NOT require `design_spawn_stage`, `design_artifact_write`, lease evidence or OpenCode 1.18.18 attestation

### Requirement: One chat per column on both clients
The Cursor and Grok runbooks SHALL require one chat per card titled `#<id>` from Em Refinamento through Done técnico. The parent MUST spawn isolated activity children (grill, Design author, Apply column, QA) and dual-reviewer / dual-critic waves. The parent MUST refuse to execute those activities itself and MUST NOT ask for a new chat titled `#<id> <coluna>`. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry.

#### Scenario: Design chat refuses apply
- **WHEN** the bound card is in `Status=Design` and the operator asks to `/opsx:apply` or implement product code
- **THEN** that request is refused in the same transcript
- **AND** the agent does not ask for a new chat titled `#<id> Apply`
- **AND** it states Apply waits for `Pronto para Dev` (T7 Alan)

#### Scenario: Both clients carry the same refusal
- **WHEN** `alan-workflow` is followed in Cursor or via the Grok stub
- **THEN** both clients document `#id` per card, activity children, and same-chat refusal
- **AND** `.cursor/process-fsm.yaml` has no new event for this rule

## ADDED Requirements

### Requirement: Activity children do not inherit parent transcript
Grill, Design-author, Apply-column, QA, Assessment A/B, `diff-reviewer`, and `code-reviewer` SHALL receive a self-contained prompt and MUST NOT inherit the parent transcript. Apply-column SHALL keep per-task sliced reads **inside** that child. Grill MUST bind on `Status=Em Refinamento` plus issue id in the prompt, not on git branch `card-<id>-*`. Nested spawn is forbidden (Design child MUST NOT spawn A/B; Apply child MUST NOT spawn reviewers).

#### Scenario: Apply column child slices internally
- **WHEN** Em desenvolvimento starts with `Status=Pronto para Dev`
- **THEN** the parent spawns one Apply child
- **AND** that child loads one task + matching spec + short `design.md` apply sections per task
- **AND** the parent does not implement product code
- **AND** the Apply child MUST NOT run `process_event`, commit, push, or spawn reviewers
- **AND** it returns task status so the parent can git + `pedir_review`

#### Scenario: Grill child binds without a card branch
- **WHEN** Alan asks to grill and Project Status is `Em Refinamento`
- **THEN** the parent spawns `grill-card` with the issue id in the prompt even if `q_git` is `develop`
- **AND** the child writes the issue body
- **AND** the parent does not write the issue body itself
