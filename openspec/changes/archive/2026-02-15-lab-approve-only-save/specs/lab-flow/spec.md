# Lab Flow - Persistência Condicional de Templates

## ADDED Requirements

### Requirement: Template Draft Não Persistido
**Description:** The system SHALL NOT save templates to `combo_templates` table during Lab development phase (draft/candidate iterations).

#### Scenario: Desenvolvimento de estratégia
- **GIVEN** uma run do Lab está em andamento
- **WHEN** o Dev gera um candidato de template
- **THEN** o template NÃO deve ser salvo na tabela `combo_templates`
- **AND** o template deve existir apenas no contexto da run (memória/log)

### Requirement: Template Só Persiste Após Aprovação
**Description:** The system SHALL ONLY persist templates to `combo_templates` when explicitly approved by the Trader.

#### Scenario: Trader aprova estratégia
- **GIVEN** o Dev submete uma estratégia para review do Trader
- **AND** o Trader clica em "Aprovar"
- **WHEN** a aprovação é processada
- **THEN** o template deve ser salvo na tabela `combo_templates`
- **AND** o template deve ter nome único e descritivo
- **AND** o template deve estar disponível na tela `/combo/select`

### Requirement: Template Rejeitado é Descartado
**Description:** The system SHALL NOT persist templates when rejected by the Trader.

#### Scenario: Trader rejeita estratégia
- **GIVEN** o Dev submete uma estratégia para review do Trader
- **AND** o Trader clica em "Rejeitar"
- **WHEN** a rejeição é processada
- **THEN** NENHUM template deve ser criado em `combo_templates`
- **AND** os dados da run podem ser mantidos em log (para análise) mas não como template utilizável

### Requirement: Remover Auto-Save de Templates
**Description:** The system MUST REMOVE any automatic saving of templates to `combo_templates` during Lab execution.

#### Scenario: Execução de candidato
- **GIVEN** um candidato é gerado no Lab
- **WHEN** o candidato é criado
- **THEN** ele NÃO deve ser automaticamente salvo como template
- **AND** deve ficar disponível apenas para o fluxo de review do Trader
