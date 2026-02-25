# Δ lab Specification — remove-auto-gate-cp10

## MODIFIED Requirements

### Requirement: Remove automatic CP10 selection gate

**Description:** The system SHALL remove the automatic CP10 selection gate from the Lab decision path. When execution reaches the post-implementation selection point, the flow SHALL continue to Trader validation without any automatic approve/reject outcome from CP10.

#### Scenario: CP10 no longer decides automatically
- **GIVEN** um Lab run com resultado de implementação pronto para avaliação
- **WHEN** o fluxo atinge o ponto onde o CP10 era aplicado
- **THEN** o sistema NÃO DEVE executar decisão automática de seleção
- **AND** o run DEVE seguir para validação do Trader

### Requirement: Trader is the single approval authority

**Description:** The system SHALL treat the Trader verdict as the only authority for final approval decisions in this stage. Any legacy auto-gate flag or CP10-derived decision MUST NOT finalize, approve, or reject a run.

#### Scenario: Final decision comes only from Trader
- **GIVEN** um run em fase de validação após implementação
- **WHEN** houver sinais de decisão automática legados do CP10
- **THEN** o sistema DEVE ignorar esses sinais para aprovação final
- **AND** DEVE aguardar e aplicar apenas o veredito do Trader (`approved`, `rejected`, `needs_adjustment`)

### Requirement: Run state must expose Trader-driven approval

**Description:** The system SHALL expose status and run outputs consistent with Trader-driven approval only, so UI and API consumers can infer that CP10 is no longer a decision gate.

#### Scenario: API and UI reflect Trader-only approval path
- **GIVEN** um run que passou do estágio de implementação
- **WHEN** cliente consulta status/outputs do run
- **THEN** os campos de estado DEVERÃO refletir decisão pendente/concluída do Trader
- **AND** NÃO DEVERÁ haver indicação de aprovação automática por CP10
