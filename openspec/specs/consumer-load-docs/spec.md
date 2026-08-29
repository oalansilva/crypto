# consumer-load-docs Specification

## Purpose
TBD - created by archiving change card-798-overlay-doc-covenant-flow. Update Purpose after archive.
## Requirements
### Requirement: Live load docs point only at covenant-flow skills
The consumer live load docs — `docs/crypto-overlay.md` (`overlay_doc`), `rules.md`, `docs/backlog-operating-model.md`, and the Hermes banner in `docs/analytics/funil-social-site-leads-plan.md` — SHALL instruct agents to load `covenant-flow` and `covenant-flow-environments`. Canonical paths SHALL be `.cursor/skills/covenant-flow/SKILL.md` and `.cursor/skills/covenant-flow-environments/SKILL.md`. Every load instruction (a path under `.cursor/skills/alan-workflow*` or a follow/use verb `siga` / `seguir` / `carregue` / `use` / `aplique` plus `alan-workflow*`) MUST retarget to those names. The OpenSpec Gist helper path SHALL be `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh`. Those four files MUST NOT contain the token `alan-workflow` and MUST NOT add formerly or avoid notes. This requirement MUST NOT rewrite main pin specs under `openspec/specs/**` (including AND «formerly» from #773).

#### Scenario: Agent follows overlay_doc
- **WHEN** an agent follows `docs/crypto-overlay.md` on a uniquely pinned worktree that has no `.cursor/skills/alan-workflow/` directory
- **THEN** the runbook path it reads is `.cursor/skills/covenant-flow/SKILL.md`
- **AND** environment load is `.cursor/skills/covenant-flow-environments/SKILL.md`
- **AND** the Gist helper path is `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh`

#### Scenario: Agent follows rules.md
- **WHEN** an agent follows `rules.md` for the global card cycle, implementation-by-card, homologation, release, branches, or git hygiene
- **THEN** it is instructed to follow `covenant-flow` (and `covenant-flow-environments` when the rule loads environments)
- **AND** the skill path is `.cursor/skills/covenant-flow/` in this repo, not `.cursor/skills/alan-workflow/`

#### Scenario: Visual QA in backlog-operating-model points at covenant-flow
- **WHEN** an agent reads the Visual QA sentence in `docs/backlog-operating-model.md`
- **THEN** that sentence names `covenant-flow`
- **AND** it does not name `alan-workflow`

#### Scenario: rg over the four live load docs is empty
- **WHEN** a reviewer runs `rg -n 'alan-workflow' docs/crypto-overlay.md rules.md docs/backlog-operating-model.md docs/analytics/funil-social-site-leads-plan.md`
- **THEN** the command returns empty
- **AND** none of those four files contains a formerly or avoid note about `alan-workflow`
- **AND** `.cursor/skills/alan-workflow*` is still absent from this consumer git

### Requirement: Funnel banner retargets skill names and keeps the DEV default
The Hermes banner in `docs/analytics/funil-social-site-leads-plan.md` SHALL name `covenant-flow` and `covenant-flow-environments`. It MUST keep the warning that the default environment is DEV and that PROD MUST NOT be changed without an explicit request from Alan. The banner MUST NOT be deleted. Only the skill names change.

#### Scenario: Funnel banner names new skills and keeps DEV/PROD warning
- **WHEN** an agent reads the Hermes banner at the top of `docs/analytics/funil-social-site-leads-plan.md`
- **THEN** the skill names are `covenant-flow` and `covenant-flow-environments`
- **AND** the banner still states DEV as the default environment
- **AND** the banner still forbids changing PROD without an explicit request from Alan
- **AND** the banner block is still present

### Requirement: Out-of-scope harness trees stay untouched
This change SHALL NOT edit `.covenant-flow/overlay.yaml`, root `AGENTS.md`, `.cursor/rules/harness.mdc`, client skins under `.dsh/` `.grok/` `.opencode/`, product repository `oalansilva/covenant-flow`, main specs under `openspec/specs/**`, historical `docs/release-*` / `docs/decision-log.md`, or product code under `backend/` and `frontend/src/`. It SHALL NOT recreate `alan-workflow*` in this consumer git. It SHALL NOT reopen #773, #554, #786, or #784.

#### Scenario: Apply touches only the four live load docs
- **WHEN** Apply of this change finishes
- **THEN** the only Markdown load-instruction files rewritten for this requirement are `docs/crypto-overlay.md`, `rules.md`, `docs/backlog-operating-model.md`, and `docs/analytics/funil-social-site-leads-plan.md`
- **AND** `.covenant-flow/overlay.yaml`, `AGENTS.md`, and `.cursor/rules/harness.mdc` are unchanged by this change
- **AND** `openspec/specs/covenant-flow` still contains the pin AND «formerly» text from #773
- **AND** no `alan-workflow*` skill directory is added under `.cursor/skills/`

