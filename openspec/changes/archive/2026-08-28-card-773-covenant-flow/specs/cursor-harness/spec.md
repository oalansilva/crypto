## MODIFIED Requirements

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

### Requirement: Code Review happy path MUST inherit the chat model
The versioned `diff-reviewer` and `code-reviewer` Tasks MUST use `inherit` unless Alan selects another model in chat. Cursor Bugbot (`/review-bugbot`) MUST NOT be part of the product or the Code Review happy path. `/review-security` MAY run when Alan explicitly asks; it MUST NOT replace the local reviewers as the gate. Review constraints SHALL live in the two agent files (and optional consumer `REVIEW.md` without Bugbot), not in `BUGBOT.md`.

#### Scenario: Local reviewers inherit
- **WHEN** Code Review spawns `.cursor/agents/diff-reviewer.md` or `.cursor/agents/code-reviewer.md`
- **THEN** the child MUST use `inherit` (same chat model)

#### Scenario: Bugbot is not a product path
- **WHEN** Code Review runs on a pinned consumer
- **THEN** `/review-bugbot` MUST NOT run as the gate
- **AND** `BUGBOT.md` MUST NOT be required

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

### Requirement: alan-workflow skill priority is delta and Guard first
`.cursor/skills/covenant-flow/SKILL.md` SHALL declare priority order **δ and Guard > overlay > skill > wording**. Chat utterances such as `implemente` MUST be classified as wording (lowest). Overlay (`overlay_doc`, Cripto: `docs/crypto-overlay.md`) MUST be loaded only when ports, Drive, PostgreSQL, or release are in scope.

#### Scenario: Skill lists inverted priority
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` is opened
- **THEN** the priority list places δ/Guard before overlay, overlay before the skill runbook, and wording last
- **AND** it no longer lists “Instrução direta de Alan no chat” as item 1 ahead of δ

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

## RENAMED Requirements

### Requirement: alan-workflow skill priority is delta and Guard first
- FROM: `alan-workflow skill priority is delta and Guard first`
- TO: `covenant-flow skill priority is delta and Guard first`
