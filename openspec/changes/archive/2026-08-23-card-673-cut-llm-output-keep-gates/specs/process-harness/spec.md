## ADDED Requirements

### Requirement: Grok stubs exist for design-critic and Impeccable
Grok SHALL have thin skill stubs at `.grok/skills/design-critic/SKILL.md` and `.grok/skills/impeccable/SKILL.md`. Each stub MUST keep the canonical skill `name`, MUST instruct MUST Read of `.agents/skills/<name>/SKILL.md`, MUST map Cursor `Task inherit` to `spawn_subagent` inherit, MUST NOT copy the runbook, and MUST keep body (non-empty lines after frontmatter) at most 8 lines. `scripts/process-fsm/grok_stubs.py` SHALL generate and CI-check these extras in addition to stubs for `.cursor/skills/*/SKILL.md`. A missing or stale extra stub MUST fail the stub generator check. The hop of reading stub then canonical is accepted for Grok only.

#### Scenario: Grok Design loads design-critic via stub
- **WHEN** a Grok session runs Design
- **THEN** `.grok/skills/design-critic/SKILL.md` exists
- **AND** its body tells the agent to Read `.agents/skills/design-critic/SKILL.md`
- **AND** the stub body does not contain the Impeccable pipeline as a copied procedure

#### Scenario: Extra stub drift fails CI
- **WHEN** `.agents/skills/impeccable/SKILL.md` description changes and the Grok stub is not regenerated
- **THEN** the stub generator check in `pytest scripts/process-fsm` fails

#### Scenario: Cursor skills stubs remain a bridge
- **WHEN** a reviewer inspects `.grok/skills/alan-workflow/SKILL.md`
- **THEN** it still points at `.cursor/skills/alan-workflow/SKILL.md`
- **AND** extra `.agents` stubs do not replace that generator path
