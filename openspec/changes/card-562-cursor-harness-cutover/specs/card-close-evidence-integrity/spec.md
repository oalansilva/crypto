## MODIFIED Requirements

### Requirement: Todos completos no fechamento de card
O `/opsx:verify` e o fechamento de card SHALL exigir que os todos da sessão Cursor associada ao card estejam concluídos (nenhum `in_progress`/`pending` no `TodoWrite` da sessão). MUST NOT consultar `opencode.db` como fonte ativa.

#### Scenario: Todo in_progress em card Done
- **WHEN** existe todo `in_progress`/`pending` na sessão Cursor do card
- **THEN** `/opsx:verify` falha e o fechamento do card não é concluído

#### Scenario: Todos completos
- **WHEN** os todos da sessão do card estão `completed`
- **THEN** o fechamento técnico do card pode ser concluído

### Requirement: Título descritivo em sessões caras
Sessões Cursor com custo alto ou trabalho de card SHALL ter título descritivo (card/contexto), não genérico.

#### Scenario: Sessão cara com título genérico
- **WHEN** uma sessão de card tem título não descritivo
- **THEN** a auditoria kaizen reporta como achado

#### Scenario: Sessão cara com título descritivo
- **WHEN** uma sessão tem título com card/contexto
- **THEN** a auditoria aceita sem achado nesse sinal
