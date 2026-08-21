## ADDED Requirements

### Requirement: I8 T14 atomic closeout is compiled at runtime
Invariant I8 in `.cursor/process-fsm.yaml` SHALL be enforced by live `process_event integrar_develop`, not only by yaml text. After `checks_green` holds, failure of squash, dirty or non-fast-forward sync of `/srv/apps/dev/criptofarol/source`, canonical `./restart`, or the Done comment MUST keep the card in QA. Sync MUST probe `git status --porcelain` before mutating the checkout and MUST NOT `reset --hard`. Restart MUST be `/srv/apps/dev/criptofarol/source/restart`. The yaml transition T14 (`from: QA`, `event: integrar_develop`, `actor: Agent`, `to: Done`, `guard: checks_green`, actions `squash`, `restart`, `comment_done`, `set_status`) MUST remain unchanged by this card.

#### Scenario: Runner failure does not move Done
- **WHEN** T14 is evaluated with `checks_green` true and a T14 runner step fails
- **THEN** Status remains QA
- **AND** `set_status(Done)` is not invoked

#### Scenario: Dirty canonical source does not move Done
- **WHEN** T14 sync sees non-empty `git status --porcelain` on `/srv/apps/dev/criptofarol/source`
- **THEN** Status remains QA
- **AND** `reset --hard` is not invoked
