# cursor-harness Specification

## Purpose
Contrato do adapter Cursor sobre o núcleo do processo (yaml + `scripts/process-fsm/` + `AGENTS.md`). Grok Build é o adapter irmão em `.grok/`; OpenCode 1.18.18 em `.opencode/plugin/`.
## Requirements
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

### Requirement: OpenSpec flow is available in Cursor
Cursor SHALL load OpenSpec skills and `/opsx-*` commands that invoke the same `openspec` CLI used by the project.

#### Scenario: OPSX commands available
- **WHEN** the user invokes `/opsx-new`, `/opsx-ff`, `/opsx-apply`, `/opsx-verify` or `/opsx-archive`
- **THEN** the corresponding Cursor command runs the OpenSpec CLI flow
- **AND** it MUST NOT invent artifacts outside `openspec instructions`

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

### Requirement: Cursor loads the current environments skill
The Cursor harness SHALL treat `covenant-flow-environments` as the environment map and SHALL NOT treat OpenClaw Gateway as the active runtime in that skill. Environment **values** SHALL come from the consumer overlay, not from the packaged skill.

#### Scenario: Skill available in Cursor
- **WHEN** a Cursor session starts a task that can affect DEV or PROD
- **THEN** the skill file is `.cursor/skills/covenant-flow-environments/SKILL.md` (regular file, not a hermes symlink)
- **AND** DEV/PROD URLs, db, and services are read from overlay `environments.*`
- **AND** OpenClaw is not an active runtime
- **AND** Hermes is not required as the only map (first consumer Cripto supplies its own overlay values)

### Requirement: Workflow skills are versioned files in the GitHub repo
The Cursor harness SHALL load `covenant-flow`, `covenant-flow-environments` and `github-project-board` from `.cursor/skills/<name>/SKILL.md` as regular files in the consumer git (first consumer: `oalansilva/crypto` after pin). Agents MUST NOT treat `~/.codex/skills/` or `/srv/knowledge/hermes-second-brain/skills/` as the canonical load path for these skills. Git file mode SHALL NOT be symlink (`120000`). After unique pin, `alan-workflow*` MUST NOT remain the canonical names in consumer git.

#### Scenario: Fresh clone
- **WHEN** a Cursor session starts from a GitHub checkout of a uniquely pinned consumer
- **THEN** the `SKILL.md` files exist in `.cursor/skills/covenant-flow/` and `.cursor/skills/covenant-flow-environments/` without resolving a symlink to hermes
- **AND** docs instruct preferring the repo path over Codex compatibility discovery

### Requirement: Column gate is always-on; full workflow is a skill
The always-on layer SHALL be the short root `AGENTS.md` plus the client paging (Cursor: `sessionStart` Moore page; Grok: generated `.grok/rules/` page). It MUST state that `Em Refinamento` is the entry column, Todo is not implementation, and Design columns must not be skipped. The detailed 12-column runbook SHALL live in the `covenant-flow` skill (on-demand). Chat requests such as `implemente` SHALL NOT authorize `/opsx:apply` or product code while `Status=Todo`. The always-on layer MUST NOT include the overlay body (`overlay_doc`, Cripto: `docs/crypto-overlay.md`).

#### Scenario: Chat says implement all Todo cards
- **WHEN** the user asks to implement cards in `Status=Todo`
- **THEN** the agent SHALL start Design (OpenSpec + critique + Gist), not `/opsx:apply` or product code

#### Scenario: Todo session does not load release playbook
- **WHEN** a session starts bound to a card with `Status=Todo`
- **THEN** always-on context is `AGENTS.md` plus `context_file[Todo]`
- **AND** it MUST NOT include the release-guard closeout playbook

### Requirement: OpenSpec Gist is a Design gate
The agent SHALL NOT move a card to `Aprovação de Design` until a secret Gist (`crypto openspec <change>`) with proposal/design/tasks/specs is published and the card has a comment with the Gist URL. HTML prototypes MUST NOT be in the Gist. Republication SHALL reuse `--gist-id` and `--comment-id`.

#### Scenario: Design without Gist
- **WHEN** design.md and critique exist but the card has no OpenSpec Gist comment
- **THEN** Design remains incomplete; the card MUST stay in `Design`

