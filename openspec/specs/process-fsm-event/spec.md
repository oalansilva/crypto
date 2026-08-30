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

### Requirement: T10-T13 events imply exclusive-group guards
For `achar_bloqueante`, `aceitar_sha`, `rerun_infra`, and `falha_codigo`, `process_event()` SHALL set the matching yaml guard true from the event name and the other exclusive-group predicates false. `reviewers_ok` for `aceitar_sha` remains true from the event name (not a measured review). Before `evaluate()`, `aceitar_sha` MUST list a pull request from `q_git` into `develop`. If that list is empty, `process_event()` MUST `reject` with `reason=no_pr`, MUST NOT call the mover, MUST NOT create a pull request, and Status MUST remain Code Review.

#### Scenario: aceitar_sha from Code Review transitions when a PR exists
- **WHEN** `process_event()` is invoked with `aceitar_sha`, `q=Code Review`, valid card binding, digest unchanged, and a PR from `q_git` into `develop` exists
- **THEN** the mover is called with `to=QA`

#### Scenario: aceitar_sha without PR stays Code Review
- **WHEN** `process_event()` is invoked with `aceitar_sha`, `q=Code Review`, valid card binding, and no PR from `q_git` into `develop` exists
- **THEN** the result is `reject` with `reason=no_pr`
- **AND** the mover is not called
- **AND** no pull request is created
- **AND** Status remains Code Review

### Requirement: T14 live classifies checks and surfaces structured reject reasons
When `checks_green` is not injected, live `process_event integrar_develop` SHALL classify the GitHub check `qa-gate` on the pull request from `q_git` into `develop` before `evaluate()`. The yaml guard remains the derived bool: True only if that check is `completed` and `conclusion=success` on the head SHA. Other checks on the same SHA MUST NOT change this predicate. The CLI MUST NOT accept a `--checks-green` flag.

If the live classifier or measurer is `None`, `process_event()` MUST `reject` and MUST NOT call the mover. When the derived bool is False, the JSON payload `reason` MUST be the classified token, not the generic `guard:checks_green`:
- no `q_git`, no PR, or no head SHA → `no_pr`
- `qa-gate` present and `status` is not `completed` → `qa-gate pending`
- missing `qa-gate`, skipped, cancelled, failure, API error, timeout, or JSON error → `qa-gate failed`

If `evaluate()` accepts, `process_event()` SHALL require a non-`None` T14 runner; a missing runner MUST `reject` with `reason=I8` and MUST NOT call the mover. With a runner present, it SHALL run in order (`squash`, `sync_dev_source`, `restart`, `comment_done`) and the mover SHALL be called with `to=Done` only after every step succeeds. `process_event()` MUST NOT poll or retry internally.

`sync_dev_source` MUST run only on overlay `environments.dev.source`. Non-empty `git status --porcelain` MUST `reject` with `reason=sync: dirty` and a `message` that contains that path and the porcelain text, with no `checkout`, `merge`, `reset --hard`, restart, or Status move (I8: Status stays QA). Other runner failures MUST `reject` with `reason=I8` and `message` set to the exception text. `--dry-run` MAY classify (read-only) and MUST NOT run the runner or the mover. Unit tests MUST inject the classifier/measurer and runner and MUST NOT call GitHub.

#### Scenario: integrar_develop without PR is no_pr
- **WHEN** `process_event()` is invoked with `integrar_develop`, `q=QA`, valid card binding, and there is no PR from `q_git` into `develop`
- **THEN** the result is `reject` with `reason=no_pr`
- **AND** the mover is not called
- **AND** the T14 runner is not called

#### Scenario: integrar_develop with qa-gate pending is visible
- **WHEN** `process_event()` is invoked with `integrar_develop`, `q=QA`, a PR exists, and `qa-gate` is not `completed`
- **THEN** the result is `reject` with `reason=qa-gate pending`
- **AND** the mover is not called
- **AND** the T14 runner is not called

#### Scenario: integrar_develop with qa-gate failed is visible
- **WHEN** `process_event()` is invoked with `integrar_develop`, `q=QA`, a PR exists, and `qa-gate` is missing, skipped, cancelled, failed, or the Checks API errors
- **THEN** the result is `reject` with `reason=qa-gate failed`
- **AND** the mover is not called
- **AND** the T14 runner is not called

#### Scenario: integrar_develop with qa-gate green runs atomic closeout
- **WHEN** `process_event()` is invoked with `integrar_develop`, `q=QA`, valid card binding, and the classifier returns ok
- **AND** a T14 runner is injected and succeeds
- **THEN** the mover is called with `to=Done` after the runner finishes
- **AND** the runner ran `squash`, `sync_dev_source`, `restart`, and `comment_done` in that order

#### Scenario: dirty canonical DEV source stays QA with visible cause
- **WHEN** `sync_dev_source` sees non-empty `git status --porcelain` on overlay `environments.dev.source`
- **THEN** the result is `reject` with `reason=sync: dirty`
- **AND** `message` contains the canonical path and the porcelain text
- **AND** no `checkout`, `merge`, `reset --hard`, restart, or Status move runs

#### Scenario: T14 restart failure stays QA
- **WHEN** `process_event()` is invoked with `integrar_develop`, the classifier returns ok, and `restart` fails
- **THEN** the result is `reject` with `reason=I8`
- **AND** the payload includes a non-empty `message`
- **AND** the mover is not called

#### Scenario: missing T14 runner never moves Done
- **WHEN** `process_event()` is invoked with `integrar_develop`, the classifier returns ok, and the runner is omitted
- **THEN** the result is `reject` with `reason=I8`
- **AND** the mover is not called

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

### Requirement: T5 G_design measures the clone gate
When `process_event()` measures `g_design` (argument omitted), it SHALL set the predicate from `files_g_design` composed with the design-route-clone-gate: OpenSpec files present **and** clone-gate pass. `submeter_design` from Design with actor Agent MUST `reject` with `reason` starting with `guard:` when that predicate is false. The YAML transition T5 (`guard: G_design`) MUST stay unchanged. T5 MUST remain offline: no authenticated Playwright and no production credentials inside `process_event`.

#### Scenario: T5 refuses a gallery proto for an existing route
- **WHEN** `process_event submeter_design` runs with `g_design` unset, `q=Design`, valid card binding, `design.md` declaring `UI impact: affected` and `live_route: /monitor`, and the prototype HTML is the r1 gallery fixture (no `table.signals`, `copied` 0)
- **THEN** the result is `reject`
- **AND** the mover is not called
- **AND** `reason` starts with `guard:`

#### Scenario: T5 still accepts UI none OpenSpec package
- **WHEN** `process_event submeter_design` runs with `g_design` unset, `q=Design`, valid card binding, and `design.md` declaring `UI impact: none` plus the three Markdown files and a spec
- **THEN** the result is `transition` to Aprovação de Design when other T5 preconditions hold
- **AND** catalog/`copied` are not required

