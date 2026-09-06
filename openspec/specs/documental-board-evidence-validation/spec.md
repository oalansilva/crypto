# documental board evidence validation Specification

## Purpose
TBD - created by syncing change card-438-release-guard-doc-board-fields.
## Requirements
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

### Requirement: Card evidence comments are listed over REST
`scripts/post-card-evidence-comment.sh` SHALL list existing issue comments via REST `GET /repos/<owner>/<repo>/issues/<n>/comments` (paginate as needed). It MUST NOT call `gh issue view --json comments` (GraphQL). If the REST list fails or returns invalid JSON, the script MUST refuse to post (fail-closed), unchanged from today's fail-closed posture. GraphQL remaining=0 MUST NOT block this REST list. Dedup by transition marker and commit ref remains.

#### Scenario: Comments fetch uses REST
- **WHEN** the script loads comments for card N before posting evidence
- **THEN** it calls REST `/issues/N/comments`
- **AND** the script source MUST NOT contain `gh issue view --json comments`

#### Scenario: REST comments failure stays fail-closed
- **WHEN** the REST comments list fails or is not a JSON array of comment objects
- **THEN** the script errors and MUST NOT post a new comment

#### Scenario: GraphQL quota 0 does not block REST comments
- **WHEN** GraphQL headers remaining=0 and REST comments GET succeeds
- **THEN** the script may read comments and post when the marker/SHA rules allow