### Requirement: Card first; OpenSpec is the complete refinement for Dev
The GitHub issue MAY originate the work. OpenSpec artifacts SHALL be a superset of every implementation-relevant decision on the issue. `/opsx:apply` SHALL use OpenSpec/Gist as the implementation contract, not the issue body as a parallel spec.

#### Scenario: Issue richer than OpenSpec
- **WHEN** the GitHub issue body contains design decisions missing from `design.md` / specs
- **THEN** the agent SHALL merge those decisions into OpenSpec, republish the same Gist, and MUST NOT move to `Aprovação de Design` until the Gist is the superset

#### Scenario: Dev implements
- **WHEN** `Status=Pronto para Dev` and `/opsx:apply` runs
- **THEN** the agent SHALL follow `openspec/changes/<change>/` and the published Gist
- **AND** SHALL NOT treat a richer issue body as authorization to skip a task missing from `tasks.md`

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

### Requirement: Agent moves Status only via process_event
While this change is active, the Cursor Agent MUST NOT invoke `gh project item-edit` (or GraphQL `updateProjectV2ItemFieldValue`) to change Project 1 `Status`. Named transitions SHALL go through `scripts/process-fsm/process_event.py`. Chat utterances such as `implemente`, `autorizo`, or `arrastei` MUST NOT be treated as `aprovar_design` / T7.

#### Scenario: Chat implemente is not T7
- **WHEN** the user says `implemente` and `Status` is not `Pronto para Dev`
- **THEN** the Agent MUST NOT call `process_event aprovar_design` as a successful transition
- **AND** MUST NOT `item-edit` Status

#### Scenario: implemente in Pronto para Dev is iniciar_apply
- **WHEN** the user says `implemente` and `Status` is `Pronto para Dev`
- **THEN** the Agent SHALL call `process_event iniciar_apply` (not `aprovar_design`)
- **AND** SHALL NOT `item-edit` Status

#### Scenario: Legal apply uses process_event
- **WHEN** `Status=Pronto para Dev` and the Agent starts implementation
- **THEN** the Agent SHALL call `process_event iniciar_apply` before product Write
- **AND** SHALL NOT treat the function return as a Write allow token

### Requirement: Cursor hooks.json registers the compiled Write Guard
`.cursor/hooks.json` SHALL register a `preToolUse` command hook whose matcher covers `Write`, `StrReplace`, `Delete`, and `EditNotebook`, invoking the process-fsm Guard adapter. The same adapter SHALL be registered on `beforeShellExecution` for mutating shell writes. `failClosed` MUST be `true` on the `preToolUse` Write-family hook and MUST NOT be `true` on `beforeShellExecution`. Existing Impeccable hooks (`afterFileEdit` and `stop` calling `.cursor/hooks/impeccable.sh`) MUST remain. The adapter MUST emit valid JSON even if Python/PyYAML fails (bash fallback: deny `product_globs`, allow `design_globs` on `card-<id>-*`).

#### Scenario: Write tools are guarded
- **WHEN** a Cursor Agent issues `Write` or `StrReplace` on a product path
- **THEN** `.cursor/hooks.json` runs the process-fsm Guard before the tool executes

#### Scenario: Impeccable is composed not replaced
- **WHEN** `.cursor/hooks.json` is loaded
- **THEN** `afterFileEdit` and `stop` still invoke `.cursor/hooks/impeccable.sh`
- **AND** the Guard command is a distinct entry from the Impeccable adapter

#### Scenario: Shell mutating writes use the same Guard
- **WHEN** `.cursor/hooks.json` is loaded
- **THEN** `beforeShellExecution` invokes the same Guard adapter as `preToolUse`
- **AND** `failClosed` is not true on that shell hook

