## ADDED Requirements

### Requirement: Release runbook names resolved-package archive on release-* as the official path
The canonical skill `.cursor/skills/covenant-flow/SKILL.md` Release section and overlay_doc publication path B SHALL state that, after an explicit closeout pedido, OpenSpec archive of Homologado package changes is written on `release-*` when that branch is the closeout git, using Guard `decide()` with per-change card id + live `Homologado` Status. The skill MUST state that `bound_card=⊥` does not block that archive, that a declared card list or the branch name alone does not authorize it, and that Alan MUST NOT be asked for an extra operational confirmation of this path (T7 remains the Design gate). Worktree-of-card + cherry-pick MUST NOT be documented as the official archive. #1059 SHALL consume this same Guard contract and MUST NOT ship a second archive-allow implementation. Product writes on `develop`/`release-*` remain deny. The skill MUST NOT dump the 12-column runbook. `AGENTS.md` MUST NOT grow this rule. Client stubs under `.dsh/skills/`, `.grok/skills/`, and `.opencode/skills/` MUST stay at most 8 non-empty body lines. `.cursor/process-fsm.yaml` MUST NOT gain state, event, hook, or `enabled_tools`. This card MUST NOT execute a release and MUST NOT absorb #1059 continuity, questions, manifesto, evidence, or general closeout.

#### Scenario: Release section names official archive without extra confirmation
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` Release section is read
- **THEN** it states that archive of Homologado OpenSpec changes on `release-*` is the official path after an explicit pedido
- **AND** it states that `bound_card=⊥` is not the archive deny and that Alan is not re-asked to authorize that path
- **AND** it does not prescribe card-worktree cherry-pick as the official archive
- **AND** `AGENTS.md` does not contain a T0–T17 table

#### Scenario: Overlay path B matches the Guard contract
- **WHEN** overlay_doc publication path B is read
- **THEN** it instructs to commit the OpenSpec archive on `release-*`
- **AND** it does not require publishing the archive in a `card-<id>-*` worktree first

#### Scenario: #1059 consumes this contract
- **WHEN** #1059 specifies archive/closeout write control
- **THEN** it reuses `scripts/process-fsm/guard.py` `decide()` as specified here
- **AND** it MUST NOT add a parallel allow for `openspec/changes/**` on `release-*`

#### Scenario: FSM table stays untouched
- **WHEN** a reviewer inspects this change's diff
- **THEN** `.cursor/process-fsm.yaml` has no new state, event, hook, or `enabled_tools`
- **AND** `scripts/process-fsm/process_event.py` is not required to change for this archive allow
