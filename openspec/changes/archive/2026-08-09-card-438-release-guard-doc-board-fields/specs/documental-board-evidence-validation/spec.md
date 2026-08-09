## ADDED Requirements

### Requirement: Validação de evidência documental antes de Pronto
O `release-guard post` SHALL falhar se a doc do pacote de release não estiver commitada ou contiver placeholders, e se houver 2+ docs de release da mesma data com conteúdo divergente.

#### Scenario: Doc com placeholder não commitada
- **WHEN** a doc de release do pacote contém placeholders ou não está commitada em develop/main
- **THEN** `release-guard post` falha com blocker indicando a doc e os placeholders

#### Scenario: Docs da mesma data divergentes
- **WHEN** existem 2+ docs de release da mesma data com conteúdo divergente
- **THEN** `release-guard post` falha exigindo uma doc canônica única

#### Scenario: Doc canônica commitada
- **WHEN** existe exatamente uma doc de release para a data, commitada e sem placeholders
- **THEN** o check documental passa

### Requirement: Validação de campos do board antes de Pronto
O `release-guard post` SHALL falhar se card do pacote estiver sem `Responsável`, `Prioridade` ou `Tipo`, e se o título board/issue estiver divergente (vinculado a #430).

#### Scenario: Card do pacote sem campos
- **WHEN** um card do pacote está sem Responsável, Prioridade ou Tipo
- **THEN** `release-guard post` falha listando o card e os campos faltantes

#### Scenario: Campos completos
- **WHEN** todos os cards do pacote têm Responsável, Prioridade e Tipo preenchidos e títulos consistentes
- **THEN** o check de campos passa
