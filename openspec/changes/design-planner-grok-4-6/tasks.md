## 1. Agent e config de modelo

- [x] 1.1 Criar `.opencode/agent/design-planner.md` com `model: opencode/grok-4.6`, effort `high` e escopo restrito a artefatos de design/protótipo
- [x] 1.2 Configurar variant/options `reasoningEffort: high` para `opencode/grok-4.6` no config do agent (sem cycle medium/xhigh)

## 2. Emendas normativas

- [x] 2.1 Atualizar `AGENTS.md` (Roteamento de LLM, Impeccable, lista de subagents) com a exceção `design-planner`
- [x] 2.2 Atualizar `rules.md` regras 4 e 9 (igualdade A/B = sessão de design; exceção de roteamento)
- [x] 2.3 Atualizar `.agents/skills/design-critic/SKILL.md` (Modelo e isolamento dos critics + critério de PASS)
- [x] 2.4 Atualizar `.opencode/agent/kaizen.md` (routing-drift: `vision` + `design-planner`)

## 3. Registro e validação

- [x] 3.1 Registrar decisão em `docs/decision-log.md` e plano em `.opencode/plans/design-gate-grok46.md`
- [ ] 3.2 Validar em sessão nova que o spawn do `design-planner` usa o modelo configurado + effort `high` (feito com grok-4.6; **revalidar com GPT 5.6 Sol após o rework**)
- [ ] 3.3 Piloto em 1 card `UI impact: affected` antes de tornar o roteamento obrigatório

## 4. Rework pós-Done (troca de modelo para GPT 5.6 Sol)

- [x] 4.1 Trocar `model: opencode/grok-4.6` por `model: openai/gpt-5.6-sol` no `.opencode/agent/design-planner.md` (effort `high` mantido)
- [x] 4.2 Atualizar OpenSpec (proposal/design/specs) e docs (AGENTS.md, rules.md, design-critic, decision-log) com GPT 5.6 Sol/OpenAI
