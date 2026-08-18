## Why

O gate `Design` é o ponto de maior alavancagem do fluxo: decisões de spec, crítica e protótipo acontecem uma vez por card e, se fracas, multiplicam rework em Dev/QA/homologação. O modelo da sessão principal (`opencode-go/deepseek-v4-flash`) é adequado para volume, mas insuficiente para planejamento frontier. O GPT 5.6 Sol (`openai/gpt-5.6-sol`, conectado via OAuth OpenAI) pode coexistir com o Go sem trocar o default do dia a dia.

## What Changes

- Introduz o subagent obrigatório `design-planner` com `model: openai/gpt-5.6-sol` fixo e **effort sempre `high`**, capaz de executar o contrato `design-critic` no `Status=Design`. O rollout experimental foi promovido após o piloto real `UI impact: affected` do card #502 concluir com PASS.
- Documenta a segunda exceção explícita à herança de modelo (ao lado do `vision`): sessão principal e demais subagents continuam no modelo da sessão; `design-planner` usa GPT 5.6 Sol (high); pixels continuam no `vision`.
- Ajusta a regra de igualdade dos critics Impeccable (Assessment A/B): herdam o modelo da **sessão de design designada** (`design-planner` quando o gate roda por esse subagent; senão o da sessão principal). Sem igualdade observável → `BLOCKED`.
- Mantém Go e OpenAI autenticados em paralelo: default/volume no Go (`deepseek-v4-flash`); frontier só no gate Design via OpenAI (OAuth, billing direto).
- Fallback operacional `opencode-go/grok-4.5` (também effort `high`) somente com autorização de Alan se o GPT 5.6 Sol estiver indisponível.
- Sem mudança de UI de produto, APIs, banco ou runtime do app.

## Capabilities

### New Capabilities

- `design-planner-routing`: roteamento obrigatório do gate Design para o subagent `design-planner` (GPT 5.6 Sol, effort `high`), promovido após o piloto UI do card #502; mantém coexistência OpenAI/Go, fallback autorizado e restrição de escopo (só artefatos de design/protótipo). O card #496 foi absorvido pelo piloto já executado e cancelado sem implementação duplicada.

### Modified Capabilities

- `impeccable-design-gate`: Assessment A/B herdam o modelo da sessão de design designada (não necessariamente o da sessão principal) quando o gate roda via `design-planner`.

## Impact

- Arquivos: `.opencode/agent/design-planner.md`, `AGENTS.md`, `rules.md`, `.agents/skills/design-critic/SKILL.md`, `.opencode/agent/kaizen.md`, `docs/decision-log.md`.
- Sem impacto em frontend de produto, backend, banco ou services.
- Pré-requisito operacional: provider OpenAI autenticado (OAuth) para o ID `openai/gpt-5.6-sol` aparecer no `/models`.
- Card #491; branch `change-491-design-planner-grok`.
