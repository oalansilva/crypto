# multiagent-operating-standard Specification

## Purpose
Modelo operacional padronizado dos agentes persistentes do projeto (main, PO, DESIGN, DEV, QA e Kaizen) e suas regras de operação.

## ADDED Requirements

### Requirement: O papel Kaizen integra o modelo operacional
O modelo operacional SHALL incluir o papel Kaizen (melhoria contínua) com responsabilidades de auditoria, registro de melhorias como cards PO (`Status=Todo`, máx. 3 por release), priorização P0/P1/P2 e regra "propõe, Alan aprova" (nunca implementa mudanças de regra/skill/script sem aprovação explícita).

#### Scenario: Kaizen registra melhoria no backlog
- **WHEN** a auditoria kaizen identifica uma melhoria acionável
- **THEN** o Kaizen cadastra 1 card por melhoria com label `kaizen`, formato PO e `Status=Todo`
- **AND** o card segue o fluxo normal do board a partir daí

#### Scenario: Limite de cards por release
- **WHEN** a auditoria de uma release gera mais de 3 melhorias
- **THEN** os 3 de maior prioridade entram na release atual
- **AND** o restante permanece no backlog kaizen para releases seguintes

#### Scenario: Mudança de processo exige aprovação humana
- **WHEN** o Kaizen propõe mudança de regra, skill ou script
- **THEN** a implementação ocorre somente após aprovação explícita de Alan
