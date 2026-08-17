# openspec archive hygiene Specification

## Purpose
Arquivar changes OpenSpec completas de cards terminais e detectar changes completas ainda ativas no guard de release.

## ADDED Requirements

### Requirement: Change completa de card terminal deve ser arquivada
Uma change OpenSpec com todos os artifacts done cujo card vinculado esteja em estado terminal (`Pronto` ou `Cancelado`) SHALL ser arquivada em `openspec/changes/archive/YYYY-MM-DD-<change>/`, com sync de delta specs quando aplicável.

#### Scenario: Change de card Pronto/Cancelado completa
- **WHEN** uma change tem 4/4 artifacts done e o card vinculado está em `Pronto` ou `Cancelado`
- **THEN** a change é movida para `openspec/changes/archive/YYYY-MM-DD-<change>/` e `openspec validate --all` permanece verde

#### Scenario: Change de card não terminal
- **WHEN** o card vinculado não está em estado terminal
- **THEN** a change permanece ativa e não é arquivada

### Requirement: Detecção de change completa de card terminal no guard
O release guard SHALL detectar, em `post`/`audit`, changes OpenSpec ativas com todos os artifacts done cujo card vinculado está em estado terminal, reportando como warn (audit) ou blocker com classificação (post).

#### Scenario: Guard post encontra change completa de card terminal
- **WHEN** `post` mode encontra uma change ativa com 4/4 artifacts done de card em `Pronto`/`Cancelado`
- **THEN** o guard reporta o achado exigindo archive/classificação antes do closeout

#### Scenario: Nenhuma change completa terminal
- **WHEN** todas as changes completas de cards terminais já foram arquivadas
- **THEN** o guard reporta ausência de achados
