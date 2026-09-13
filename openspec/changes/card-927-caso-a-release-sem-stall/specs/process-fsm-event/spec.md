## MODIFIED Requirements

### Requirement: Unbound or mismatched card rejects moves
For events that move an existing **bound** card, `bound_card=⊥` or a `--card` that does not match `q_git`'s `card-<id>` MUST yield `reject` without a mover call. Event `fechar_release` is a lote closeout: a non-empty `RELEASE_CARDS` list (or `--card` as a one-id package) MUST be accepted when `q_git` is `develop` or `release-*` even if `bound_card=⊥`. When `fechar_release` is invoked and `q_git` is `main`, `docs-*`, or `sync-*`, `process_event()` MUST `reject` without a mover call, MUST NOT switch git, and MUST include a next-action `message` that tells the operator to switch to `develop` or `release-*` and repeat. That reject MUST NOT use a dry `reason=unbound` alone. Other events MUST keep the unbound reject.

#### Scenario: Unbound process_event
- **WHEN** `bound_card` is `⊥` and the event is `iniciar_apply`
- **THEN** the result is `reject` and the mover is not called

#### Scenario: Unbound fechar_release with package is allowed to evaluate
- **WHEN** `bound_card` is `⊥`, `q_git` is `develop`, event is `fechar_release`, and `RELEASE_CARDS` is a non-empty list of Homologado ids
- **THEN** the unbound reject MUST NOT fire
- **AND** evaluation proceeds with `state=Homologado`, measured `M_lote`, and the package membership checks
- **AND** Status moves use each package id, not the session `bound_card`

#### Scenario: fechar_release on production git names the next action
- **WHEN** event is `fechar_release` and `q_git` is `main`
- **THEN** the result is `reject`
- **AND** the mover is not called
- **AND** git is not switched
- **AND** `message` names the next action: switch to `develop` or `release-*` and repeat
- **AND** `reason` MUST NOT be only the dry token `unbound`

#### Scenario: fechar_release on docs-* or sync-* names the next action
- **WHEN** event is `fechar_release` and `q_git` matches `docs-*` or `sync-*`
- **THEN** the result is `reject`
- **AND** the mover is not called
- **AND** git is not switched
- **AND** `message` names the next action: switch to `develop` or `release-*` and repeat
