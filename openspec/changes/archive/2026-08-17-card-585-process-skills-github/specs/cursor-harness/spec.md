## MODIFIED Requirements

### Requirement: Workflow skills are versioned files in the GitHub repo
The Cursor harness SHALL load `alan-workflow`, `alan-workflow-ambientes` and `github-project-board` from `.cursor/skills/<name>/SKILL.md` as regular files in `oalansilva/crypto`. Agents MUST NOT treat `~/.codex/skills/` or `/srv/knowledge/hermes-second-brain/skills/` as the canonical load path for these three skills. Git file mode SHALL NOT be symlink (`120000`). Hermes/Codex copies of these three skills SHALL NOT be dual-written by this change.

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
