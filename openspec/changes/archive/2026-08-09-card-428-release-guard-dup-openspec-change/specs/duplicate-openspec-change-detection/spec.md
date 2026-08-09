## ADDED Requirements

### Requirement: Detecção de change OpenSpec duplicada no post
O `release-guard post` SHALL verificar que nenhuma change ativa em `openspec/changes/` tem correspondente em `openspec/changes/archive/*/`, falhando/diagnosticando quando houver duplicação após sync `main -> develop`.

#### Scenario: Change ativa e arquivada simultaneamente
- **WHEN** uma change existe em `openspec/changes/<change>/` e em `openspec/changes/archive/*/<change>/`
- **THEN** `release-guard post` lista a duplicação como blocker com instrução de correção

#### Scenario: Sync não reintroduz duplicação
- **WHEN** o sync `main -> develop` pós-publicação é executado com check ativo
- **THEN** nenhuma change ativa duplicada (ativa + arquivada) permanece

#### Scenario: Sem duplicação
- **WHEN** toda change ativa tem apenas pasta ativa e toda change arquivada está apenas em `archive/`
- **THEN** o check de duplicação passa sem blockers
