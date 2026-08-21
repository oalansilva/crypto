## ADDED Requirements

### Requirement: Pronto closeout is process_event fechar_release
After an explicit release request, the Agent SHALL publish (`main`, deploy PROD, docs) using the overlay and `release-guard`. Closing Homologado → Pronto SHALL be `process_event fechar_release` with live `M_lote` (`release-guard post` PASS) for the `RELEASE_CARDS` package. The Agent MUST NOT treat `gh project item-edit` of Status or a chat `suba a release` / `autorizo Pronto` as T16. `priorizar`, `aprovar_design`, and `homologar` remain Alan-only. Always-on `harness.mdc` SHALL say Alan-only is T1/T7/T15 (not T16).

#### Scenario: Agent closes Homologado to Pronto after post PASS
- **WHEN** the package cards are Homologado, `release-guard post` exits 0, and the Agent runs `process_event fechar_release`
- **THEN** each package card moves to Pronto
- **AND** the Agent does not edit Project 1 Status via `gh project item-edit`

#### Scenario: Chat does not close Pronto
- **WHEN** the user says `implemente` or `autorizo Pronto` without `process_event fechar_release` succeeding
- **THEN** Status MUST remain Homologado
