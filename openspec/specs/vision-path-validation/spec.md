# vision path validation Specification

## Purpose
TBD - created by syncing change card-439-vision-path-check.
## Requirements

### Requirement: Path-check antes de delegar análise visual
Antes de passar arquivos ao subagent vision, o fluxo de QA visual SHALL confirmar a existência dos paths (`ls`/glob) e a validade das URLs; arquivo inexistente ou URL inválida bloqueia a delegação.

#### Scenario: Path inexistente na delegação
- **WHEN** um path de imagem/artefato não existe no momento da delegação ao vision
- **THEN** a delegação não é feita com o path inválido
- **AND** o artefato é gerado antes de qualquer respawn

#### Scenario: URL inválida
- **WHEN** uma URL não é resolvível (404/erro) antes da delegação
- **THEN** o fluxo não delega com a URL inválida e registra o bloqueio

#### Scenario: Paths validados
- **WHEN** todos os paths existem e as URLs são válidas
- **THEN** a delegação ao vision prossegue sem respawn por arquivo inexistente
