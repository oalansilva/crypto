## ADDED Requirements

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
Events `priorizar`, `aprovar_design`, `homologar`, and `fechar_release` MUST reject when invoked via `process_event()`. `fechar_release` MUST also reject when predicate `M_lote` is false. Every `fechar_release` reject message (actor or guard) MUST contain `alan-workflow-ambientes` and `release-guard`. `process_event()` MUST NOT run `release-guard`, deploy PROD, or set Status to `Pronto`.

#### Scenario: Agent cannot fire T1 T15 T16
- **WHEN** `process_event()` is invoked with `priorizar`, `homologar`, or `fechar_release`
- **THEN** each result is `reject` and the mover is not called
- **AND** the `fechar_release` message contains `alan-workflow-ambientes` and `release-guard`

#### Scenario: M_lote false rejects T16
- **WHEN** event is `fechar_release` and `M_lote` is false
- **THEN** the result is `reject`
- **AND** the message contains `alan-workflow-ambientes` and `release-guard`

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
For events that move an existing card, `bound_card=⊥` or a `--card` that does not match `q_git`'s `card-<id>` MUST yield `reject` without a mover call.

#### Scenario: Unbound process_event
- **WHEN** `bound_card` is `⊥` and the event is `iniciar_apply`
- **THEN** the result is `reject` and the mover is not called

### Requirement: T10-T13 events imply exclusive-group guards; T14 stays reject live
For `achar_bloqueante`, `aceitar_sha`, `rerun_infra`, and `falha_codigo`, `process_event()` SHALL set the matching yaml guard true from the event name and the other exclusive-group predicates false. `integrar_develop` MUST reject in live `process_event()` (`checks_green` unset) and MUST NOT call the mover.

#### Scenario: aceitar_sha from Code Review transitions
- **WHEN** `process_event()` is invoked with `aceitar_sha`, `q=Code Review`, valid card binding, and digest unchanged
- **THEN** the mover is called with `to=QA`

#### Scenario: integrar_develop rejects without checks_green
- **WHEN** `process_event()` is invoked with `integrar_develop` and `checks_green` is unset
- **THEN** the result is `reject` and the mover is not called