### Requirement: Root AGENTS.md is a stub; overlay is on-demand
The repository root `AGENTS.md` SHALL be a stub of at most 40 non-empty lines that points to the consumer `overlay_doc` (Cripto: `docs/crypto-overlay.md`) for ports/URLs, Drive, PostgreSQL, and release-guard/lote/PROD, MUST include the board URL generated from overlay `board.owner` and `board.number` (Cripto: `github.com/users/oalansilva/projects/1`), and MUST carry the short always-on δ (resolve the tuple, chat ≠ δ, Todo ≠ código, Alan-only T1/T7/T15, clients Cursor, Grok Build, and OpenCode). The long overlay body SHALL live at `overlay_doc` (not always-injected). Agents MUST `Read` that overlay only when the task needs those topics. The stub MUST NOT contain the 12-column runbook, `release-guard pre`/`post` snippets, or deploy PROD procedure. The stub MUST NOT claim Auto OpenCode or Auto Grok.

#### Scenario: Fresh session does not ingest the overlay body from AGENTS.md
- **WHEN** the root `AGENTS.md` is read as the always-on workspace file
- **THEN** it has at most 40 non-empty lines
- **AND** it does not contain `scripts/release-guard pre` or the 12-column path as a procedure
- **AND** it names the consumer `overlay_doc` as the on-demand overlay
- **AND** it contains a board URL derived from overlay board fields (Cripto: `github.com/users/oalansilva/projects/1`)

#### Scenario: Stub names three clients and the tuple
- **WHEN** the root `AGENTS.md` is read
- **THEN** it mentions Cursor Agent, Grok Build, and OpenCode
- **AND** it tells the agent to resolve `(q, bound_card, q_git)`
- **AND** it states that chat wording is not authorization
- **AND** it does not claim OpenCode Auto or Grok Auto

### Requirement: Always-on harness rule is 8-15 body lines
`.cursor/rules/harness.mdc` SHALL remain `alwaysApply: true`. Its body (non-empty lines after the YAML frontmatter) MUST contain between 4 and 12 lines. The body SHALL identify the Cursor client: hooks under `.cursor/hooks.json`, juízo = Grok 4.6 and execução = Composer 2.5 without inheriting the picker, a pointer to skill `covenant-flow` for the table, and that the always-on δ lives in `AGENTS.md`. It MUST NOT include the Code Review reviewer procedure, the OpenSpec Gist republication helper, the release closeout, a T0–T17 table, a restatement of I1–I9, or the role table itself.

#### Scenario: harness.mdc body budget
- **WHEN** `.cursor/rules/harness.mdc` is counted excluding the YAML frontmatter
- **THEN** non-empty body lines are between 4 and 12 inclusive
- **AND** the body mentions juízo/execução or Cursor hooks
- **AND** the body does not mention `diff-reviewer` or `release-guard`
- **AND** the body does not claim Grok Auto
- **AND** the body does not say that every Task inherits the parent picker

### Requirement: alan-workflow skill priority is delta and Guard first
`.cursor/skills/covenant-flow/SKILL.md` SHALL declare priority order **δ and Guard > overlay > skill > wording**. Chat utterances such as `implemente` MUST be classified as wording (lowest). Overlay (`overlay_doc`, Cripto: `docs/crypto-overlay.md`) MUST be loaded only when ports, Drive, PostgreSQL, or release are in scope.

