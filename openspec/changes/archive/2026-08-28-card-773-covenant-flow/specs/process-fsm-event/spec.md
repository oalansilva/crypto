## MODIFIED Requirements

### Requirement: Human gates and lote stub reject the Agent
Events `priorizar`, `aprovar_design`, and `homologar` MUST reject when invoked via `process_event()`. `fechar_release` MUST reject when predicate `M_lote` is false. Every `fechar_release` reject caused by ¬`M_lote` MUST contain `covenant-flow-environments` and `release-guard`. `process_event()` MUST NOT run deploy PROD (`git reset` no path PROD, `systemctl` PROD) as part of `fechar_release`.

#### Scenario: Agent cannot fire T1 T15
- **WHEN** `process_event()` is invoked with `priorizar` or `homologar`
- **THEN** each result is `reject` and the mover is not called

#### Scenario: M_lote false rejects T16
- **WHEN** event is `fechar_release` and `M_lote` is false
- **THEN** the result is `reject`
- **AND** the mover is not called
- **AND** the message contains `covenant-flow-environments` and `release-guard`

### Requirement: T16 live compiles M_lote and closes Pronto for the package
When `m_lote` is not injected, live `process_event fechar_release` SHALL measure it before `evaluate()`: True only if `scripts/release-guard post` exits 0. Non-zero exit, timeout, missing binary, or spawn error SHALL yield False. The CLI MUST NOT accept a `--m-lote` flag. If the live measurer is `None`, `process_event()` MUST `reject` and MUST NOT call the mover. If `evaluate()` rejects, the mover and the T16 closer MUST NOT run.

The package is `RELEASE_CARDS` (canonical env). If that env is empty, `--card` SHALL be the sole member. Every member MUST currently be Homologado or already Pronto; Done, QA, Design, missing item, or empty package MUST `reject` with `reason=I9` and MUST NOT call the mover. Already Pronto members MUST be skipped (no second `set_status`). After membership passes, `evaluate()` MUST run with `state=Homologado`, `actor=Agent`, and the measured `m_lote` — not `github_status_provider(None)`. The mover MUST be invoked per remaining Homologado package id, not via the session `bound_card`.

If `evaluate()` accepts, `process_event()` SHALL require a non-`None` T16 closer; a missing closer MUST `reject` with `reason=I9` and MUST NOT call the mover. With a closer present, it SHALL `comment_pronto` for each member (canonical `post-card-evidence-comment.sh --transition pronto`) and the mover SHALL be called with `to=Pronto` for each member only after that card's comment step succeeds. `--dry-run` MAY measure (read-only) and MUST NOT comment or move. Unit tests MUST inject the measurer and closer and MUST NOT call GitHub, `release-guard` real, or the live Project board.

#### Scenario: fechar_release rejects without M_lote
- **WHEN** `process_event()` is invoked with `fechar_release` and `m_lote` is unset and the measurer is absent or returns False
- **THEN** the result is `reject` with `reason` starting with `guard:`
- **AND** the mover is not called
- **AND** the T16 closer is not called
- **AND** the message contains `covenant-flow-environments` and `release-guard`

#### Scenario: fechar_release with post PASS closes the package
- **WHEN** `process_event()` is invoked with `fechar_release`, every `RELEASE_CARDS` member is Homologado, and the measurer returns True
- **AND** a T16 closer is injected and succeeds
- **THEN** the mover is called with `to=Pronto` for each package member
- **AND** `comment_pronto` ran for each member before that member's Status move

#### Scenario: package member not Homologado stays put
- **WHEN** `process_event()` is invoked with `fechar_release`, the measurer returns True, and at least one `RELEASE_CARDS` member is Done, QA, or missing
- **THEN** the result is `reject` with `reason=I9`
- **AND** the mover is not called

#### Scenario: already Pronto members are skipped on retry
- **WHEN** `process_event()` is invoked with `fechar_release`, the measurer returns True, and `RELEASE_CARDS` mixes Homologado and already Pronto ids
- **THEN** already Pronto ids are not moved again
- **AND** remaining Homologado ids are commented and moved to Pronto

#### Scenario: missing T16 closer never moves Pronto
- **WHEN** `process_event()` is invoked with `fechar_release`, the measurer returns True, package members are Homologado, and the closer is omitted
- **THEN** the result is `reject` with `reason=I9`
- **AND** the mover is not called

#### Scenario: comment_pronto failure stays Homologado
- **WHEN** the T16 closer fails on `comment_pronto` before any Status move
- **THEN** the result is `reject` with `reason=I9`
- **AND** the mover is not called

## ADDED Requirements

### Requirement: process_event mover reads overlay board ids via board_status
`process_event()` SHALL move Project Status using ids from `scripts/process-fsm/board_status.py`, which loads overlay `board.status_field_id` and `board.status_options`. Packaged `process_event.py` MUST NOT hardcode `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM`.

#### Scenario: Mover does not embed Cripto field id
- **WHEN** a legal `process_event` transition calls the board mover
- **THEN** the field id and option id come from overlay via `board_status`
- **AND** `process_event.py` does not contain the Cripto `PVTSSF_*` constant
