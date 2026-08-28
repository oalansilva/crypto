# process-fsm-event Specification

## Purpose
CLI SMAG `process_event`: valida δ e só então move o Status do Project 1. Actor da função/CLI é sempre Agent.
## Requirements
### Requirement: process_event is the Agent Status mover
`scripts/process-fsm/process_event.py` SHALL accept a named event, resolve `(q, bound_card, q_git)` via the #610 resolver, evaluate δ from `.cursor/process-fsm.yaml`, and call an injectable board mover to set Project 1 `Status` **only** when the result is `transition`. The CLI and the `process_event()` function MUST hardcode actor `Agent` (no `--actor` flag and no `actor=` parameter). Unit tests MUST inject the mover, status, git binding, and guard predicates, MUST NOT inject actor, and MUST NOT call GitHub, Cursor hooks, or the live Project board. `evaluate()` tests MAY use actor `Alan`/`Guard` directly; `process_event()` MUST NOT.

#### Scenario: Agent aprovar_design is rejected
- **WHEN** `process_event()` is invoked with event `aprovar_design`
- **THEN** the result is `reject`
- **AND** the board mover is not called
- **AND** `q` is unchanged

#### Scenario: iniciar_apply does not grant Write while Status is still Pronto para Dev
- **WHEN** `process_event iniciar_apply` runs with injected `q=Pronto para Dev`, `q_git=card-<id>-*`, matching `bound_card`, and `digest_changed=false`
- **AND** a product `Write` Guard `decide` is evaluated with status still injected as `Pronto para Dev`
- **THEN** `process_event` SHALL record a transition to `Em desenvolvimento` on the mover
- **AND** the Guard result for that Write is `deny` (I3)
- **AND** `process_event` stdout MUST NOT include a write-allow token

#### Scenario: request_implement is not in delta
- **WHEN** `process_event` is invoked with event `request_implement`
- **THEN** the result is `reject`
- **AND** the mover is not called
- **AND** the output lists `enabled_events(q)` from the yaml

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

### Requirement: Digest change compiles I4 as T17
If `digest` of `design.md` plus optional prototype files differs from the sidecar written on a successful T5 (or the sidecar is missing) while `q` is `Pronto para Dev` or `Em desenvolvimento`, `evaluate(iniciar_apply)` and `evaluate(pedir_review)` MUST `reject` with `reason=I4` (not T8/T9). `process_event()` MUST then compile I4: `evaluate(invalidar_aprovacao, actor=Guard, digest_changed=true)` internally and move to `Design` (T17a/T17b). The mover MUST never be called with Em desenvolvimento or Code Review in that path. `invalidar_aprovacao` via `process_event()` with `digest_changed` false MUST reject with actor `Agent` and MUST NOT call the mover. The sidecar MUST be written only by a successful T5 in the script (`--dry-run` MUST NOT write it).

#### Scenario: iniciar_apply with changed digest goes to Design
- **WHEN** `process_event iniciar_apply` runs with `q=Pronto para Dev`, valid card binding, and `digest_changed=true`
- **THEN** the mover is called with `to=Design`
- **AND** the mover is not called with `to=Em desenvolvimento`
- **AND** `reason` is `I4`

#### Scenario: pedir_review with changed digest goes to Design
- **WHEN** `process_event pedir_review` runs with `q=Em desenvolvimento`, valid card binding, and `digest_changed=true`
- **THEN** the mover is called with `to=Design`
- **AND** the mover is not called with `to=Code Review`
- **AND** `reason` is `I4`

#### Scenario: invalidar_aprovacao without digest change rejects
- **WHEN** `process_event()` is invoked with `invalidar_aprovacao` and `digest_changed` is false
- **THEN** the result is `reject` and the mover is not called

### Requirement: Unbound or mismatched card rejects moves
For events that move an existing **bound** card, `bound_card=⊥` or a `--card` that does not match `q_git`'s `card-<id>` MUST yield `reject` without a mover call. Event `fechar_release` is a lote closeout: a non-empty `RELEASE_CARDS` list (or `--card` as a one-id package) MUST be accepted when `q_git` is `develop` or `release-*` even if `bound_card=⊥`. Other events MUST keep the unbound reject.

#### Scenario: Unbound process_event
- **WHEN** `bound_card` is `⊥` and the event is `iniciar_apply`
- **THEN** the result is `reject` and the mover is not called

#### Scenario: Unbound fechar_release with package is allowed to evaluate
- **WHEN** `bound_card` is `⊥`, `q_git` is `develop`, event is `fechar_release`, and `RELEASE_CARDS` is a non-empty list of Homologado ids
- **THEN** the unbound reject MUST NOT fire
- **AND** evaluation proceeds with `state=Homologado`, measured `M_lote`, and the package membership checks
- **AND** Status moves use each package id, not the session `bound_card`

### Requirement: T10-T13 events imply exclusive-group guards; T14 stays reject live
For `achar_bloqueante`, `aceitar_sha`, `rerun_infra`, and `falha_codigo`, `process_event()` SHALL set the matching yaml guard true from the event name and the other exclusive-group predicates false. `integrar_develop` MUST reject in live `process_event()` (`checks_green` unset) and MUST NOT call the mover.

#### Scenario: aceitar_sha from Code Review transitions
- **WHEN** `process_event()` is invoked with `aceitar_sha`, `q=Code Review`, valid card binding, and digest unchanged
- **THEN** the mover is called with `to=QA`

#### Scenario: integrar_develop rejects without checks_green
- **WHEN** `process_event()` is invoked with `integrar_develop` and `checks_green` is unset
- **THEN** the result is `reject` and the mover is not called

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

### Requirement: process_event mover reads overlay board ids via board_status
`process_event()` SHALL move Project Status using ids from `scripts/process-fsm/board_status.py`, which loads overlay `board.status_field_id` and `board.status_options`. Packaged `process_event.py` MUST NOT hardcode `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM`.

#### Scenario: Mover does not embed Cripto field id
- **WHEN** a legal `process_event` transition calls the board mover
- **THEN** the field id and option id come from overlay via `board_status`
- **AND** `process_event.py` does not contain the Cripto `PVTSSF_*` constant

