# favorites Specification

## Purpose
TBD - created by syncing delta from change save-combo-favorites. Save combo strategy from results to favorites.

## Requirements

### Requirement: Salvar Estratégia dos Resultados do Combo
O sistema SHALL fornecer um mecanismo para salvar uma configuração específica de estratégia (incluindo parâmetros e métricas) da página de Resultados do Backtest de Combo para a lista de Favoritos. O fluxo inclui um botão "Salvar nos Favoritos" e um modal para nome e notas; o sistema SHALL evitar duplicatas, apresentando aviso para sobrescrever ou salvar como novo.

#### Scenario: Salvar nova estratégia
- **WHEN** the user clicks "Salvar nos Favoritos" on a new combo result
- **THEN** the system SHALL open a modal with name and optional notes
- **AND** the strategy SHALL be persisted to the favorites list

#### Scenario: Duplicate name warning
- **WHEN** the user enters a name that already exists in favorites
- **THEN** the system SHALL display a warning offering to overwrite or save as a new entry

### Requirement: Campo de Notas
O modal de salvamento SHALL incluir campo opcional "Notas", que SHALL ser persistido no banco junto com a estratégia.

#### Scenario: Notas persistidas
- **WHEN** the user fills in the optional notes field and saves
- **THEN** the notes SHALL be stored alongside the strategy in the database
- **AND** the notes SHALL be displayed when viewing the favorite

### Requirement: Armazenar Métricas Compostas
O sistema SHALL armazenar `total_return` como Retorno Composto ao salvar nos Favoritos. O painel de Favoritos SHALL exibir o mesmo retorno composto, não soma simples.

#### Scenario: Compound return stored and displayed
- **WHEN** the user saves a combo strategy to favorites
- **THEN** the system SHALL store `total_return` as the compound return
- **AND** the Favorites panel SHALL display the compound return, not a simple sum
