## ADDED Requirements

### Requirement: Gate Design disponibiliza design-planner com GPT 5.6 Sol
O repositório SHALL definir um subagent `design-planner` em `.opencode/agent/design-planner.md` com `model: openai/gpt-5.6-sol` fixo e effort `high` (`reasoningEffort: high`), para executar o contrato `design-critic` quando o card estiver em `Status=Design`. Até o card #496 concluir o piloto `UI impact: affected` com PASS e registrar a decisão de promoção, o roteamento SHALL permanecer experimental e MUST NOT ser obrigatório globalmente.

#### Scenario: Subagent disponível no gate Design
- **WHEN** um card está em `Status=Design` e o provider OpenAI está autenticado
- **THEN** uma sessão principal nova na worktree que contém o agent MAY delegar o contrato design-critic via ferramenta `Task` ao subagent `design-planner`, no mesmo padrão do `vision`
- **AND** o request SHALL rodar com modelo `openai/gpt-5.6-sol` e effort `high`

#### Scenario: Rollout obrigatório aguarda piloto UI
- **WHEN** o card #496 ainda não concluiu o piloto `UI impact: affected` com PASS e decisão de promoção registrada
- **THEN** o uso do `design-planner` MUST permanecer experimental
- **AND** cards `UI impact: none` MAY ser usados como smoke sem promover o roteamento a regra global obrigatória

#### Scenario: Subagent não pode ser iniciado como agente primário
- **WHEN** o operador tenta usar `opencode run --agent design-planner`
- **THEN** o fluxo MUST rejeitar essa forma de invocação porque `design-planner` usa `mode: subagent`
- **AND** qualquer fallback para o agente/modelo default MUST invalidar o gate de Design

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

### Requirement: Coexistência OpenAI e Go
O cliente SHALL manter os providers OpenAI (`openai/`) e Go (`opencode-go/`) autenticados em paralelo. A sessão principal e o `vision` SHALL permanecer no Go; o frontier do gate Design SHALL usar OpenAI.

#### Scenario: Conectar OpenAI não remove o Go
- **WHEN** o operador conecta o provider OpenAI (OAuth)
- **THEN** a key do `opencode-go` MUST permanecer
- **AND** o default da sessão principal MUST continuar `opencode-go/deepseek-v4-flash`

### Requirement: Fallback autorizado quando o modelo frontier está indisponível
Se `openai/gpt-5.6-sol` estiver indisponível, o `design-planner` SHALL emitir `BLOCKED (modelo indisponível)` e MUST NOT cair automaticamente para outro modelo. Fallback para `opencode-go/grok-4.5` com effort `high` SHALL ocorrer somente com autorização explícita de Alan.

#### Scenario: OpenAI sem credencial ou falha
- **WHEN** o provider OpenAI não está autenticado ou a chamada a `openai/gpt-5.6-sol` falha
- **THEN** o veredito de Design SHALL ser `BLOCKED (modelo indisponível)`
- **AND** nenhum fallback silencioso MAY ser usado
