## ADDED Requirements

### Requirement: Gate Design usa design-planner com grok 4.6
O repositório SHALL definir um subagent `design-planner` em `.opencode/agent/design-planner.md` com `model: opencode/grok-4.6` fixo e effort `high` (`reasoningEffort: high`), para executar o contrato `design-critic` quando o card estiver em `Status=Design`.

#### Scenario: Subagent disponível no gate Design
- **WHEN** um card está em `Status=Design` e o provider Zen está autenticado
- **THEN** a sessão principal SHALL delegar o contrato design-critic ao subagent `design-planner`
- **AND** o request SHALL rodar com modelo `opencode/grok-4.6` e effort `high`

#### Scenario: Effort não pode variar
- **WHEN** o `design-planner` é invocado
- **THEN** o effort SHALL ser `high`
- **AND** o agente MUST NOT ciclar para `medium` ou `xhigh` no fluxo operacional

### Requirement: Escopo de escrita do design-planner
O `design-planner` SHALL editar somente artefatos de design e protótipo da change; MUST NOT editar código de produção.

#### Scenario: Artefatos permitidos
- **WHEN** o `design-planner` produz a entrega de Design
- **THEN** ele MAY escrever `openspec/changes/<change>/design.md`, `frontend/public/prototypes/<slug>/` e o espelho `openspec/changes/<change>/prototype/` quando houver UI
- **AND** ele MUST NOT alterar backend, frontend de produto, migrations ou services

### Requirement: Pixels permanecem no vision
Qualquer julgamento de pixels no gate Design SHALL continuar delegado ao subagent `vision` (`opencode-go/qwen3.7-plus`).

#### Scenario: Screenshot no pipeline de design
- **WHEN** o `design-planner` precisa julgar screenshot, diff ou fidelidade visual
- **THEN** ele SHALL delegar ao `vision`
- **AND** MUST NOT interpretar pixels

### Requirement: Coexistência Zen e Go
O cliente SHALL manter os providers Zen (`opencode/`) e Go (`opencode-go/`) autenticados em paralelo. A sessão principal e o `vision` SHALL permanecer no Go; o frontier do gate Design SHALL usar Zen.

#### Scenario: Conectar Zen não remove o Go
- **WHEN** o operador executa `/connect` no OpenCode Zen
- **THEN** a key do `opencode-go` MUST permanecer
- **AND** o default da sessão principal MUST continuar `opencode-go/deepseek-v4-flash`

### Requirement: Fallback autorizado quando Zen indisponível
Se `opencode/grok-4.6` estiver indisponível, o `design-planner` SHALL emitir `BLOCKED (modelo indisponível)` e MUST NOT cair automaticamente para outro modelo. Fallback para `opencode-go/grok-4.5` com effort `high` SHALL ocorrer somente com autorização explícita de Alan.

#### Scenario: Zen sem credencial ou saldo
- **WHEN** o provider Zen não está autenticado ou a chamada a `opencode/grok-4.6` falha
- **THEN** o veredito de Design SHALL ser `BLOCKED (modelo indisponível)`
- **AND** nenhum fallback silencioso MAY ser usado
