# Δ backend Specification — dev-pythonrepl-fix-logic

## ADDED Requirements

### Requirement: Dev Agent must include PythonREPLTool
**Description:** The system MUST enable PythonREPLTool in the Dev agent so it can execute Python for validating and correcting logic expressions.

#### Scenario: Dev uses PythonREPLTool for logic validation
- **GIVEN** o Dev precisa validar uma expressão de lógica
- **WHEN** ele executa a verificação/correção
- **THEN** o Dev MUST poder usar PythonREPLTool
- **AND** o resultado da execução deve estar disponível para a decisão de correção

### Requirement: Dev correction precedes fallback logic
**Description:** When logic validation fails, the system SHALL attempt Dev correction using PythonREPLTool before applying any automatic fallback logic.

#### Scenario: Logic error triggers Dev correction first
- **GIVEN** a lógica de entrada/saída é inválida
- **WHEN** o erro é detectado no preflight
- **THEN** o sistema MUST solicitar correção ao Dev usando PythonREPLTool
- **AND** somente se falhar a correção, o sistema MAY aplicar fallback

### Requirement: Corrections must be logged
**Description:** The system SHALL persist correction metadata in the run trace, including original logic, corrected logic, and reason.

#### Scenario: Correction log is persisted
- **GIVEN** uma correção de lógica foi aplicada
- **WHEN** o run segue para execução
- **THEN** o trace MUST registrar lógica original, lógica corrigida e motivo
- **AND** o log deve indicar que a correção foi feita pelo Dev
