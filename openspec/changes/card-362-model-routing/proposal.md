## Why

O fluxo atual define responsabilidades e gates por etapa, mas não fixa de forma automática e auditável qual modelo executa Design/OpenSpec, desenvolvimento, Code Review, QA e release. A padronização elimina escolha manual, fallback silencioso e variação de qualidade entre cards.

## What Changes

- Manter a sessão principal em GPT-5.6 Sol com esforço High para conduzir Design/OpenSpec e reassumir a aceitação técnica em QA.
- Delegar toda implementação em `Em desenvolvimento` a um perfil project-scoped GPT-5.6 Luna com esforço Max.
- Delegar todo `Code Review` a uma nova thread GPT-5.6 Luna Max, independente da implementação e configurada como read-only.
- Delegar toda release explicitamente solicitada a uma nova thread GPT-5.6 Luna Max dedicada à operação, sem autorização para alterar código.
- Tornar o roteamento obrigatório por estágio, sem decisão por complexidade, sem uso de Terra e sem fallback para outro perfil/modelo/esforço.
- Bloquear a etapa quando o perfil esperado estiver ausente, divergente ou não observável.
- Validar a instalação inicial dos perfis por configuração e testes reproduzíveis; coletar evidência runtime somente quando cada lane for usada naturalmente após a ativação, sem smoke-spawn antecipado.
- Preservar integralmente os gates humanos, o ciclo de retorno `Em desenvolvimento -> Code Review -> QA` e os critérios automatizados de QA/release.
- Alinhar as instruções globais e locais, os perfis de agentes Codex, a skill de orquestração e a documentação operacional do Project.

## Capabilities

### New Capabilities

- `stage-model-routing`: Roteamento automático, fixo e fail-closed de Sol High e Luna Max conforme o estágio operacional do card.

### Modified Capabilities

- `multiagent-operating-standard`: Fixar os agentes/modelos responsáveis por cada etapa sem alterar o Kanban canônico nem as aprovações humanas.
- `delivery-qa-stage`: Exigir que QA seja conduzido pelo Sol High sobre o SHA revisado e as evidências automatizadas.
- `agent-instruction-alignment`: Manter instruções globais, locais e perfis project-scoped coerentes com o roteamento obrigatório.

## Impact

- `AGENTS.md`, `rules.md` e documentação operacional do Project 1.
- Skill global `alan-workflow`, por change coordenada em seu repositório de origem, e skill project-scoped Codex de orquestração.
- Perfis em `.codex/agents/` e configuração multiagente em `.codex/config.toml` quando necessária.
- Contratos de desenvolvimento, Code Review, QA e release; sem alteração de API, banco, frontend ou comportamento funcional do produto.
- Instalações do Codex precisam recarregar os perfis em uma nova tarefa após a atualização.
- A ativação não exige nem autoriza alteração de AppArmor, sysctl, sandbox do host ou outra configuração do servidor.
- Cursor e outros clientes não fazem parte da implementação nem da validação desta change.
