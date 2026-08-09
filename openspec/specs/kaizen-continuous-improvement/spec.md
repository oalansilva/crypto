# kaizen-continuous-improvement Specification

## Purpose
Capacidade de melhoria contínua de processo do projeto: auditoria read-only de como o processo é executado (board, Git, OpenSpec, CI, tech debt e sessões do opencode), detecção de fricções e de sessões onde o modelo se perde ou alucina, registro de evidência local versionada e criação de cards kaizen no board com priorização visível.

## Requirements

### Requirement: Auditoria kaizen read-only disponível via command
O opencode SHALL expor o command `/kaizen` com modos de auditoria: `/kaizen` (completa), `/kaizen card <id>` (pós-card) e `/kaizen release` (pós-release), executando a coleta de evidências sem mutar arquivos, board, Git, PRs ou runtime.

#### Scenario: Auditoria completa executada
- **WHEN** o usuário invoca `/kaizen`
- **THEN** o subagent kaizen coleta evidências de board, Git, OpenSpec, CI e sessões do opencode
- **AND** o relatório é anexado em `docs/kaizen-log.md` sem alterações em código de produto

#### Scenario: Auditoria pós-release executada no fechamento de lote
- **WHEN** um lote/release é fechado (após deploy PROD validado, antes de mover cards para `Pronto`)
- **THEN** `/kaizen release` é executado com escopo de sessões dos cards do pacote
- **AND** a evidência da auditoria consta em `docs/kaizen-log.md`

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
Cada melhoria acionável da auditoria SHALL ser registrada como 1 issue separada no repo, em formato de proposta PO (`## Proposta (PO)` com Contexto, Escopo, Critérios de aceite), com label `kaizen`, `Status=Todo` no Project 1, campos preenchidos (`Prioridade` P0/P1/P2, `Tipo`, `Frente`, `Responsavel`, `Semana`) e dependências linkadas.

#### Scenario: Card criado como backlog
- **WHEN** o Kaizen registra uma melhoria
- **THEN** a issue é criada com label `kaizen` e `Status=Todo` no board
- **AND** o fluxo normal do board (Design, Aprovação de Design, ...) é seguido a partir daí

#### Scenario: Limite de 3 cards por release
- **WHEN** uma análise gera mais de 3 melhorias
- **THEN** apenas os 3 de maior prioridade entram como cards na release atual
- **AND** as demais permanecem no backlog kaizen para releases seguintes

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
