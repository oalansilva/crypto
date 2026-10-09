## ADDED Requirements

### Requirement: Release parent model prerequisite is not T18
The Release section of `.cursor/skills/covenant-flow/SKILL.md` SHALL keep the existing rule that T16 and `fecho-lote` require the parent chat to be the vigente `execucao` slug from `.cursor/model-map.yaml`. That prerequisite MUST NOT be labeled T18. T18 MUST remain Alan's `nao_homologar` gesture. The section MUST NOT tell release closeout to use "the same model as the parent chat" instead of the `execucao` band. Codex closeout MUST read `execucao.codex` from the same map. The file `.cursor/model-map.yaml` MUST NOT be edited by this requirement. `AGENTS.md` MUST NOT gain this rule.

#### Scenario: Release section no longer names the parent prerequisite T18
- **WHEN** the Release section of `.cursor/skills/covenant-flow/SKILL.md` is read
- **THEN** it does not contain the label `Pré-requisito (T18)` for the execução parent rule
- **AND** it still refuses a `juizo` parent chat for T16 and `fecho-lote`
- **AND** the `nao_homologar` description of T18 elsewhere in the skill remains

#### Scenario: Release does not inherit the design same-model sentence
- **WHEN** an operator closes a release from the runbook
- **THEN** the parent and `fecho-lote` use the `execucao` band of `.cursor/model-map.yaml`
- **AND** the overlay sentence about Design critique using the same model as the chat is not applied as a release gate

### Requirement: Authorized release archives without the generic menu
The Release section SHALL state that, for an explicitly requested release, sync and archive of completed Homologado package changes on `release-*` proceed without the generic `openspec-archive-change` reconfirmation menu by reusing #1022 `decide()`. The section and the overlay release sentences MUST NOT copy a second allow-list and MUST NOT instruct a card worktree plus cherry-pick, including as a way to bypass the guard. Until that `decide()` is in the tree, an archive deny MUST be stated as a real block that points at #1022. Conflict without a resolution, discard, or a real human exception MUST still be asked as such. Silence MUST NOT count as approval. This requirement MUST NOT change `guard.decide()` and MUST NOT add an FSM event.

#### Scenario: Runbook does not require the archive menu
- **WHEN** the Release section is read during an explicitly requested closeout
- **THEN** it tells the agent to sync and archive completed changes without the generic menu
- **AND** it names #1022 `decide()` as the archive-write contract, forbids a second allow-list, and does not instruct a card worktree plus cherry-pick

#### Scenario: Unbound release deny points at #1022
- **WHEN** archive on unbound `release-*` is denied with `fail_closed` because #1022 `decide()` is not in the tree yet
- **THEN** the Release section tells the agent to stop and point at #1022
- **AND** it does not instruct a card worktree plus cherry-pick

#### Scenario: Unresolved conflict is still a question
- **WHEN** archive sync hits a conflict that has no resolution
- **THEN** the runbook requires that conflict to be presented as a human decision
- **AND** it forbids treating elapsed silence as approval

### Requirement: Package branch deletion order matches the existing post gate
The Release section and the release sentences of `docs/crypto-overlay.md` SHALL agree that package branches listed in `RELEASE_BRANCHES` are deleted before `release-guard post` PASS and before cards move to `Pronto`, matching the existing post-release cleanup gate. They MUST NOT say that those branches are deleted only after the cards are already `Pronto`. In-flight worktrees and `PRESERVED_BRANCHES` MUST remain preserved. This requirement MUST NOT weaken branch protection or `qa-gate`.

#### Scenario: Overlay and skill name the same deletion order
- **WHEN** the Release section and the overlay release branch-deletion sentences are read
- **THEN** both require package branches in `RELEASE_BRANCHES` to be absent before `post` PASS and before `Pronto`
- **AND** neither instructs deletion only after the cards have moved to `Pronto`

#### Scenario: Preserved in-flight branches stay
- **WHEN** a branch is listed in `PRESERVED_BRANCHES` or still has an active worktree and is not part of the package deletion set
- **THEN** the aligned sentences do not require deleting it to close the package
