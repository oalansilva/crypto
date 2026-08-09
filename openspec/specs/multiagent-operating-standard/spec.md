# multiagent-operating-standard Specification

## Purpose
TBD - created by archiving change standardize-multiagent-kadro-operating-model. Update Purpose after archive.
## Requirements
### Requirement: The operating model MUST preserve the current Kadro and persistent role agents
The project MUST preserve the current Kadro/Kanban flow and the persistent role agents `main`, `PO`, `DESIGN`, `DEV`, and `QA` while standardizing operation.

#### Scenario: Preserve the current operating structure
- **WHEN** this change is implemented
- **THEN** the current Kanban stage flow and persistent role agents MUST remain in place
- **AND** the change MUST improve operation without replacing that structure

### Requirement: The operating model MUST define explicit responsibilities for the current role agents
The operating model MUST explicitly define the responsibilities and completion expectations for the current persistent role agents.

#### Scenario: Role responsibilities are explicit
- **WHEN** a role participates in a stage transition
- **THEN** its operational responsibilities MUST be documented
- **AND** its completion expectations MUST be explicit

### Requirement: A stage MUST NOT count as complete without runtime state and handoff update
A stage MUST only count as complete when both the runtime/Kanban state and the operational handoff/comment have been updated.

#### Scenario: Validate a stage transition
- **WHEN** PO, DESIGN, DEV, or QA claims a stage is complete
- **THEN** the stage MUST NOT count as complete unless runtime reflects the transition
- **AND** the relevant handoff/comment has been published

### Requirement: Legacy coordination markdown MUST be treated as mirror/audit only
`docs/coordination/*.md` MUST be treated as mirror/audit support rather than the active operational source.

#### Scenario: Runtime differs from legacy coordination
- **WHEN** runtime/Kanban and legacy coordination differ
- **THEN** runtime/Kanban MUST remain the authoritative operational source
- **AND** legacy coordination MUST be treated as a mirror to reconcile, not the deciding execution surface


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
