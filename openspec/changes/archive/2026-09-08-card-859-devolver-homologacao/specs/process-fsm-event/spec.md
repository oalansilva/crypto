## MODIFIED Requirements

### Requirement: Human gates and lote stub reject the Agent
Events `priorizar`, `aprovar_design`, `homologar`, and `nao_homologar` MUST reject when invoked via `process_event()`. `fechar_release` MUST reject when predicate `M_lote` is false. Every `fechar_release` reject caused by ¬`M_lote` MUST contain `covenant-flow-environments` and `release-guard`. `process_event()` MUST NOT run deploy PROD (`git reset` no path PROD, `systemctl` PROD) as part of `fechar_release`.

#### Scenario: Agent cannot fire T1 T15
- **WHEN** `process_event()` is invoked with `priorizar` or `homologar`
- **THEN** each result is `reject` and the mover is not called

#### Scenario: Agent cannot fire nao_homologar
- **WHEN** `process_event()` is invoked with `nao_homologar`
- **THEN** the result is `reject`
- **AND** the mover is not called
- **AND** Status remains Done

#### Scenario: M_lote false rejects T16
- **WHEN** event is `fechar_release` and `M_lote` is false
- **THEN** the result is `reject`
- **AND** the mover is not called
- **AND** the message contains `covenant-flow-environments` and `release-guard`
