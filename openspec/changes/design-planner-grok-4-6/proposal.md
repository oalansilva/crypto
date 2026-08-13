## Why

O gate `Design` é o ponto de maior alavancagem do fluxo: decisões de spec, crítica e protótipo acontecem uma vez por card e, se fracas, multiplicam rework em Dev/QA/homologação. O modelo da sessão principal (`opencode-go/deepseek-v4-flash`) é adequado para volume, mas insuficiente para planejamento frontier. O grok 4.6 já está no catálogo Zen (`opencode/grok-4.6`) e pode coexistir com o Go sem trocar o default do dia a dia.

## What Changes

- Introduz o subagent `design-planner` com `model: opencode/grok-4.6` fixo e **effort sempre `high`**, executando o contrato `design-critic` no `Status=Design`.
- Documenta a segunda exceção explícita à herança de modelo (ao lado do `vision`): sessão principal e demais subagents continuam no modelo da sessão; `design-planner` usa grok 4.6; pixels continuam no `vision`.
- Ajusta a regra de igualdade dos critics Impeccable (Assessment A/B): herdam o modelo da **sessão de design designada** (`design-planner` quando o gate roda por esse subagent; senão o da sessão principal). Sem igualdade observável → `BLOCKED`.
- Mantém Go e Zen autenticados em paralelo: default/volume no Go (`deepseek-v4-flash`); frontier só no gate Design via Zen.
- Fallback operacional `opencode-go/grok-4.5` (também effort `high`) somente com autorização de Alan se o Zen estiver indisponível.
- Sem mudança de UI de produto, APIs, banco ou runtime do app.

## Capabilities

### New Capabilities

- `design-planner-routing`: roteamento do gate Design para o subagent `design-planner` (grok 4.6, effort `high`), coexistência Zen/Go, fallback autorizado e restrição de escopo (só artefatos de design/protótipo).

### Modified Capabilities

- `impeccable-design-gate`: Assessment A/B herdam o modelo da sessão de design designada (não necessariamente o da sessão principal) quando o gate roda via `design-planner`.

## Impact

- Arquivos: `.opencode/agent/design-planner.md`, `AGENTS.md`, `rules.md`, `.agents/skills/design-critic/SKILL.md`, `.opencode/agent/kaizen.md`, `docs/decision-log.md`.
- Sem impacto em frontend de produto, backend, banco ou services.
- Pré-requisito operacional: provider Zen autenticado (`/connect`) para o ID `opencode/grok-4.6` aparecer no `/models`.
- Card #491; branch `change-491-design-planner-grok`.
