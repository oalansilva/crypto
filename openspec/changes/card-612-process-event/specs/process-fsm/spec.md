## ADDED Requirements

### Requirement: Named yaml guards are evaluated
`evaluate()` SHALL interpret the optional `guard` field on a transition (`G_design`, `q_git_card`, `digest_changed`, `M_lote`, `checks_green`, `open_p0_p1`, `reviewers_ok`, `flaky_infra`, `source_failure`). `q_git_card` MUST be derived from `ctx.q_git` via the existing `CARD_GIT_RE` (not a disconnected boolean). A named guard whose predicate in `EvalContext` is `False` MUST yield `reject` with `reason` starting with `guard:`. A named guard whose predicate is `None` MUST yield `reject` (fail-closed). A transition without `guard` MUST not require these predicates. Independently of the yaml `guard:` field, `iniciar_apply` and `pedir_review` MUST reject with `reason=I4` when `digest_changed` is True or None. Event `write_produto` MUST continue to use I1 / illegal_edges and MUST ignore those named guards.

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
