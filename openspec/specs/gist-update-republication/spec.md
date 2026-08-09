# gist update republication Specification

## Purpose
TBD - created by syncing change card-423-publish-helper-gist-update.
## Requirements

### Requirement: Publicação de artefatos OpenSpec atualiza Gist existente
O helper `publish-openspec-card-artifacts.sh` SHALL aceitar `--gist-id <id>` e atualizar o Gist existente em republicações, criando novo Gist apenas na primeira publicação por change.

#### Scenario: Republicação com gist-id
- **WHEN** o helper é executado com `--gist-id` de publicação anterior da mesma change
- **THEN** os arquivos do Gist existente são atualizados sem criar novo Gist
- **AND** o comentário do card é atualizado/evitado conforme o fluxo, sem duplicação

#### Scenario: Primeira publicação sem gist-id
- **WHEN** o helper é executado sem `--gist-id` pela primeira vez para a change
- **THEN** um novo Gist é criado e o comentário do card é publicado

#### Scenario: Sem novos Gists por change
- **WHEN** a change é republicada mais de uma vez
- **THEN** apenas um Gist existe para a change e nenhum comentário duplicado é criado

### Requirement: Retrigger de CI via workflow_dispatch
O retrigger de CI SHALL ser feito via `workflow_dispatch` (`gh workflow run`) quando possível, em vez de commit vazio.

#### Scenario: Retrigger necessário
- **WHEN** um check de CI precisa ser reagendado sem mudança de código
- **THEN** o retrigger usa `gh workflow run` (workflow_dispatch) e nenhum commit vazio é criado

#### Scenario: Agrupamento de ajustes pós-review
- **WHEN** ajustes pós-review são necessários
- **THEN** eles são agrupados em um único commit/PR por card, evitando PRs fragmentados
