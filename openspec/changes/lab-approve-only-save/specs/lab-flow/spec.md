# Lab Flow - Persistência Condicional de Templates

## ADDED Requirements

### Requirement: Template Draft Não Persistido
**Description:** The system SHALL NOT save templates to `combo_templates` table during Lab development phase (draft/candidate iterations).

#### Scenario: Desenvolvimento de estratégia
**Given** uma run do Lab está em andamento  
**When** o Dev gera um candidato de template  
**Then** o template NÃO deve ser salvo na tabela `combo_templates`  
**And** o template deve existir apenas no contexto da run (memória/log)

### Requirement: Template Só Persiste Após Aprovação
**Description:** The system SHALL ONLY persist templates to `combo_templates` when explicitly approved by the Trader.

#### Scenario: Trader aprova estratégia
**Given** o Dev submete uma estratégia para review do Trader  
**And** o Trader clica em "Aprovar"  
**When** a aprovação é processada  
**Then** o template deve ser salvo na tabela `combo_templates`  
**And** o template deve ter nome único e descritivo  
**And** o template deve estar disponível na tela `/combo/select`

### Requirement: Template Rejeitado é Descartado
**Description:** The system SHALL NOT persist templates when rejected by the Trader.

#### Scenario: Trader rejeita estratégia
**Given** o Dev submete uma estratégia para review do Trader  
**And** o Trader clica em "Rejeitar"  
**When** a rejeição é processada  
**Then** NENHUM template deve ser criado em `combo_templates`  
**And** os dados da run podem ser mantidos em log (para análise) mas não como template utilizável

## MODIFIED Requirements

### Requirement: Remover Auto-Save de Templates
**Description:** The system MUST REMOVE any automatic saving of templates to `combo_templates` during Lab execution.

#### Scenario: Execução de candidato
**Given** um candidato é gerado no Lab  
**When** o candidato é criado  
**Then** ele NÃO deve ser automaticamente salvo como template  
**And** deve ficar disponível apenas para o fluxo de review do Trader

## REMOVED Requirements

- Auto-save de templates candidatos no banco (persistência temporária desnecessária)
- Criação automática de templates em `combo_templates` durante desenvolvimento
