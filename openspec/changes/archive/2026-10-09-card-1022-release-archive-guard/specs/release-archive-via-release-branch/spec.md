## ADDED Requirements

### Requirement: Official closeout archives OpenSpec on release-* without card-worktree cherry-pick
When Alan has explicitly requested a release and the overlay path B applies (`release-* = origin/develop + archive` because push of archive to `develop` is protected), the agent SHALL prepare and record the OpenSpec archive of the Homologado package **on that `release-*` branch**. The agent MUST identify each change by `card-<id>`/`issue-<id>` in the change name, resolve live Status `Homologado`, and write only `openspec/changes/**` of those changes (active directory and `openspec/changes/archive/<YYYY-MM-DD>-<change>/`). The agent MUST NOT open a card worktree nor cherry-pick the archive solely to bypass Guard `fail_closed`. The agent MUST NOT ask Alan for a new operational confirmation of a path already allowed inside the requested release. Design approval of this card remains T7. Absence of a single session `bound_card` MUST NOT block the archive. `docs/crypto-overlay.md` SHALL name this as the normal path B step (commit archive on `release-*`). The next applicable `/kaizen release` MUST record whether the F-1/#1022 recurrence (Guard `fail_closed` on `release-*` unbound forcing worktree+cherry-pick) has ended. This requirement MUST NOT execute a release by itself and MUST NOT absorb #1059 continuity, manifesto, evidence, or general closeout.

#### Scenario: Agent archives on release-* with package resolved
- **WHEN** a requested release is on `q_git=release-*`, the package cards are Homologado, and each change name carries `card-<id>` or `issue-<id>` of those cards
- **THEN** the agent runs `openspec archive` (or equivalent move into `openspec/changes/archive/`) in that worktree
- **AND** it does not switch to a `card-<id>-*` worktree to obtain the write
- **AND** it does not ask Alan to re-authorize the archive

#### Scenario: Missing bound_card is not the block
- **WHEN** paging shows `bound_card=⊥` on the `release-*` session and the package is otherwise resolved
- **THEN** the documented path still instructs to archive on `release-*`
- **AND** the Guard allow of the previous requirement is the write control

#### Scenario: Next Kaizen records whether F-1 ended
- **WHEN** `/kaizen release` runs for the next applicable closeout after this change is in the consumer
- **THEN** `docs/kaizen-log.md` states whether archive on `release-*` succeeded without worktree+cherry-pick
- **AND** a new improvisation of the same deny is recorded as recurrence of #1022

#### Scenario: Cherry-pick workaround is not the official path
- **WHEN** a reviewer reads overlay path B and this requirement
- **THEN** `bc6382d5`-style cherry-pick from a card worktree is not prescribed as the normal archive step
- **AND** #617 sync `main → develop` after merge remains unchanged
