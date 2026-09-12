## ADDED Requirements

### Requirement: Composer destape and resume keep execução slug
When the Cursor parent resumes or destapes (`subagentStop` followup) an isolated execução child (Apply-coluna, QA, `diff-reviewer`, `code-reviewer`, same-card search, `fecho-lote`), the continued run MUST remain executed and billed as `composer-2.5`. `composer-2.5-fast` MUST NOT be used for that continuation, including after destape or host `resume`. If the host resumes or bills the continuation as `composer-2.5-fast`, the parent SHALL treat that run as abort: it MUST NOT use that run as acceptance and MUST NOT call Task `resume` on it. The parent SHALL spawn a **new** Task with `model: composer-2.5` and a self-contained prompt (Task `resume` MUST NOT be used to change model). Same-card search on a bound card MUST NOT use subagent_type `explore` when the host maps `explore` to `composer-2.5-fast`; search SHALL use `generalPurpose` with `model: composer-2.5`. The `fecho-lote` child MUST NOT use destape sidecar; if the host auto-resumes a prior `fecho-lote` run, the parent MUST ignore that run.

#### Scenario: Fast continuation after destape is refused
- **WHEN** an execução child was spawned with `model: composer-2.5` and the host continues after destape or resume as `composer-2.5-fast`
- **THEN** the parent MUST NOT treat that continuation as the passing child
- **AND** the parent MUST NOT `resume` that run
- **AND** the parent SHALL spawn a new Task with `model: composer-2.5`

#### Scenario: Same-card search avoids explore when mapped to fast
- **WHEN** the parent needs codebase search on the same bound card on Cursor
- **THEN** it SHALL use `generalPurpose` with `model: composer-2.5`
- **AND** it MUST NOT rely on subagent_type `explore` if that maps to `composer-2.5-fast`

### Requirement: Release and lote closeout require Composer parent chat
When the operator explicitly asks to close the lote, subir a release, or run T16 (`process_event fechar_release`), including the isolated `fecho-lote` kaizen child, the Cursor parent chat MUST be Composer 2.5 (`composer-2.5`). This is the sole exception to silence about the parent picker on bound card chats. If the parent chat is Grok 4.6 (`cursor-grok-4.6-high`) or any model other than `composer-2.5`, the parent SHALL refuse visibly: it MUST NOT run T16 or spawn `fecho-lote` in that chat and SHALL direct the operator to a new session with Composer 2.5. Grok 4.6 remains only for juízo roles in the role table. The git MUST NOT force the parent picker via `AGENTS.md`, harness, or overlay `clients.*.auto`. The runbook MUST NOT recommend a parent picker on other `#<id>` card chats.

#### Scenario: Grok parent refuses T16
- **WHEN** the operator asks to fechar o lote or subir a release while the parent chat picker is not `composer-2.5`
- **THEN** the parent shows a visible refusal
- **AND** it MUST NOT call `process_event fechar_release` in that chat
- **AND** it MUST NOT spawn `fecho-lote` in that chat

#### Scenario: Composer parent may run release closeout
- **WHEN** the operator asks to fechar o lote or subir a release and the parent chat is `composer-2.5`
- **THEN** the parent MAY spawn `fecho-lote` and call T16 per the existing closeout contract

