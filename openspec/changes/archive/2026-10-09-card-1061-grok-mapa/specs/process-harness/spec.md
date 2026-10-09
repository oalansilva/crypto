## MODIFIED Requirements

### Requirement: Skill stubs are a bridge not a second runbook
Grok SHALL discover process skills via `.grok/skills/<name>/SKILL.md` stubs for every `SKILL.md` directory under `.cursor/skills/` (including `covenant-flow`, `covenant-flow-environments`, `implantar`, `github-project-board`, `kaizen`, and `openspec-*`). Each stub MUST keep the same skill `name`, MUST instruct the agent to Read the canonical `.cursor/skills/<name>/SKILL.md` and follow it (client is Grok Build; pass `spawn_subagent` `model` from `juizo.grok` or `execucao.grok` in `.cursor/model-map.yaml`; do not omit `model`; do not inherit the picker), and MUST NOT copy the runbook body. The stub MUST NOT map Cursor Task `inherit` to `spawn_subagent` inherit. Stub body (non-empty lines after frontmatter) MUST be at most 8 lines. Stubs MUST be generated from canonical frontmatter plus a fixed body template so description drift is caught in CI. Git mode of canonical skills remains a regular file (not a Hermes symlink). Cursor compatibility scanning `.cursor/skills/` MAY remain enabled; the stub is still the versioned Grok skin because `.grok/skills/` wins name dedup.

#### Scenario: Stub points at the canonical skill
- **WHEN** a Grok session activates `covenant-flow`
- **THEN** `.grok/skills/covenant-flow/SKILL.md` exists
- **AND** its body tells the agent to Read `.cursor/skills/covenant-flow/SKILL.md`
- **AND** the stub body does not contain the 12-column path as a procedure
- **AND** the stub body does not contain `spawn_subagent` inherit
- **AND** the stub body tells the agent not to omit `model` and not to inherit the picker

#### Scenario: Stale stub fails CI
- **WHEN** a canonical skill `description` changes and the stub is not regenerated
- **THEN** the stub generator check in `pytest scripts/process-fsm` fails

### Requirement: Grok stubs exist for design-critic and Impeccable
Grok SHALL have thin skill stubs at `.grok/skills/design-critic/SKILL.md` and `.grok/skills/impeccable/SKILL.md`. Each stub MUST keep the canonical skill `name`, MUST instruct MUST Read of the canonical skill, MUST tell the agent to pass `spawn_subagent` `model` from `juizo.grok` or `execucao.grok` and MUST NOT map Cursor `Task inherit` to `spawn_subagent` inherit, MUST NOT copy the runbook, and MUST keep body (non-empty lines after frontmatter) at most 8 lines. `scripts/process-fsm/grok_stubs.py` SHALL generate and CI-check these extras in addition to stubs for `.cursor/skills/*/SKILL.md`. A missing or stale extra stub MUST fail the stub generator check. The hop of reading stub then canonical is accepted for Grok only. After unique pin, Cursor-skill stubs SHALL use `covenant-flow` names, not `alan-workflow`.

#### Scenario: Grok Design loads design-critic via stub
- **WHEN** a Grok session runs Design
- **THEN** `.grok/skills/design-critic/SKILL.md` exists
- **AND** its body tells the agent to Read the canonical design-critic skill
- **AND** the stub body does not contain the Impeccable pipeline as a copied procedure
- **AND** the stub body does not map children to inherit

#### Scenario: Extra stub drift fails CI
- **WHEN** `.agents/skills/impeccable/SKILL.md` description changes and the Grok stub is not regenerated
- **THEN** the stub generator check in `pytest scripts/process-fsm` fails

#### Scenario: Cursor skills stubs remain a bridge
- **WHEN** a reviewer inspects `.grok/skills/covenant-flow/SKILL.md` on a uniquely pinned consumer
- **THEN** it points at `.cursor/skills/covenant-flow/SKILL.md`
- **AND** it does not copy the role table
