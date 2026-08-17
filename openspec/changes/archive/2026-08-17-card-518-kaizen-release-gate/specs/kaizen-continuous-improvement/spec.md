# kaizen-continuous-improvement Delta Specification

## MODIFIED Requirements

### Requirement: Auditoria kaizen read-only disponível via command

O opencode SHALL expor o command `/kaizen` com modos de auditoria: `/kaizen` (completa), `/kaizen card <id>` (pós-card) e `/kaizen release` (pós-release), executando a coleta de evidências sem mutar board, Git, PRs ou runtime. No fechamento de release, `/kaizen release` MUST ocorrer após o deploy PROD validado e antes do `release-guard post` e da promoção para `Pronto`; seu relatório SHALL ser versionado em `docs/kaizen-log.md` no único PR documental do fechamento.

#### Scenario: Auditoria completa executada
- **WHEN** o usuário invoca `/kaizen`
- **THEN** o subagent kaizen coleta evidências de board, Git, OpenSpec, CI e sessões do opencode
- **AND** o relatório é anexado em `docs/kaizen-log.md` sem alterações em código de produto

#### Scenario: Auditoria pós-release executada na ordem canônica
- **WHEN** o deploy PROD do pacote foi validado e os cards ainda não estão em `Pronto`
- **THEN** `/kaizen release` é executado com escopo de sessões dos cards do pacote
- **AND** a evidência da auditoria é versionada em `docs/kaizen-log.md` antes do `post`

#### Scenario: Auditoria está ausente no post
- **WHEN** o fechamento tenta executar `post` sem entrada kaizen canônica para a data da release
- **THEN** o guard bloqueia e os cards não são movidos para `Pronto`

## ADDED Requirements

### Requirement: Resultado vazio de subagent é falha explícita

Após delegar via Task tool, o orquestrador MUST verificar que a sessão retornou ao menos uma message e ao menos uma part utilizável. Sessão ausente, erro de criação, `0 messages` ou `0 parts` MUST ser tratado como falha: a etapa delegada permanece incompleta e o handoff SHALL registrar erro explícito, identificador disponível e impacto. O fluxo MUST NOT interpretar resultado vazio como sucesso nem aplicar fallback silencioso.

#### Scenario: Spawn retorna zero messages
- **WHEN** uma Task session termina ou é retornada com `0 messages`
- **THEN** o handoff registra `ERROR: subagent spawn failed/empty` e a etapa não é marcada como concluída

#### Scenario: Spawn retorna zero parts
- **WHEN** uma Task session possui registro, mas nenhuma part utilizável
- **THEN** o resultado é erro explícito com impacto informado, mesmo que a chamada não tenha lançado exceção

#### Scenario: Spawn produz resultado utilizável
- **WHEN** a Task session retorna messages e parts não vazias
- **THEN** o orquestrador pode avaliar o conteúdo normalmente, sem inferir sucesso apenas pelo status da chamada
