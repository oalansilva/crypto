# card close evidence integrity Specification

## Purpose
TBD - created by syncing change card-440-card-close-todos-session-title.
## Requirements

### Requirement: Todos completos no fechamento de card
O `/opsx:verify` e o fechamento de card SHALL exigir todos `completed` (0 todos `in_progress`/`pending`) nas sessões associadas a cards `Done`.

#### Scenario: Todo in_progress em card Done
- **WHEN** existe todo `in_progress`/`pending` em sessão associada a um card `Done`
- **THEN** `/opsx:verify` falha e o fechamento do card não é concluído

#### Scenario: Todos completos
- **WHEN** todos os todos das sessões associadas ao card estão `completed`
- **THEN** o fechamento do card pode ser concluído

### Requirement: Título descritivo em sessões caras
Sessões do opencode com custo > $0.10 SHALL ter título descritivo (card/contexto), não genérico.

#### Scenario: Sessão cara com título genérico
- **WHEN** uma sessão com custo > $0.10 tem título não descritivo (ex.: "Casual greeting")
- **THEN** a auditoria kaizen reporta como achado e o fluxo exige renomeação/título descritivo

#### Scenario: Sessão cara com título descritivo
- **WHEN** uma sessão cara tem título com card/contexto
- **THEN** a auditoria aceita sem achado

### Requirement: Publicação única de comentário OpenSpec
O helper `publish-openspec-card-artifacts` SHALL atualizar gist/comentário existente em republicações, evitando comentário OpenSpec duplicado no card (sinergia #423).

#### Scenario: Republicação sem duplicação
- **WHEN** os artefatos OpenSpec de um card são republicados
- **THEN** o comentário OpenSpec existente é atualizado e nenhum comentário duplicado é criado

### Requirement: Incomplete QA tasks block card close
`/opsx:verify` and Done technical SHALL fail when any test/QA task in `tasks.md` is still `[ ]`, or when a UI task is `[x]` without implementation evidence.

#### Scenario: False-complete UI checklist
- **WHEN** UI tasks are `[x]` but the described UI is missing
- **THEN** card close is blocked

#### Scenario: Open Playwright task
- **WHEN** a Playwright task is `[ ]` at Done
- **THEN** card close is blocked
