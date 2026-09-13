# kaizen-continuous-improvement Specification

## Purpose
Capacidade de melhoria contínua de processo do projeto: auditoria read-only de como o processo é executado (board, Git, OpenSpec, CI, tech debt e sessões do opencode), detecção de fricções e de sessões onde o modelo se perde ou alucina, registro de evidência local versionada e criação de cards kaizen no board com priorização visível.
## Requirements
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

### Requirement: Análise de sessões do opencode com escopo da release
A auditoria SHALL consultar o banco de sessões do opencode (`~/.local/share/opencode/opencode.db`) em modo read-only, correlacionando as sessões com os cards do pacote (`#<id>`/`card-<id>` no título ou mensagens de usuário, diretório do projeto, janela entre a release anterior e a atual), incluindo sessões de subagentes via `parent_id`.

#### Scenario: Sessões correlacionadas e sinais reportados
- **WHEN** a auditoria analisa as sessões da release
- **THEN** ela reporta sinais de modelo perdido/alucinando (caminho/URL inventado, loop sem progresso, `step-finish unknown`, custo alto sem `Done`, deriva de roteamento de modelo, subagent falhando, TODO eterno) e custo/eficácia por card
- **AND** nenhum dado privado (prompts, raciocínio íntegro, tokens, credenciais) é incluído em issues públicas — trechos curtos apenas em `docs/kaizen-log.md`

#### Scenario: Fonte indisponível declarada
- **WHEN** uma fonte de evidência não está acessível (sem gh auth, DB ausente)
- **THEN** a limitação é declarada no relatório em vez de audit vazio

### Requirement: Registro de melhorias como cards PO no board
Cada melhoria acionável da auditoria SHALL ser registrada como 1 issue separada no repo, em formato de proposta PO (`## Proposta (PO)` com Contexto, Escopo, Critérios de aceite), com label `kaizen`, `Status=Em Refinamento` no Project 1, campos preenchidos (`Prioridade` P0/P1/P2, `Tipo`, `Frente`, `Responsavel`, `Semana`) e dependências linkadas.

#### Scenario: Card criado como entrada
- **WHEN** o Kaizen (via orquestrador de closeout) registra uma melhoria
- **THEN** a issue é criada com label `kaizen` e `Status=Em Refinamento` no board
- **AND** o fluxo normal do board (`Em Refinamento` → `Todo` → Design → …) é seguido a partir daí

#### Scenario: Limite de 3 cards por release
- **WHEN** uma análise gera mais de 3 melhorias
- **THEN** apenas os 3 de maior prioridade entram como cards na release atual
- **AND** as demais permanecem no backlog kaizen para releases seguintes

### Requirement: Evidência de materialização Kaizen no fechamento de release

Antes de concluir o `release-guard post`, a entrada canônica de `/kaizen release` em `docs/kaizen-log.md` para a data da release MUST evidenciar materialização de melhorias acionáveis: (a) 1 a 3 issues novas listadas na tabela cujo heading `###` **começa com** `Cards kaizen criados` (sufixo livre) sob o(s) heading(s) `## YYYY-MM-DD — Kaizen release`, ou (b) linhas `(não criado)` com `coberto por` seguido de um ou mais `#N` (todos em fluxo no Project 1: Status presente e não `Pronto`/`Cancelado`), ou (c) marcador explícito `Sem achados acionáveis` quando não houver linhas de dados na união das tabelas. Qualquer linha de dados inválida MUST falhar o check mesmo se houver cards criados ou marcador. A auditoria da skill `kaizen` permanece read-only; a criação de issues é responsabilidade do orquestrador de closeout e o guard apenas valida.

#### Scenario: Post bloqueia sem cards nem dedupe válido
- **WHEN** o `post` encontra heading Kaizen da data mas a união das tabelas não tem issues novas nem dedupe válido nem marcador sem achados acionáveis
- **THEN** o guard emite blocker e não autoriza promover o pacote a `Pronto`

#### Scenario: Post passa com cards listados
- **WHEN** a união das tabelas lista entre 1 e 3 issues `#N` criadas, sem linhas inválidas, e qualquer dedupe extra tem todas as coberturas em fluxo
- **THEN** o check de materialização Kaizen passa

#### Scenario: Post passa com zero cards e dedupe em fluxo
- **WHEN** não há issues novas e cada linha `(não criado)` cita `coberto por` com um ou mais `#N` em Status de fluxo
- **THEN** o check de materialização Kaizen passa

