# process-fsm Specification

## Purpose
Tabela EFSM compilável das 12 colunas do processo (`T0`–`T17` + fixtures), versionada em `.cursor/process-fsm.yaml`. Consumida pelo resolver (#610), pelo Guard Write (#611) e pelo `process_event` (#612).
## Requirements
### Requirement: Process FSM table is versioned YAML
The repository SHALL contain `.cursor/process-fsm.yaml` as the compilable source of the 12-column EFSM defined in issue #608. The file MUST declare `states`, `transitions` matching the T0–T18 matrix in `design.md` (including T17a, T17b, and T18), `illegal_events`, `illegal_edges`, `enabled_tools` per state, `enabled_events` per state, `context_file` stub per state, invariants I1 through I9, and `fail_closed_asymmetric: true`. The packaged yaml MUST NOT declare `product_globs` or `design_globs` as law; those lists SHALL live in `.covenant-flow/overlay.yaml`. Column **names** in the yaml remain the law for the 12 statuses.

Legal event alphabet Σ SHALL be exactly: `criar_card`, `priorizar`, `cancelar`, `iniciar_design`, `recriticar`, `submeter_design`, `devolver_design`, `aprovar_design`, `iniciar_apply`, `pedir_review`, `achar_bloqueante`, `aceitar_sha`, `rerun_infra`, `falha_codigo`, `integrar_develop`, `homologar`, `nao_homologar`, `fechar_release`, `invalidar_aprovacao`.

#### Scenario: Table lists legal transitions
- **WHEN** the yaml is loaded by the validator
- **THEN** transitions T0–T16 plus T17a, T17b, and T18 are present with `from`, `event`, `actor`, `actions`, and `to` matching the design.md matrix
- **AND** T17a is Pronto para Dev -- invalidar_aprovacao --> Design
- **AND** T17b is Em desenvolvimento -- invalidar_aprovacao --> Design
- **AND** T18 is Done -- nao_homologar --> Em desenvolvimento

#### Scenario: request_implement is not a transition
- **WHEN** the validator inspects `transitions[]`
- **THEN** no transition has event `request_implement`
- **AND** `request_implement` is listed under `illegal_events` (not `illegal_edges` alone) and yields `reject`

#### Scenario: Packaged yaml does not declare globs as law
- **WHEN** the product `process-fsm.yaml` is validated
- **THEN** it does not declare `product_globs` or `design_globs` as yaml law keys
- **AND** it still declares T0–T18, I1–I9, 12 column names, events, and `enabled_tools`
- **AND** `product_globs` and `design_globs` are read from `.covenant-flow/overlay.yaml`

### Requirement: Product write is gated by I1 not banned globally
`write_produto` MUST NOT appear in `illegal_events`. It SHALL be modeled as a Moore/tool action allowed only when invariant I1 holds (`q` in Em desenvolvimento or Code Review, `q_git=card-<id>`, `bound_card=id`, path in that worktree). Combinations that violate I1 MUST appear in `illegal_edges` and yield `reject`.

#### Scenario: Write allowed under I1
- **WHEN** the fixture applies `write_produto` in Em desenvolvimento with `bound_card` set and `q_git=card-<id>`
- **THEN** the expected result is `allow`

#### Scenario: Illegal Write in Todo
- **WHEN** the fixture applies `write_produto` in state Todo
- **THEN** the expected result is `reject` and the state is unchanged

#### Scenario: Agent cannot approve design
- **WHEN** the fixture applies `aprovar_design` with actor Agent
- **THEN** the expected result is `reject`

#### Scenario: Unbound product write
- **WHEN** the fixture applies `write_produto` with `bound_card` unset
- **THEN** the expected result is `reject`

### Requirement: Validator rejects an incomplete or nondeterministic table
`scripts/process-fsm/` SHALL validate schema completeness, expansion of `from: Vivo` for T2, and that at most one transition is enabled for a given `(state, event, guard)` tuple. Determinism checks MUST cover Design (T4 vs T5), Code Review (T10 vs T11), and QA (T12/T13/T14). T1 (`priorizar`), T7 (`aprovar_design`), T15 (`homologar`), and T18 (`nao_homologar`) MUST include actor Alan. T16 (`fechar_release`) MUST include actor Agent and MUST NOT be validated as an Alan-only gate.

#### Scenario: Missing T7 actor Alan
- **WHEN** a yaml omits Alan as actor on `aprovar_design`
- **THEN** validation MUST fail

#### Scenario: Missing Alan on other human gates
- **WHEN** a yaml omits Alan as actor on `priorizar`, `homologar`, or `nao_homologar`
- **THEN** validation MUST fail

#### Scenario: T16 requires Agent not Alan-only
- **WHEN** a yaml sets T16 `fechar_release` actor to Alan only, or omits Agent
- **THEN** validation MUST fail

#### Scenario: Overlapping QA guards
- **WHEN** two transitions from QA share an event with non-exclusive guards
- **THEN** validation MUST fail

### Requirement: Fixtures live under scripts/process-fsm and run without GitHub
The change SHALL include pytest modules matching `scripts/process-fsm/test_*.py` that exercise the design.md matrix and the illegal edges Todo+Write, develop+Write, Done+Write, Agent+T7, and unbound+Write. Tests MUST NOT call GitHub, Cursor hooks, or the Project board. Continuous integration MUST run `pytest scripts/process-fsm -q`.

#### Scenario: Pytest path
- **WHEN** a contributor runs `pytest scripts/process-fsm -q` at the repo root
- **THEN** the legal and illegal fixtures execute and the command exits 0 for a valid yaml

### Requirement: Card 609 does not enable Cursor write hooks
This change MUST NOT register `preToolUse` or `beforeShellExecution` guards and MUST NOT modify product code under `backend/` or `frontend/src/`.

#### Scenario: hooks.json unchanged by this card
- **WHEN** the #609 diff is reviewed
- **THEN** `.cursor/hooks.json` is unmodified
- **AND** no `Write` of product paths is introduced

### Requirement: Named yaml guards are evaluated
`evaluate()` SHALL interpret the optional `guard` field on a transition (`G_design`, `q_git_card`, `digest_changed`, `M_lote`, `checks_green`, `open_p0_p1`, `reviewers_ok`, `flaky_infra`, `source_failure`, `motivo_visivel`). `q_git_card` MUST be derived from `ctx.q_git` via the existing `CARD_GIT_RE` (not a disconnected boolean). A named guard whose predicate in `EvalContext` is `False` MUST yield `reject` with `reason` starting with `guard:`. A named guard whose predicate is `None` MUST yield `reject` (fail-closed). A transition without `guard` MUST not require these predicates. Independently of the yaml `guard:` field, `iniciar_apply` and `pedir_review` MUST reject with `reason=I4` when `digest_changed` is True or None. Event `write_produto` MUST continue to use I1 / illegal_edges and MUST ignore those named guards.

#### Scenario: T8 without card git is rejected
- **WHEN** `evaluate` runs `iniciar_apply` from Pronto para Dev with actor Agent and `q_git_card` predicate false (`q_git=develop`)
- **THEN** the result is `reject` and `to` is unset

#### Scenario: T16 without M_lote is rejected
- **WHEN** `evaluate` runs `fechar_release` from Homologado with `M_lote` false
- **THEN** the result is `reject`

#### Scenario: Legal T8 still transitions when q_git_card is true
- **WHEN** `evaluate` runs `iniciar_apply` from Pronto para Dev with actor Agent, `q_git` matching `card-<id>-*`, and `digest_changed` false
- **THEN** the result is `transition` to Em desenvolvimento with reason `T8`

#### Scenario: T8 with digest changed is I4 not T8
- **WHEN** `evaluate` runs `iniciar_apply` from Pronto para Dev with actor Agent, `q_git` matching `card-<id>-*`, and `digest_changed` true
- **THEN** the result is `reject` with `reason=I4`
- **AND** `to` is unset

#### Scenario: T9 with digest missing is I4
- **WHEN** `evaluate` runs `pedir_review` from Em desenvolvimento with actor Agent and `digest_changed` is None
- **THEN** the result is `reject` with `reason=I4`

#### Scenario: T17 requires Guard actor
- **WHEN** `evaluate` runs `invalidar_aprovacao` from Pronto para Dev with actor Agent and `digest_changed` true
- **THEN** the result is `reject` (`reason=actor`)
- **AND** the same event with actor Guard and `digest_changed` true is `transition` to Design (`T17a`)

#### Scenario: T17b from Em desenvolvimento
- **WHEN** `evaluate` runs `invalidar_aprovacao` from Em desenvolvimento with actor Guard and `digest_changed` true
- **THEN** the result is `transition` to Design with reason `T17b`

#### Scenario: T18 without visible reason stays Done
- **WHEN** `evaluate` runs `nao_homologar` from Done with actor Alan and `motivo_visivel` false or None
- **THEN** the result is `reject` with `reason` starting with `guard:`
- **AND** `to` is unset
- **AND** the state remains Done

### Requirement: T16 actor is Agent with M_lote
Transition T16 in `.cursor/process-fsm.yaml` SHALL be `Homologado --fechar_release, Agent, guard M_lote--> Pronto` with actions including `release_guard` and `set_status`. Invariant I2 SHALL list Alan-only as T1, T7, T15, and T18 (not T16). Invariant I9 SHALL remain: T16 requires `M_lote`. `enabled_tools` for Homologado SHALL include `process_event`. `evaluate()` with actor Agent, state Homologado, event `fechar_release`, and `M_lote` true SHALL `transition` to Pronto with reason `T16`.

#### Scenario: Agent fechar_release with M_lote transitions
- **WHEN** `evaluate` runs `fechar_release` from Homologado with actor Agent and `M_lote` true
- **THEN** the result is `transition` to Pronto with reason `T16`

#### Scenario: T16 without M_lote is still rejected
- **WHEN** `evaluate` runs `fechar_release` from Homologado with actor Agent and `M_lote` false
- **THEN** the result is `reject`

### Requirement: Moore stubs describe grill-card without new states

`.cursor/process-fsm.yaml` `context_file` stubs SHALL describe the grill-card ritual without adding states or changing T0/T1. `context_file[Em Refinamento]` SHALL tell the agent to clarify the card and grill the GitHub issue, that chat is not T1, and not to write `CONTEXT.md` on develop. `context_file[Todo]` SHALL contain the exact substring `Próximo evento = iniciar_design. Não apply. Não /opsx:new ainda.` `context_file[Design]` SHALL tell the agent to synthesize OpenSpec from the grilled issue and not to re-interview. sessionStart paging MUST remain ≤20 lines. `enabled_tools` for Em Refinamento SHALL remain `[issue_edit, comment]` and MUST NOT add `write_openspec`.

#### Scenario: Todo stub keeps paging contract
- **WHEN** `.cursor/process-fsm.yaml` `context_file.Todo` is read
- **THEN** it contains `Próximo evento = iniciar_design. Não apply. Não /opsx:new ainda.`

#### Scenario: Em Refinamento stub names issue grilling
- **WHEN** `.cursor/process-fsm.yaml` `context_file['Em Refinamento']` is read
- **THEN** it mentions clarifying the card and that chat is not T1
- **AND** it mentions grill-card or grilling the issue

#### Scenario: T0 and T1 unchanged
- **WHEN** the compiled transition table is inspected
- **THEN** T0 still targets Em Refinamento
- **AND** T1 `priorizar` remains Alan-only from Em Refinamento to Todo

#### Scenario: Em Refinamento tools stay issue-only
- **WHEN** `.cursor/process-fsm.yaml` `enabled_tools` for Em Refinamento is read
- **THEN** it is `[issue_edit, comment]`
- **AND** it does not include `write_openspec`

### Requirement: Moore QA stub requires same-turn T14
`.cursor/process-fsm.yaml` `context_file[QA]` SHALL tell the parent to leave product source untouched. The stub MUST name both client paths in one short Moore page: Cursor/Grok — the QA child (when the client spawns one) reads checks and MUST NOT call `process_event`; dsh — the runtime root MUST NOT spawn a QA child and MUST wait for `qa-gate` in the same turn (`job_output wait`, without `continue`). The parent MUST invoke `integrar_develop` in the same turn as a green child (or, on dsh, after `qa-gate` success). The stub MUST say the first reject is not the end of the turn: `qa-gate pending` waits and retries T14; `no_pr` and `sync: dirty` are visible causes. The stub MAY still mention T13 returning to Em desenvolvimento. sessionStart paging MUST remain at most 20 lines. This change MUST NOT add a state, event, or `enabled_tools` entry.

#### Scenario: QA stub names same-turn T14
- **WHEN** `.cursor/process-fsm.yaml` `context_file.QA` is read
- **THEN** it tells the parent to call T14 in the same turn as green QA
- **AND** it says the first reject is not the end of the turn
- **AND** it tells the QA child not to call `process_event`

#### Scenario: QA paging stays short
- **WHEN** `page()` compiles a bound card with `q=QA`
- **THEN** `additional_context` is at most 20 lines
- **AND** it contains the yaml `context_file[QA]` stub

#### Scenario: QA stub names dsh root closeout
- **WHEN** `.cursor/process-fsm.yaml` `context_file.QA` is read
- **THEN** it says the dsh root MUST NOT spawn a QA child
- **AND** it says to wait for `qa-gate` in the turn without `continue`
- **AND** it still tells a Cursor/Grok QA child not to call `process_event`

### Requirement: T18 returns the same card from Done to Em desenvolvimento
Transition T18 in `.cursor/process-fsm.yaml` SHALL be `Done --nao_homologar, Alan, guard motivo_visivel--> Em desenvolvimento` with actions including `set_status`. `enabled_events` for Done SHALL be `[homologar, nao_homologar, cancelar]`. T15 (`homologar` → Homologado) MUST remain unchanged. Homologado MUST NOT gain an inverse edge in this change. `enabled_tools` for Done SHALL remain empty.

`motivo_visivel` SHALL be true only when the bound issue has a comment containing the marker `Não homologar:` followed by non-empty reason text. Chat-only text, an empty body, or an Agent-only comment MUST NOT satisfy the guard. `evaluate()` with actor Alan, state Done, event `nao_homologar`, and `motivo_visivel` true SHALL `transition` to Em desenvolvimento with reason `T18`. The same event with actor Agent MUST `reject` (`reason=actor`) and MUST NOT change state.

The overlay anti-regression that forbids Done → Em desenvolvimento SHALL be punctured only by this Alan gesture with visible reason. Agent, archive, commit, PR, merge, and closeout MUST still reject that move. After a legal T18, product Write remains gated by I1 (card worktree, not `develop`/`main`); the card MUST NOT skip to QA or Design via this event. Always-on and runbook surfaces that enumerate Alan-only gates SHALL include T18.

#### Scenario: Alan nao_homologar with visible reason returns to Em desenvolvimento
- **WHEN** `evaluate` runs `nao_homologar` from Done with actor Alan and `motivo_visivel` true
- **THEN** the result is `transition` to Em desenvolvimento with reason `T18`
- **AND** the destination is not Cancelado, QA, or Design

#### Scenario: Agent cannot nao_homologar
- **WHEN** `evaluate` runs `nao_homologar` from Done with actor Agent and `motivo_visivel` true
- **THEN** the result is `reject` with `reason=actor`
- **AND** the state remains Done

#### Scenario: Homologado has no undo from this change
- **WHEN** the compiled transition table is inspected
- **THEN** no transition has `from: Homologado` and `to` other than Pronto or Cancelado
- **AND** T15 remains Done -- homologar --> Homologado

