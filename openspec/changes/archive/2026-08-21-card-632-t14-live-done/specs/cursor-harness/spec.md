## ADDED Requirements

### Requirement: Done closeout is process_event integrar_develop
While `Status=QA` and the card is bound to `card-<id>-*`, the Agent SHALL close Done by invoking `process_event integrar_develop` from that worktree. That event MUST measure `qa-gate`, squash into `develop`, sync `/srv/apps/dev/criptofarol/source` to `origin/develop`, run the canonical `/srv/apps/dev/criptofarol/source/restart`, comment Done evidence, and only then move Status. The Agent MUST NOT treat `gh project item-edit` of Status, a worktree `./restart`, or a Status move without restart as Done closeout. `homologar` and `fechar_release` remain Alan-only.

#### Scenario: Agent closes QA to Done
- **WHEN** the card is in QA, `qa-gate` is green, and the Agent runs `process_event integrar_develop`
- **THEN** canonical DEV restart runs before Status becomes Done
- **AND** the Agent does not edit Project 1 Status via `gh project item-edit`

#### Scenario: Worktree restart is not Done proof
- **WHEN** the Agent runs `./restart` inside `crypto-worktrees/card-<id>-*`
- **THEN** that command MUST NOT be treated as T14 closeout
- **AND** the card MUST remain in QA until `process_event integrar_develop` succeeds