#### Scenario: Post passa com marcador sem achados acionáveis
- **WHEN** não há linhas de dados na(s) tabela(s) e o corpo contém `Sem achados acionáveis`
- **THEN** o check de materialização Kaizen passa

#### Scenario: Dedupe com cobertura Pronto ou Cancelado falha
- **WHEN** cobertura `#N` está `Pronto` ou `Cancelado` (ou ausente)
- **THEN** o guard emite blocker

#### Scenario: Mais de 3 cards na data falha
- **WHEN** a união das tabelas lista mais de 3 issues distintas criadas
- **THEN** o guard emite blocker

#### Scenario: Linha inválida falha mesmo com cards criados
- **WHEN** há 1–3 `#N` criados e também uma linha `(não criado)` sem `coberto por #N`
- **THEN** o guard emite blocker

#### Scenario: Marcador não salva linhas inválidas
- **WHEN** existe `Sem achados acionáveis` e também há linha de dados inválida na tabela
- **THEN** o guard emite blocker

#### Scenario: Board indisponível com dedupe falha fechado
- **WHEN** há dedupe e o snapshot do Project 1 está indisponível
- **THEN** o guard emite blocker fail-closed

### Requirement: Priorização visível com override humano
O campo `Prioridade` (P0/P1/P2) SHALL ser preenchido na criação do card pela regra severidade × frequência / esforço: P0 = risco de segurança/dados/produção ou falha recorrente bloqueante ou alucinação cara → semana atual; P1 = quick win/higiene → próxima semana; P2 = desejável → backlog. O override humano deve ser sempre possível.

#### Scenario: Prioridade calculada na criação
- **WHEN** o card kaizen é criado
- **THEN** o campo `Prioridade` é preenchido conforme a regra, com o achado de origem e o link para `docs/kaizen-log.md` no corpo da issue

#### Scenario: Reclassificação por Alan
- **WHEN** Alan reclassifica a prioridade de um card kaizen
- **THEN** o novo valor prevalece sobre a regra padrão

### Requirement: Evolução de skills com pesquisa e aprovação
O Kaizen SHALL poder propor melhorias nas skills em uso e pesquisar skills alternativas (busca read-only em GitHub/docs/CLIs, comparação de fit com evidência) quando a atual não atender. Toda troca ou criação de skill SHALL depender de aprovação explícita de Alan e respeitar a herança de modelo/roteamento do projeto.

#### Scenario: Proposta de skill com evidência
- **WHEN** o Kaizen identifica skill insuficiente ou propõe alternativa
- **THEN** a proposta registra comparação com evidência no card
- **AND** a mudança só é aplicada após aprovação de Alan

#### Scenario: Segurança de output
- **WHEN** o Kaizen reporta achados em issues públicas
- **THEN** apenas métricas agregadas e IDs são publicados; trechos de sessão ficam somente em `docs/kaizen-log.md`

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

### Requirement: Kaizen reads issue surface over REST and Status pontual
The kaizen skill SHALL read issue body, comments, and labels over REST (`gh api repos/<owner>/<repo>/issues/<n>` and REST comments). It MUST NOT call `gh issue view` (with or without `--json`) for those fields. Status of a single card N on Project 1 MUST be a pontual GraphQL query of that card. `/kaizen card N` MUST NOT list the whole board (`gh project item-list`) to operate that card. A full-board `/kaizen` photograph, when the task is the whole board, remains at most one listing per run and MUST NOT retry on RATE_LIMIT. When GraphQL remaining is 0 or the body is RATE_LIMIT (including HTTP 200), kaizen MUST fail immediately with the reset time from GraphQL headers; MUST NOT wait for reset in the same command; MUST NOT treat unknown Status as the card off the board. REST remaining=5000 MUST NOT authorize GraphQL. Audit remains read-only on product code.

#### Scenario: kaizen card N does not item-list the board
- **WHEN** `/kaizen card N` needs Status of issue N
- **THEN** it uses a pontual issue→Status query
- **AND** MUST NOT call `gh project item-list` for that card

#### Scenario: Issue evidence stays on REST
- **WHEN** kaizen reads body or comments of issue N
- **THEN** it uses REST
- **AND** MUST NOT use `gh issue view --json`

#### Scenario: GraphQL quota 0 fails immediately
- **WHEN** GraphQL headers remaining=0 during a board Status read
- **THEN** kaizen fails immediately with the reset time
- **AND** MUST NOT retry GraphQL in a loop
- **AND** MUST NOT wait for reset in the same command