#### Scenario: Skill lists inverted priority
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` is opened
- **THEN** the priority list places δ/Guard before overlay, overlay before the skill runbook, and wording last
- **AND** it no longer lists “Instrução direta de Alan no chat” as item 1 ahead of δ

### Requirement: Pronto closeout is process_event fechar_release
After an explicit release request, the Agent SHALL publish (`main`, deploy PROD, docs) using the overlay and `release-guard`. Closing Homologado → Pronto SHALL be `process_event fechar_release` with live `M_lote` (`release-guard post` PASS) for the `RELEASE_CARDS` package. The Agent MUST NOT treat `gh project item-edit` of Status or a chat `suba a release` / `autorizo Pronto` as T16. `priorizar`, `aprovar_design`, and `homologar` remain Alan-only. Always-on `AGENTS.md` SHALL say Alan-only is T1/T7/T15 (not T16). `.cursor/rules/harness.mdc` MUST NOT restate that table.

#### Scenario: Agent closes Homologado to Pronto after post PASS
- **WHEN** the package cards are Homologado, `release-guard post` exits 0, and the Agent runs `process_event fechar_release`
- **THEN** each package card moves to Pronto
- **AND** the Agent does not edit Project 1 Status via `gh project item-edit`

#### Scenario: Chat does not close Pronto
- **WHEN** the user says `implemente` or `autorizo Pronto` without `process_event fechar_release` succeeding
- **THEN** Status MUST remain Homologado

#### Scenario: Alan-only lives in AGENTS.md not harness.mdc
- **WHEN** `AGENTS.md` and `.cursor/rules/harness.mdc` are read
- **THEN** `AGENTS.md` states Alan-only T1/T7/T15
- **AND** `harness.mdc` does not contain the string `T1/T7/T15` as the always-on law

### Requirement: Em Refinamento story sharpening uses grill-card
The Cursor harness SHALL load `.cursor/skills/grill-card/SKILL.md` and `.cursor/skills/grilling/SKILL.md` as regular files in the consumer git. `covenant-flow` SHALL describe Em Refinamento as intake **and** story grilling (issue body ledger, T1 Alan-only). `github-project-board` SHALL state the same for the Em Refinamento column. Agents MUST NOT treat `grill-with-docs` or `to-spec` as the project entry skill.

#### Scenario: Fresh clone has adapter and primitive
- **WHEN** a Cursor session starts from a GitHub checkout of a uniquely pinned consumer
- **THEN** `.cursor/skills/grill-card/SKILL.md` and `.cursor/skills/grilling/SKILL.md` exist and are not mode `120000`
- **AND** `covenant-flow` names `grill-card` for Em Refinamento

#### Scenario: Design synthesizes a grilled issue
- **WHEN** `Status=Design` and the bound issue body contains the grill-card DoD sections
- **THEN** `/opsx:new` / `/opsx:ff` SHALL use that issue as briefing and MUST NOT start a new interview
- **AND** MUST NOT invoke `grill-card` or `grill-with-docs` as a step to generate `proposal.md`

#### Scenario: Incomplete DoD in Design
- **WHEN** `Status=Design` and the bound issue body is missing any grill-card DoD section
- **THEN** the agent MUST NOT run `/opsx:ff` and MUST NOT invent story text
- **AND** SHALL comment the missing sections and remain in Design
- **AND** `/opsx:explore` MAY run only for technical codebase questions, not to rewrite product scope

#### Scenario: Em Refinamento page mentions grilling the issue
- **WHEN** a session starts bound to a card with `Status=Em Refinamento`
- **THEN** `context_file[Em Refinamento]` instructs issue clarification / grill-card and that chat is not T1

### Requirement: Parent grill relay presents all host options
`.cursor/skills/covenant-flow/SKILL.md` SHALL include, in the Grill-card section, a line that the **parent** calls the host tool with **all** `options[]` of each closed question and MUST NOT collapse the card to the recommended option. The parent SHALL map the child's listed alternatives 1:1 into `options[]` in the same order, recommended first (Cursor `AskUserQuestion`, Grok `ask_user_question`). The isolated grill child MUST NOT call the host tool. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry, MUST NOT edit `process-fsm.yaml` as a side effect of this relay line, and MUST NOT name the host tool in `.grok/skills/*` stubs.

#### Scenario: Parent relays every closed-question option
- **WHEN** the grill child returns closed questions with listed options on Grok or Cursor
- **THEN** the parent SHALL call the host tool and re-present all of those options
- **AND** MUST NOT present only the `➡️` / recommended option
- **AND** `covenant-flow` SHALL contain that relay line in the Grill-card section

#### Scenario: No FSM change for host-option relay
- **WHEN** this change is applied
- **THEN** `process-fsm.yaml` law table is unchanged by the relay line
- **AND** `AGENTS.md` always-on does not grow with this rule

### Requirement: One chat per column on both clients
The Cursor and Grok runbooks SHALL require one chat per card titled `#<id>` from Em Refinamento through Done técnico. The parent MUST spawn isolated activity children (grill, Design author, Apply column, QA) and dual-reviewer / dual-critic waves. The parent MUST refuse to execute those activities itself and MUST NOT ask for a new chat titled `#<id> <coluna>`. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry.

#### Scenario: Design chat refuses apply
- **WHEN** the bound card is in `Status=Design` and the operator asks to `/opsx:apply` or implement product code
- **THEN** that request is refused in the same transcript
- **AND** the agent does not ask for a new chat titled `#<id> Apply`
- **AND** it states Apply waits for `Pronto para Dev` (T7 Alan)

#### Scenario: Both clients carry the same refusal
- **WHEN** `covenant-flow` is followed in Cursor or via the Grok stub
- **THEN** both clients document `#id` per card, activity children, and same-chat refusal
- **AND** `process-fsm.yaml` has no new event for this rule

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

### Requirement: Apply does not ingest the whole OpenSpec dump
`.cursor/skills/openspec-apply-change/SKILL.md` SHALL instruct the agent, for each pending task, to read that task, the matching capability spec, and the short apply sections of `design.md`. It MUST NOT instruct the agent to read every `contextFiles` path as a single dump. It MUST NOT instruct reading `.impeccable/critique/`. For `UI impact: affected`, the skill still requires reading the prototype file on disk before product UI edits.

#### Scenario: Apply skill no longer dumps every context file
- **WHEN** `/opsx:apply` starts a task
- **THEN** the skill tells the agent to load the current task, the matching spec, and short `design.md` apply sections
- **AND** the skill does not say to read every `contextFiles` path before starting

### Requirement: OpenCode lock machine stays dead
While OpenCode 1.18.18 is an active adapter, Design and Apply flows MUST NOT require `design_spawn_stage`, `design_artifact_write`, lease evidence, packet, or OpenCode 1.18.18 attestation. Decision-log for this change SHALL revoke only the #562 uniqueness of Cursor as the sole operational harness; it MUST NOT revoke the death of the lock machine.

#### Scenario: Design in OpenCode does not require lease
- **WHEN** Design runs in OpenCode 1.18.18
- **THEN** the flow MUST NOT require `design_spawn_stage`, `design_artifact_write`, lease evidence, or attestation

### Requirement: Parent closes Done in the same turn as green QA
While `Status=Code Review` or `Status=QA` and the card is bound to `card-<id>-*`, the Cursor **parent** SHALL require a pull request from `q_git` into `develop` before `process_event aceitar_sha`. Without that PR, `aceitar_sha` MUST be treated as reject `no_pr` and the parent MUST open the PR in the same turn and retry `aceitar_sha`. The parent MUST NOT treat local unit tests or `openspec validate` as Done. After `aceitar_sha` moves QA, the parent MAY spawn one isolated QA child that reads checks and MUST NOT call `process_event`. When that child returns green, or when the parent itself sees `qa-gate` success, the parent MUST call `process_event integrar_develop` in the **same turn**. A reject `qa-gate pending` MUST wait for the check and retry `integrar_develop` in that turn. A reject `sync: dirty` or `no_pr` is visible and is not the end of the turn by itself. The Agent MUST NOT `gh project item-edit` Status to QA or Done.

#### Scenario: T11 without PR is retried after opening the PR
- **WHEN** the parent is in Code Review, reviewers are accepted, and no PR from `q_git` into `develop` exists
- **THEN** `process_event aceitar_sha` rejects with `reason=no_pr`
- **AND** the parent opens the PR and retries `aceitar_sha` in the same turn
- **AND** Status is not moved via `item-edit`

#### Scenario: Green QA child is followed by T14 in the same turn
- **WHEN** the card is in QA, the QA child reports `qa-gate` success, and the canonical source is clean
- **THEN** the parent calls `process_event integrar_develop` in that turn
- **AND** the QA child does not call `process_event`

#### Scenario: Pending qa-gate retries T14
- **WHEN** `integrar_develop` returns `reason=qa-gate pending`
- **THEN** the parent waits for the check and retries `integrar_develop` in the same turn
- **AND** it does not treat the first reject as the end of the turn

### Requirement: Cursor Impeccable afterFileEdit and stop are cwd-independent
`.cursor/hooks.json` SHALL keep `afterFileEdit` and `stop` as distinct Impeccable entries that invoke `.cursor/hooks/impeccable.sh` (event names `afterFileEdit` and `stop`). Those command strings MUST locate the script with the same class as the Grok JSON locator: repo-relative `.cursor/hooks/impeccable.sh`, sibling `./hooks/impeccable.sh` or `./impeccable.sh`, then `git rev-parse --show-toplevel` + `.cursor/hooks/impeccable.sh`. Running each command with cwd at the repo root, at `.cursor/`, or at `.cursor/hooks/` MUST exit 0. Cursor `preToolUse` (failClosed Write-family), `beforeShellExecution`, and `sessionStart` MUST remain the existing Guard / paging commands and MUST NOT be rewritten by this requirement. The adapter MUST still emit fail-open for the detector (a finding or crash of `hook.mjs` MUST NOT abort the turn). Dual-write of T0–T17 into `.cursor/rules/` remains forbidden.

#### Scenario: afterFileEdit resolves from three Cursor cwds
- **WHEN** the `afterFileEdit` command in `.cursor/hooks.json` runs via `sh -c` with cwd at the repo root, at `.cursor/`, and at `.cursor/hooks/`
- **THEN** each invocation exits 0
- **AND** `.cursor/hooks/impeccable.sh` is the script that runs

#### Scenario: stop resolves from three Cursor cwds
- **WHEN** the `stop` command in `.cursor/hooks.json` runs via `sh -c` with those same three cwds
- **THEN** each invocation exits 0

#### Scenario: Guard and sessionStart stay composed not replaced
- **WHEN** `.cursor/hooks.json` is loaded after this change
- **THEN** `preToolUse` command is still `.cursor/hooks/process-fsm-guard.sh` with `failClosed` true
- **AND** `beforeShellExecution` command is still `.cursor/hooks/process-fsm-guard.sh` without `failClosed` true
- **AND** `sessionStart` command is still `.cursor/hooks/process-fsm-session-start.sh`
- **AND** `afterFileEdit` and `stop` remain distinct from the Guard entries

### Requirement: Parent binds visible root; isolated child never calls move_agent_to_root
On Cursor, the **parent** SHALL bind the operator-visible workspace root to the card worktree `card-<id>-*` after that tree exists. An isolated activity child MUST NOT call MCP `move_agent_to_root`. On modo Desktop+SSH Windows to this VM the parent MUST NOT call `move_agent_to_root` either (witness 2026-09-09: `Failed to move agent root: InstantiationService has been disposed`). In that mode the parent SHALL open a new Remote-SSH window at the worktree URI with chat title `#<id>` and MUST NOT ask for `#<id> Apply`. Children SHALL still use `working_directory` equal to the worktree; that parameter MUST NOT replace a visible-root bind.

#### Scenario: Isolated child does not move agent root
- **WHEN** a grill, Design-author, Apply, review, or QA child runs
- **THEN** its prompt forbids `move_agent_to_root`
- **AND** Write/Shell in that child use the worktree path without changing the live workbench root

#### Scenario: Desktop plus SSH parent skips the broken MCP
- **WHEN** the Cursor parent on Windows Desktop + SSH to this VM needs the card folder as visible root
- **THEN** it does not call `move_agent_to_root`
- **AND** a retry of that MCP after InstantiationService disposed is also forbidden

### Requirement: Flow Shell on this Desktop plus SSH pair does not wait for an extra click
Flow commands of the Cursor runbook (git, `process_event`, harness pytest) executed in a `card-<id>-*` worktree on Windows Desktop + SSH to this VM SHALL request `required_permissions: ["all"]` on the first Shell of the turn. Isolation `workspace_readwrite` that fails Landlock/`uid_map` (`Failed to write /proc/self/uid_map`) MUST NOT be the first attempt of a passing flow command. The failure MUST stay visible; a blank workbench without explanation is not a pass. This requirement MUST NOT add a FSM event, MUST NOT grow always-on `AGENTS.md`, and MUST NOT set overlay `clients.*.auto`.

#### Scenario: All on the first attempt
- **WHEN** T8 or a later flow Shell runs in the card worktree on this Desktop+SSH pair
- **THEN** the Shell payload includes `required_permissions: ["all"]` before Landlock is tried
- **AND** the operator does not click an extra approval to finish the command

#### Scenario: No pin and no auto overlay for sandbox
- **WHEN** this change is applied
- **THEN** it does not bump overlay `pin` solely for host sandbox
- **AND** it does not write `clients.*.auto`

### Requirement: Host interrupt of a Cursor child is not success
A Cursor Task/subagent for a stage child SHALL be treated as success only when the host reports `completed` and the child return payload is present. `Task was interrupted by the user` without a visible operator Stop in that turn SHALL be classified as host kill and MUST NOT satisfy the stage. The parent MUST NOT run the stage itself on Desktop to compensate. Destape after a child already completed stays #879.

#### Scenario: Interrupted Apply child is not T8 success
- **WHEN** an Apply child ends with `Task was interrupted by the user after` a duration and the operator did not Stop
- **THEN** the parent MUST NOT treat Apply as done
- **AND** it MUST NOT implement the remaining tasks in the parent Desktop transcript

### Requirement: Cursor subagentStop destapes a mute parent after a completed waited child
`.cursor/hooks.json` SHALL register a `subagentStop` command hook invoking `.cursor/hooks/process-fsm-subagent-stop.sh`, which SHALL run `scripts/process-fsm/subagent_stop.py`. The hook MUST NOT set `failClosed` true. Matcher MUST be `generalPurpose|diff-reviewer|code-reviewer` (one entry or equivalent) and MUST include `generalPurpose`, `diff-reviewer`, and `code-reviewer`. `loop_limit` MUST be `32`. The repo MUST NOT register `subagentStart` for destape. Existing `sessionStart`, Guard (`preToolUse` failClosed Write-family, `beforeShellExecution` without failClosed), and Impeccable (`afterFileEdit`, `stop`) entries MUST remain. Grok, OpenCode, and dsh adapters MUST NOT receive this destape hook as a dual-write of T0–T17. Overlay `clients.*.auto` MUST remain `false`. Root `AGENTS.md` MUST NOT grow with this rule. `.cursor/process-fsm.yaml` MUST NOT gain a state, event, or `enabled_tools` entry from this requirement.

The hook SHALL emit JSON `followup_message` only when all of the following hold: stdin `status` is `completed`; `loop_count` is `0`; sidecar `.cursor/tmp/awaiting-task.json` exists and its fingerprint matches this stop's `task`/`description` (parent still waiting for the same Task); the child classifies as one of the four Cursor etapas (grelha / `grill-card`, Apply / `apply-coluna`, `diff-reviewer` / `code-reviewer`, QA / `qa-gate`) **or** a Design child (Design-autor / `design-autor`, Design-crítico sem-tela / `design-critic`, Assessment A/B). Classification MUST use only sidecar `description` ∪ stop `task` (the short title) ∪ `subagent_type`. It MUST NOT classify from the long prompt body (`description`). The classifier MUST NOT treat the bare word `Design` as a match. Design-autor SHALL match before crítico/A/B. Otherwise it SHALL emit `{}`. `error` and `aborted` MUST emit `{}`. A child still running MUST emit `{}`. `explore` and `shell` MUST emit `{}`. `is_parallel_worker: true` (when present) MUST emit `{}`. A crash or invalid JSON MUST fail-open (`{}`), not block the turn.

The `followup_message` SHALL be an order to finish the etapa, never a status question. It MUST NOT contain `concluiu?`, `já acabou?`, or `verifique se nao concluiu`. Exact payloads:
- grelha: `O filho grill já devolveu. Faz o relaying das Qs / handoff T1 agora. Não perguntes se concluiu. Não spawnes outro grill.`
- Apply: `O filho Apply já devolveu. Segue para o review: materializa o diff e spawna diff-reviewer + code-reviewer. Não perguntes se concluiu.`
- review: `O filho reviewer já devolveu. Segue commit / push / PR agora. Não perguntes se concluiu.`
- QA: `O filho QA já devolveu. Fecha o QA conforme o veredito (verde → integrar_develop; falhou → evidência visível). Não perguntes se concluiu.`
- Design-autor: `O filho Design-autor já devolveu. Spawna o crítico (sem-tela) ou a dupla A/B (com-tela). Não perguntes se concluiu. Não spawnes outro autor.`
- Design-crítico / Assessment: `O filho crítico de Design já devolveu. Escreve ## Design Critique, publica o Gist e chama submeter_design. Não perguntes se concluiu.`

`.cursor/skills/covenant-flow/SKILL.md` SHALL tell the Cursor parent, for those four etapas **and** Design-autor / crítico / Assessment A/B, to write the sidecar before the Task and to delete it after handling the result. The hook SHALL delete the sidecar after a poke. Pin overlay `covenant-flow` MUST stay at the existing tag unless a later card bumps it. This destape MUST NOT claim to fire for background children or to cure a host hang. Staff MUST NOT re-prompt while the child is still running.

#### Scenario: Completed grill child destapes with a relay order
- **WHEN** `subagentStop` stdin has `status=completed`, `loop_count=0`, a matching awaiting sidecar, and task/description classifying as grill
- **THEN** stdout JSON includes `followup_message` equal to the grelha order
- **AND** that message does not contain `concluiu?`

#### Scenario: Mute Apply child destapes into Code Review
- **WHEN** the same guards hold and the child classifies as Apply
- **THEN** `followup_message` is the Apply order to materialize the diff and spawn the two local reviewers

#### Scenario: Mute reviewer destapes into commit/push/PR
- **WHEN** the same guards hold and the child classifies as `diff-reviewer` or `code-reviewer`
- **THEN** `followup_message` is the review order to commit / push / PR

#### Scenario: Mute QA child destapes into closeout
- **WHEN** the same guards hold and the child classifies as QA
- **THEN** `followup_message` is the QA order to close according to the child's verdict

#### Scenario: Completed Design-autor destapes into critic or A/B
- **WHEN** the same guards hold and the child classifies as Design-autor
- **THEN** `followup_message` equals `O filho Design-autor já devolveu. Spawna o crítico (sem-tela) ou a dupla A/B (com-tela). Não perguntes se concluiu. Não spawnes outro autor.`
- **AND** that message does not contain `concluiu?`

#### Scenario: Completed Design critic destapes into critique submit
- **WHEN** the same guards hold and the child classifies as Design-crítico sem-tela or Assessment A/B
- **THEN** `followup_message` equals `O filho crítico de Design já devolveu. Escreve ## Design Critique, publica o Gist e chama submeter_design. Não perguntes se concluiu.`
- **AND** that message does not contain `concluiu?`

#### Scenario: Parent already advanced gets no extra poke
- **WHEN** `subagentStop` fires with `status=completed` but `.cursor/tmp/awaiting-task.json` is absent or does not match
- **THEN** stdout is `{}`
- **AND** no `followup_message` is emitted

#### Scenario: Child still running is not destaped
- **WHEN** the child has not reached `subagentStop` with `status=completed`
- **THEN** this hook emits no follow-up
- **AND** it MUST NOT spawn a second child of the same etapa

#### Scenario: Non-completed stop is silent
- **WHEN** stdin `status` is `error` or `aborted`
- **THEN** stdout is `{}`
- **AND** this includes a Design child that aborted (the 27 min critic abort of this session does not destape)

#### Scenario: subagentStart is not registered for destape
- **WHEN** `.cursor/hooks.json` is loaded after this change
- **THEN** it has a `subagentStop` command with `loop_limit` 32 and without `failClosed` true
- **AND** the matcher contains `generalPurpose`, `diff-reviewer`, and `code-reviewer`
- **AND** it has no `subagentStart` destape entry
- **AND** `sessionStart`, Guard, and Impeccable `afterFileEdit`/`stop` remain

#### Scenario: Pasted skill prompt does not reclassify grill
- **WHEN** sidecar is `{"task":"generalPurpose","description":"grill-card 879"}`, stop `task` is `grill-card 879`, `subagent_type` is `generalPurpose`, and stop `description` pastes skill text containing `design-autor` and `diff-reviewer`
- **THEN** `followup_message` is the grelha order
- **AND** it is not the Design-autor order

#### Scenario: Other clients do not receive this destape as law
- **WHEN** a reviewer inspects `.dsh/`, `.grok/`, and overlay `clients.*.auto`
- **THEN** none contains a T0–T17 copy of this destape
- **AND** `clients.*.auto` remains `false`
- **AND** `AGENTS.md` line count does not grow with this rule

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