### Requirement: Isolated lote-close child uses Composer and does not destape
When the operator explicitly asks to close the lote / subir a release, the Cursor parent SHALL spawn one isolated `fecho-lote` child with Task `model: composer-2.5` via `generalPurpose` with a self-contained prompt. The Task `description` MUST contain `fecho-lote` and MUST NOT contain destape classifier needles (`grill-card`, `apply-coluna`, `diff-reviewer`, `code-reviewer`, `qa-gate`, `design-autor`, `design-critic`, `Assessment A`, `Assessment B`). Canonical title: `fecho-lote kaizen`. The child MUST NOT call `process_event`, MUST NOT move Status, and MUST NOT commit or push. The parent SHALL await native Task `completed` plus payload in the **same** turn, then call `process_event fechar_release`. The parent MUST NOT write `.cursor/tmp/awaiting-task.json` for this spawn. Destape MUST NOT fire (no new classifier needle, no new `FOLLOWUP_*`). This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools`. Overlay pin remains `v1.1.15` for this change.

#### Scenario: Lote child is Composer and parent still calls T16
- **WHEN** the operator asks to fechar o lote / subir a release on Cursor
- **THEN** the parent spawns one isolated child whose Task `model` is `composer-2.5`
- **AND** the Task `description` contains `fecho-lote`
- **AND** the child does not call `process_event`
- **AND** the parent calls `process_event fechar_release` in the same turn after `completed`

#### Scenario: Lote child does not destape
- **WHEN** that `fecho-lote` child returns `status=completed`
- **THEN** `subagent_stop` does not inject a followup for it
- **AND** no sidecar was written for that spawn
- **AND** `classify_etapa` needles of existing children are unchanged

### Requirement: Invalid Task model slug is a visible refusal
If the Cursor host rejects the Task `model` slug, the parent SHALL surface that rejection in the chat. The parent MUST NOT omit `model`, MUST NOT pass `inherit`, and MUST NOT retry with `composer-2.5-fast`. Changing a subagent model requires a new session (#430); in-flight spawns stay on the old model. Renaming a slug is a new card.

#### Scenario: Rejected slug does not inherit the picker
- **WHEN** the parent spawns a Task with a slug the Cursor host no longer accepts
- **THEN** the operator-facing chat shows the host refusal
- **AND** the child MUST NOT run under the parent picker
- **AND** the parent MUST NOT retry with `inherit` or with `composer-2.5-fast`

### Requirement: Live proof of role models on both Cursor modes
Done of this change SHALL include live proof on both Cursor modes (terminal and Desktop+SSH): one Apply-coluna spawn with `composer-2.5` and one grill or Design spawn with `cursor-grok-4.6-high`, each with host `completed`. The Apply of card #904 is that Composer proof (not a later product card). Cloud, Auto, and `composer-2.5-fast` MUST NOT be used. Q2–Q6 of existing children MUST NOT be redesigned.

#### Scenario: Apply of this card is the Composer proof
- **WHEN** Apply-coluna of #904 runs after T8
- **THEN** the Task `model` is `composer-2.5`
- **AND** host status is `completed` in that mode

#### Scenario: Both Cursor modes are required
- **WHEN** live proof is recorded
- **THEN** terminal and Desktop+SSH each have host `completed` for one juízo spawn and one Apply spawn
- **AND** Cloud and Auto were not used

## MODIFIED Requirements

### Requirement: Cursor is the versioned development harness
The repository SHALL contain a versioned Cursor **adapter** under `.cursor/` (rules, skills, commands, hooks) that compiles the process nucleus (`.cursor/process-fsm.yaml` + `scripts/process-fsm/` + root `AGENTS.md`). Cursor is not the only versioned client: Grok Build has a sibling adapter under `.grok/`, OpenCode 1.18.18 has a sibling adapter under `.opencode/plugin/` (auto-load; no `opencode.json`), and dsh has a sibling adapter under `.dsh/plugin/` (Cordis native; no Claude `hooks.json` Guard). The repo MUST NOT restore the lock machine (`design_spawn_stage`, `design_artifact_write`, lease, packet, attestation, `opencode.db` as kaizen contract). `opencode.json` MUST NOT be an active contract of model, MCP, or permission. `.cursor/rules/harness.mdc` SHALL identify the Cursor client (hooks + juízo/execução Task models) and MUST NOT repeat the δ table or the 12-column runbook. The fourth harness (dsh) MUST NOT be a source of law.

#### Scenario: Fresh checkout loads Cursor config
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** project rules, OpenSpec skills/commands and the Impeccable hook are available from `.cursor/`
- **AND** no Cursor instruction requires `opencode.json` as a model/MCP/permission contract

#### Scenario: No secrets in versioned harness files
- **WHEN** `.cursor/` is inspected
- **THEN** no token, key or credential is present in versioned files

#### Scenario: harness.mdc is Cursor identity not the law
- **WHEN** `.cursor/rules/harness.mdc` is counted excluding the YAML frontmatter
- **THEN** the body names Cursor hooks and juízo/execução (or the covenant-flow runbook)
- **AND** it does not contain a T0–T17 table or `release-guard`
- **AND** it does not say that every Task inherits the parent picker

### Requirement: Role models by juízo and execução
On the Cursor client, isolated Task children SHALL use the role model passed as the Task `model` parameter on both spawn paths (named `subagent_type` or `generalPurpose` with the agent-file body pasted). They MUST NOT inherit the parent chat picker. Juízo (grill-card, Design-autor, Design-critic, Assessment A/B) SHALL use Grok 4.6 (`cursor-grok-4.6-high`). Execução (Apply-coluna, QA, `diff-reviewer`, `code-reviewer`, same-card explore/search, fecho-lote) SHALL use Composer 2.5 (`composer-2.5`). `composer-2.5-fast` MUST NOT be used. Reviewers on Grok MUST NOT be used by this change. The git MUST NOT force the parent picker; the runbook MUST NOT recommend a picker to the parent. Grok Build, OpenCode, and dsh children SHALL keep inherit. The law is the spawn parameter; agent-file YAML `model` is a redundant pin.

#### Scenario: Juízo spawn asks for Grok
- **WHEN** the session spawns grill-card, Design-autor, Design-critic, or Assessment A/B on Cursor
- **THEN** the Task `model` is `cursor-grok-4.6-high`
- **AND** the child MUST NOT inherit the parent picker

#### Scenario: Execução spawn asks for Composer
- **WHEN** the session spawns Apply-coluna, QA, `diff-reviewer`, `code-reviewer`, same-card explore, or fecho-lote on Cursor
- **THEN** the Task `model` is `composer-2.5`
- **AND** it MUST NOT require `composer-2.5-fast` or Grok for those roles

#### Scenario: Other clients keep inherit
- **WHEN** Grok Build, OpenCode, or dsh stubs are read
- **THEN** they still map children to inherit
- **AND** they MUST NOT copy the Cursor role table

### Requirement: Design gate is process-based
While `Status=Design`, the **parent** session SHALL spawn an isolated Design-author child (Grok 4.6 / `cursor-grok-4.6-high`, no parent transcript) to write OpenSpec artifacts and a navigable prototype when UI-impacting. After those artifacts exist, the parent SHALL spawn Assessment A and B as a wave (MUST NOT nest A/B inside the Design child) with the same juízo model. Isolated critics MUST NOT edit product code, `design.md`, or prototype files. They MAY write only `.impeccable/critique/**`. The parent MUST NOT author OpenSpec proposal/specs/tasks, prototype files, or `design.md` **except** that after A/B return with zero open P0/P1 the parent MUST write only the `## Design Critique` section (bullets, disposition, verdict, snapshot path). Open P0/P1 SHALL re-spawn the Design-author child with those findings in the prompt; the parent MUST NOT polish. `process_event submeter_design` SHALL stay on the parent. The agent MUST NOT implement product code until `Status=Pronto para Dev`.

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

#### Scenario: Design-author does not inherit the picker
- **WHEN** the parent spawns the Design-author child on Cursor
- **THEN** the Task `model` is `cursor-grok-4.6-high`
- **AND** the spawn MUST NOT inherit the parent picker

### Requirement: Code Review happy path MUST use Composer execução model
The versioned `diff-reviewer` and `code-reviewer` Tasks MUST use `composer-2.5` on both spawn paths (named `subagent_type` or `generalPurpose` with the agent-file body). They MUST NOT inherit the parent picker and MUST NOT use Grok or `composer-2.5-fast`. Cursor Bugbot (`/review-bugbot`) MUST NOT be part of the product or the Code Review happy path. `/review-security` MAY run when Alan explicitly asks; it MUST NOT replace the local reviewers as the gate. Review constraints SHALL live in the two agent files (and optional consumer `REVIEW.md` without Bugbot), not in `BUGBOT.md`. Agent-file YAML MAY pin `model: composer-2.5`; the law remains the Task parameter.

#### Scenario: Local reviewers use Composer execução
- **WHEN** Code Review spawns `.cursor/agents/diff-reviewer.md` or `.cursor/agents/code-reviewer.md`
- **THEN** the child MUST use `composer-2.5`
- **AND** the spawn MUST NOT omit `model` or pass `inherit`

#### Scenario: Bugbot is not a product path
- **WHEN** Code Review runs on a pinned consumer
- **THEN** `/review-bugbot` MUST NOT run as the gate
- **AND** `BUGBOT.md` MUST NOT be required

### Requirement: Always-on harness rule is 8-15 body lines
`.cursor/rules/harness.mdc` SHALL remain `alwaysApply: true`. Its body (non-empty lines after the YAML frontmatter) MUST contain between 4 and 12 lines. The body SHALL identify the Cursor client: hooks under `.cursor/hooks.json`, juízo = Grok 4.6 and execução = Composer 2.5 without inheriting the picker, a pointer to skill `covenant-flow` for the table, and that the always-on δ lives in `AGENTS.md`. It MUST NOT include the Code Review reviewer procedure, the OpenSpec Gist republication helper, the release closeout, a T0–T17 table, a restatement of I1–I9, or the role table itself.

#### Scenario: harness.mdc body budget
- **WHEN** `.cursor/rules/harness.mdc` is counted excluding the YAML frontmatter
- **THEN** non-empty body lines are between 4 and 12 inclusive
- **AND** the body mentions juízo/execução or Cursor hooks
- **AND** the body does not mention `diff-reviewer` or `release-guard`
- **AND** the body does not claim Grok Auto
- **AND** the body does not say that every Task inherits the parent picker
