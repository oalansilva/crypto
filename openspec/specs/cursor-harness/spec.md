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
The always-apply harness rule SHALL state that `Em Refinamento` is the entry column, Todo is not implementation, and Design columns must not be skipped. The detailed 12-column runbook SHALL live in the `alan-workflow` skill. Chat requests such as `implemente` SHALL NOT authorize `/opsx:apply` or product code while `Status=Todo`.

#### Scenario: Chat says implement all Todo cards
- **WHEN** the user asks to implement cards in `Status=Todo`
- **THEN** the agent SHALL start Design (OpenSpec + critique + Gist), not `/opsx:apply` or product code

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
