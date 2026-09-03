# cursor-harness Specification

## Purpose
Contrato do adapter Cursor sobre o núcleo do processo (yaml + `scripts/process-fsm/` + `AGENTS.md`). Grok Build é o adapter irmão em `.grok/`; OpenCode 1.18.18 em `.opencode/plugin/`.
## Requirements
### Requirement: Cursor is the versioned development harness
The repository SHALL contain a versioned Cursor **adapter** under `.cursor/` (rules, skills, commands, hooks) that compiles the process nucleus (`.cursor/process-fsm.yaml` + `scripts/process-fsm/` + root `AGENTS.md`). Cursor is not the only versioned client: Grok Build has a sibling adapter under `.grok/`, OpenCode 1.18.18 has a sibling adapter under `.opencode/plugin/` (auto-load; no `opencode.json`), and dsh has a sibling adapter under `.dsh/plugin/` (Cordis native; no Claude `hooks.json` Guard). The repo MUST NOT restore the lock machine (`design_spawn_stage`, `design_artifact_write`, lease, packet, attestation, `opencode.db` as kaizen contract). `opencode.json` MUST NOT be an active contract of model, MCP, or permission. `.cursor/rules/harness.mdc` SHALL identify the Cursor client (hooks + Task `inherit`) and MUST NOT repeat the δ table or the 12-column runbook. The fourth harness (dsh) MUST NOT be a source of law.

#### Scenario: Fresh checkout loads Cursor config
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** project rules, OpenSpec skills/commands and the Impeccable hook are available from `.cursor/`
- **AND** no Cursor instruction requires `opencode.json` as a model/MCP/permission contract

#### Scenario: No secrets in versioned harness files
- **WHEN** `.cursor/` is inspected
- **THEN** no token, key or credential is present in versioned files

#### Scenario: harness.mdc is Cursor identity not the law
- **WHEN** `.cursor/rules/harness.mdc` is counted excluding the YAML frontmatter
- **THEN** the body names Cursor hooks and Task `inherit`
- **AND** it does not contain a T0–T17 table or `release-guard`

### Requirement: OpenSpec flow is available in Cursor
Cursor SHALL load OpenSpec skills and `/opsx-*` commands that invoke the same `openspec` CLI used by the project.

#### Scenario: OPSX commands available
- **WHEN** the user invokes `/opsx-new`, `/opsx-ff`, `/opsx-apply`, `/opsx-verify` or `/opsx-archive`
- **THEN** the corresponding Cursor command runs the OpenSpec CLI flow
- **AND** it MUST NOT invent artifacts outside `openspec instructions`

### Requirement: Chat-selected model runs every role
The Cursor chat model SHALL be the source of truth for Design, implementation, review and vision. Subagents MUST inherit that model unless Alan explicitly selects another model in the chat or Task.

#### Scenario: Default inheritance
- **WHEN** the session spawns a Task for critique or review
- **THEN** the child uses `inherit` (same chat model)
- **AND** it MUST NOT require `openai/gpt-5.6-sol` or `opencode-go/*` models

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

### Requirement: Code Review happy path MUST inherit the chat model
The versioned `diff-reviewer` and `code-reviewer` Tasks MUST use `inherit` unless Alan selects another model in chat. Cursor Bugbot (`/review-bugbot`) MUST NOT be part of the product or the Code Review happy path. `/review-security` MAY run when Alan explicitly asks; it MUST NOT replace the local reviewers as the gate. Review constraints SHALL live in the two agent files (and optional consumer `REVIEW.md` without Bugbot), not in `BUGBOT.md`.

#### Scenario: Local reviewers inherit
- **WHEN** Code Review spawns `.cursor/agents/diff-reviewer.md` or `.cursor/agents/code-reviewer.md`
- **THEN** the child MUST use `inherit` (same chat model)

#### Scenario: Bugbot is not a product path
- **WHEN** Code Review runs on a pinned consumer
- **THEN** `/review-bugbot` MUST NOT run as the gate
- **AND** `BUGBOT.md` MUST NOT be required

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
`.cursor/rules/harness.mdc` SHALL remain `alwaysApply: true`. Its body (non-empty lines after the YAML frontmatter) MUST contain between 4 and 12 lines. The body SHALL identify the Cursor client: hooks under `.cursor/hooks.json`, Task `inherit`, and that the always-on δ lives in `AGENTS.md`. It MUST NOT include the Code Review reviewer procedure, the OpenSpec Gist republication helper, the release closeout, a T0–T17 table, or a restatement of I1–I9.

#### Scenario: harness.mdc body budget
- **WHEN** `.cursor/rules/harness.mdc` is counted excluding the YAML frontmatter
- **THEN** non-empty body lines are between 4 and 12 inclusive
- **AND** the body mentions Task `inherit` or Cursor hooks
- **AND** the body does not mention `diff-reviewer` or `release-guard`
- **AND** the body does not claim Grok Auto

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

