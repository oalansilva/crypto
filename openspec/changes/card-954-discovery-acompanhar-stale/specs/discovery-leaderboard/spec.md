## ADDED Requirements

### Requirement: Acompanhar parciais show the candidate before the run closes

While the active Discovery sweep is still non-terminal, Acompanhar locked top-5 parciais SHALL show a candidate row as soon as that result exists for **this** sweep. The empty copy **Parciais ainda carregando** SHALL NOT remain in that state. The Acompanhar progress counter SHALL NOT display 0 of N when this sweep has already processed combinations. Parciais SHALL keep being a top-5 of this sweep (no pagination, no becoming Decidir). Montar SHALL keep Preflight and Rascunho without this card's partials delta.

#### Scenario: Candidate exists mid-run

- **GIVEN** a non-terminal sweep the Acompanhar is following, and a ranked result for that sweep already exists
- **WHEN** the operator stays on Acompanhar without reloading
- **THEN** the parciais table shows that candidate line
- **AND** the phrase «Parciais ainda carregando» is not shown

#### Scenario: Progress is not stuck at zero after processing

- **GIVEN** the active sweep has `processed > 0`
- **WHEN** Acompanhar shows the progress of that sweep
- **THEN** the counter is not 0 de N
- **AND** the displayed processed count matches this sweep, not another run in Histórico
