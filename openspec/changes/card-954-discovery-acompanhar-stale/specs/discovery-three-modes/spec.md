## ADDED Requirements

### Requirement: Acompanhar leaves when this run closes

When the server marks **this** active Discovery sweep terminal, the Descoberta UI SHALL leave Acompanhar (no chip **EM CURSO**, no copy **Varredura em execução**, no counter frozen at 0 of N). Without a click and without a reload, the operator SHALL see the closed ranking in **Decidir of this sweep** (the candidate of this `sweep_id` visible). The UI SHALL NOT show a screen «Acompanhar já concluída». Opening Histórico / Decidir of a **different** sweep SHALL NOT count as this transition.

Acompanhar SHALL remain available only while this run is still non-terminal (em curso or pausada), per the existing three-mode contract.

#### Scenario: Server closes this one-combination run

- **GIVEN** Acompanhar is following sweep `#00e9a4d28e114099bc18fc85d5500df3` and Histórico may display another run
- **WHEN** the server marks that same sweep `completed` with its candidate persisted
- **THEN** Acompanhar is no longer EM CURSO / «Varredura em execução» with 0 de 1
- **AND** the operator sees Decidir of `#00e9a4d28e114099bc18fc85d5500df3` with that candidate
- **AND** there is no screen «Acompanhar já concluída»
- **AND** the operator did not click and did not reload

#### Scenario: Other-run Histórico is not the fix

- **GIVEN** Acompanhar is following the active sweep
- **WHEN** Histórico is open on a different completed sweep
- **THEN** that other ranking is not treated as the closed result of the active sweep
- **AND** the copy that the active sweep is separado do Histórico exibido MAY remain while the active run still runs
