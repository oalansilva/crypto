# process-harness Specification

## Purpose
Contrato multi-cliente do processo: núcleo = verdade; adapter Cursor e adapter Grok = tradução. Proíbe dual-write da lei.

## Requirements

### Requirement: Process law has one nucleus and two adapters
The process SHALL have a single nucleus and two client adapters. The nucleus is `.cursor/process-fsm.yaml`, `scripts/process-fsm/`, the canonical skill files under `.cursor/skills/`, and the short root `AGENTS.md`. The Cursor adapter is `.cursor/hooks.json`, `.cursor/hooks/*`, `.cursor/rules/harness.mdc`, and `.cursor/commands/`. The Grok adapter is `.grok/hooks/`, generated Moore paging under `.grok/rules/`, and skill stubs under `.grok/skills/`. A change of column, invariant, product glob, or Moore `context_file` text MUST be made once in the yaml (and in a skill only when the change is *how* to work). Adapters MUST NOT copy T0–T17, I1–I9, or the 12-column runbook. OpenCode, Codex home skills, and Hermes skill symlinks MUST NOT be an active contract.

#### Scenario: One yaml change reaches both adapters
- **WHEN** a glob, column, or `context_file` stub is changed in `.cursor/process-fsm.yaml`
- **THEN** both the Cursor Guard/paging path and the Grok Guard/paging path compile from that yaml
- **AND** no second copy of the table exists in `.grok/rules/` or `.cursor/rules/`

#### Scenario: Dual-write of the law is forbidden
- **WHEN** a reviewer inspects `.cursor/rules/` and `.grok/rules/`
- **THEN** neither directory contains a T0–T17 table, I1–I9 list, or 12-column procedure
- **AND** a Grok skill stub MUST NOT contain the runbook copied from `.cursor/skills/`

### Requirement: Skill stubs are a bridge not a second runbook
Grok SHALL discover process skills via `.grok/skills/<name>/SKILL.md` stubs for every `SKILL.md` directory under `.cursor/skills/` (including `alan-workflow`, `alan-workflow-ambientes`, `github-project-board`, `kaizen`, and `openspec-*`). Each stub MUST keep the same skill `name`, MUST instruct the agent to Read the canonical `.cursor/skills/<name>/SKILL.md` and follow it (client is Grok Build; map Cursor `Task inherit` to `spawn_subagent` inherit), and MUST NOT copy the runbook body. Stub body (non-empty lines after frontmatter) MUST be at most 8 lines. Stubs MUST be generated from canonical frontmatter plus a fixed body template so description drift is caught in CI. Git mode of canonical skills remains a regular file (not a Hermes symlink). Cursor compatibility scanning `.cursor/skills/` MAY remain enabled; the stub is still the versioned Grok skin because `.grok/skills/` wins name dedup.

#### Scenario: Stub points at the canonical skill
- **WHEN** a Grok session activates `alan-workflow`
- **THEN** `.grok/skills/alan-workflow/SKILL.md` exists
- **AND** its body tells the agent to Read `.cursor/skills/alan-workflow/SKILL.md`
- **AND** the stub body does not contain the 12-column path as a procedure

#### Scenario: Stale stub fails CI
- **WHEN** a canonical skill `description` changes and the stub is not regenerated
- **THEN** the stub generator check in `pytest scripts/process-fsm` fails

### Requirement: Always-on delta lives in AGENTS.md
The short always-on law (resolve `(q, bound_card, q_git)`, chat wording is not authorization, NLU is not δ, `Em Refinamento` is the entry column, `Todo` is not implementation, Design columns must not be skipped, overlay is on-demand, Alan-only T1/T7/T15, T16 is `process_event fechar_release`) SHALL live in the root `AGENTS.md` stub so both clients ingest it. `AGENTS.md` MUST remain at most 40 non-empty lines and MUST still point to `docs/crypto-overlay.md` for ports/Drive/PostgreSQL/release. It MUST name both Cursor Agent and Grok Build as clients. It MUST state that Cursor Auto is allowed and that Grok Build remains cooperative until the deny essay PASS. It MUST NOT include the 12-column runbook or `release-guard pre`/`post` snippets. The file header MUST NOT say the stub is “não always-on” after this change.

#### Scenario: Both clients read the same always-on stub
- **WHEN** a Cursor session and a Grok session start in the repo
- **THEN** both load root `AGENTS.md`
- **AND** that file states that chat wording is not δ and that `Todo` is not implementation
- **AND** it states Alan-only T1/T7/T15
- **AND** it does not claim Grok Auto is active
- **AND** it does not contain `scripts/release-guard pre`

### Requirement: Grok Auto is gated on the deny essay
Until a human essay on the same worktree shows that an illegal product Write with `q_git=develop` is denied in **both** Cursor and Grok Build, Grok Build MUST be treated as cooperative, not Auto. `process_event` remains the only Agent Status mover in both clients. Agent MUST NOT `item-edit` Status.

#### Scenario: Essay not yet green
- **WHEN** the Grok deny essay has not been recorded as PASS
- **THEN** docs and always-on text MUST NOT claim Grok Auto is active
- **AND** the compiled Guard for Grok MUST still emit `decision: deny` on illegal product writes (the gate is operational claim, not an excuse to skip the adapter)

#### Scenario: process_event is the Status mover in both clients
- **WHEN** a Grok or Cursor agent needs to move Project 1 Status
- **THEN** it SHALL call `scripts/process-fsm/process_event.py` with a named event
- **AND** it MUST NOT `gh project item-edit` the Status field

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
