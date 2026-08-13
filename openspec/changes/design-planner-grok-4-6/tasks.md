## 1. Agent e config de modelo

- [x] 1.1 Criar `.opencode/agent/design-planner.md` com modelo frontier fixo, effort `high` e escopo restrito a artefatos de design/protótipo (modelo final: `openai/gpt-5.6-sol`; histórico grok 4.6 preservado no design)
- [x] 1.2 Configurar `reasoningEffort: high` no agent e confirmar no config resolvido por `opencode debug agent design-planner`

## 2. Emendas normativas

- [x] 2.1 Atualizar `AGENTS.md` (Roteamento de LLM, Impeccable, lista de subagents) com a exceção `design-planner`
- [x] 2.2 Atualizar `rules.md` regras 4 e 9 (igualdade A/B = sessão de design; exceção de roteamento)
- [x] 2.3 Atualizar `.agents/skills/design-critic/SKILL.md` (Modelo e isolamento dos critics + critério de PASS)
- [x] 2.4 Atualizar `.opencode/agent/kaizen.md` (routing-drift: `vision` + `design-planner`)

## 3. Registro e validação

- [x] 3.1 Registrar decisão em `docs/decision-log.md` e plano em `.opencode/plans/design-gate-grok46.md`
- [x] 3.2 Validar em sessão nova o spawn via `Task`: parent Go/flash; child runtime `agent=design-planner`, `model=openai/gpt-5.6-sol`; config resolvido `options.reasoningEffort=high` (2026-08-13)
- [x] 3.3 Transferir o piloto `UI impact: affected` para o card filho #496, criado em `Em Refinamento`; #491 conclui o smoke e mantém o rollout experimental até #496 validar a promoção

## 4. Rework pós-Done (troca de modelo para GPT 5.6 Sol)

- [x] 4.1 Trocar `model: opencode/grok-4.6` por `model: openai/gpt-5.6-sol` no `.opencode/agent/design-planner.md` (effort `high` mantido)
- [x] 4.2 Atualizar OpenSpec (proposal/design/specs) e docs (AGENTS.md, rules.md, design-critic, decision-log) com GPT 5.6 Sol/OpenAI
- [x] 4.3 Alinhar invocação ao padrão do `vision`: sessão principal delega via `Task`; proibir `opencode run --agent design-planner` e fallback para o agente default
