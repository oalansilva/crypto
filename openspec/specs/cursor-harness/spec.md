# cursor-harness Specification

## Purpose
Contrato do cliente de desenvolvimento ativo do Cripto Farol: Cursor Agent, com o modelo selecionado no chat em todos os papéis.

## Requirements
### Requirement: Cursor is the versioned development harness
The repository SHALL contain versioned Cursor Agent configuration under `.cursor/` (rules, skills, commands, hooks) and MUST NOT keep OpenCode (`opencode.json`, `.opencode/`) as an active contract.

#### Scenario: Fresh checkout loads Cursor config
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** project rules, OpenSpec skills/commands and the Impeccable hook are available from `.cursor/`
- **AND** no active instruction requires `.opencode/` or `opencode.json`

#### Scenario: No secrets in versioned harness files
- **WHEN** `.cursor/` is inspected
- **THEN** no token, key or credential is present in versioned files

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
While `Status=Design`, the Cursor session SHALL author OpenSpec artifacts and a navigable prototype when UI-impacting, then spawn an isolated same-model critique Task. The agent MUST NOT implement product code until `Status=Pronto para Dev`.

#### Scenario: Isolated critique
- **WHEN** Design evidence is ready
- **THEN** Assessment uses a separate Task instructed not to edit files
- **AND** missing critique keeps the verdict `BLOCKED`

#### Scenario: No OpenCode lock machine
- **WHEN** Design runs in Cursor
- **THEN** the flow MUST NOT require `design_spawn_stage`, `design_artifact_write`, lease evidence or OpenCode 1.18.18 attestation

### Requirement: Cursor loads the current environments skill
The Cursor harness SHALL treat `alan-workflow-ambientes` as the environment map and SHALL NOT treat OpenClaw Gateway as the active runtime in that skill.

#### Scenario: Skill available in Cursor
- **WHEN** a Cursor session starts a task that can affect DEV or PROD
- **THEN** the environments skill is loaded with Hermes as the active agent runtime map
- **AND** the skill file is `.cursor/skills/alan-workflow-ambientes/SKILL.md` in this repo (regular file, not a hermes symlink)

### Requirement: Workflow skills are versioned files in the GitHub repo
The Cursor harness SHALL load `alan-workflow`, `alan-workflow-ambientes` and `github-project-board` from `.cursor/skills/<name>/SKILL.md` as regular files in `oalansilva/crypto`. Agents MUST NOT treat `~/.codex/skills/` or `/srv/knowledge/hermes-second-brain/skills/` as the canonical load path for these three skills. Git file mode SHALL NOT be symlink (`120000`).

#### Scenario: Fresh clone
- **WHEN** a Cursor session starts from a GitHub checkout of the repo
- **THEN** the three `SKILL.md` files exist in `.cursor/skills/` without resolving a symlink to hermes
- **AND** docs instruct preferring the repo path over Codex compatibility discovery

### Requirement: Column gate is always-on; full workflow is a skill
The always-apply harness rule SHALL state that `Em Refinamento` is the entry column, Todo is not implementation, and Design columns must not be skipped. The detailed 12-column runbook SHALL live in the `alan-workflow` skill (on-demand). Chat requests such as `implemente` SHALL NOT authorize `/opsx:apply` or product code while `Status=Todo`. The always-on layer SHALL be the short `harness.mdc` plus the `sessionStart` Moore page; it MUST NOT include the `AGENTS.md` overlay body.

#### Scenario: Chat says implement all Todo cards
- **WHEN** the user asks to implement cards in `Status=Todo`
- **THEN** the agent SHALL start Design (OpenSpec + critique + Gist), not `/opsx:apply` or product code

#### Scenario: Todo session does not load release playbook
- **WHEN** a session starts bound to a card with `Status=Todo`
- **THEN** always-on context is harness.mdc plus `context_file[Todo]`
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
The versioned `diff-reviewer` and `code-reviewer` Tasks MUST use `inherit` unless Alan selects another model in chat. `/review-bugbot` and `/review-security` MAY use the Cursor-managed product model only when Alan explicitly requests those skills.

#### Scenario: Local reviewers inherit
- **WHEN** Code Review spawns `.cursor/agents/diff-reviewer.md` or `.cursor/agents/code-reviewer.md`
- **THEN** the child MUST use `inherit` (same chat model)

#### Scenario: Optional Bugbot uses the product model
- **WHEN** Alan asks for `/review-bugbot` or `/review-security`
- **THEN** that optional run MAY use the Cursor-managed reviewer model
- **AND** that MUST NOT be treated as a silent swap of the session LLM for implementation or the local reviewers

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
The repository root `AGENTS.md` SHALL be a stub of at most 40 non-empty lines that points to `docs/crypto-overlay.md` for ports/URLs, Drive, PostgreSQL, and release-guard/lote/PROD, and MUST include the board URL `github.com/users/oalansilva/projects/1`. The long overlay body SHALL live in `docs/crypto-overlay.md` (not always-injected by Cursor). Agents MUST `Read` that overlay only when the task needs those topics. The stub MUST NOT contain the 12-column runbook, `release-guard pre`/`post` snippets, or deploy PROD procedure.

#### Scenario: Fresh session does not ingest the overlay body from AGENTS.md
- **WHEN** the root `AGENTS.md` is read as the always-on workspace file
- **THEN** it has at most 40 non-empty lines
- **AND** it does not contain `scripts/release-guard pre` or the 12-column path as a procedure
- **AND** it names `docs/crypto-overlay.md` as the on-demand overlay
- **AND** it contains `github.com/users/oalansilva/projects/1`

### Requirement: Always-on harness rule is 8-15 body lines
`.cursor/rules/harness.mdc` SHALL remain `alwaysApply: true` and its body (non-empty lines after the YAML frontmatter) MUST contain between 8 and 15 lines. The body SHALL tell the agent to resolve `(q, bound_card, q_git)`, that chat wording is not authorization, that NLU is not δ, that `Todo` is not implementation, and that the overlay is on-demand. It MUST NOT include the Code Review reviewer procedure, the OpenSpec Gist republication helper, or the release closeout.

#### Scenario: harness.mdc body budget
- **WHEN** `.cursor/rules/harness.mdc` is counted excluding the YAML frontmatter
- **THEN** non-empty body lines are between 8 and 15 inclusive
- **AND** the body mentions resolving `(q, bound_card, q_git)`
- **AND** the body does not mention `diff-reviewer` or `release-guard`

### Requirement: alan-workflow skill priority is delta and Guard first
`.cursor/skills/alan-workflow/SKILL.md` SHALL declare priority order **δ and Guard > overlay > skill > wording**. Chat utterances such as `implemente` MUST be classified as wording (lowest). Overlay (`docs/crypto-overlay.md`) MUST be loaded only when ports, Drive, PostgreSQL, or release are in scope.

#### Scenario: Skill lists inverted priority
- **WHEN** `.cursor/skills/alan-workflow/SKILL.md` is opened
- **THEN** the priority list places δ/Guard before overlay, overlay before the skill runbook, and wording last
- **AND** it no longer lists “Instrução direta de Alan no chat” as item 1 ahead of δ
