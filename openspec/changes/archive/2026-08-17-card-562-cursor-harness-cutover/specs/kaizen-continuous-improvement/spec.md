## MODIFIED Requirements

### Requirement: Auditoria kaizen read-only disponível via command
O Cursor SHALL expor o command `/kaizen` com modos `/kaizen`, `/kaizen card <id>` e `/kaizen release`, coletando evidências sem mutar arquivos de produto, board, Git, PRs ou runtime.

#### Scenario: Auditoria completa executada
- **WHEN** o usuário invoca `/kaizen`
- **THEN** a auditoria coleta evidências de board, Git, OpenSpec, CI e sessões Cursor
- **AND** o relatório é anexado em `docs/kaizen-log.md` sem alterações em código de produto

#### Scenario: Auditoria pós-release executada no fechamento de lote
- **WHEN** um lote/release é fechado (após deploy PROD validado, antes de mover cards para `Pronto`)
- **THEN** `/kaizen release` é executado com escopo de sessões dos cards do pacote
- **AND** a evidência consta em `docs/kaizen-log.md`

### Requirement: Análise de sessões Cursor com escopo da release
A auditoria SHALL ler transcripts Cursor do projeto (diretório de agent-transcripts da worktree) em modo read-only, correlacionando sessões com cards do pacote (`#<id>` / `card-<id>`). MUST NOT exigir `~/.local/share/opencode/opencode.db` como fonte ativa.

#### Scenario: Sessões correlacionadas e sinais reportados
- **WHEN** a auditoria analisa as sessões da release
- **THEN** reporta sinais de modelo perdido/alucinando (path/URL inventado, loop, custo alto sem `Done`, TODO eterno) e custo/eficácia por card quando o transcript expuser esses dados
- **AND** nenhum dado privado vai para issues públicas — trechos curtos só em `docs/kaizen-log.md`

#### Scenario: Fonte indisponível declarada
- **WHEN** transcripts Cursor ou `gh` não estão acessíveis
- **THEN** a limitação é declarada no relatório em vez de audit vazio
