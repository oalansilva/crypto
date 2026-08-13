## Context

Card #491. Branch `change-491-design-planner-grok`. Change `design-planner-grok-4-6`.

Hoje a sessão principal e todos os subagents herdam `opencode-go/deepseek-v4-flash`, com uma única exceção documentada: `vision` (`opencode-go/qwen3.7-plus`). O gate Design (specs, crítica, protótipo) é judgment-heavy e acontece uma vez por card. grok 4.6 existe no Zen (`opencode/grok-4.6`, effort `low|medium|high|xhigh`) e não existe no Go. Zen e Go coexistem no mesmo cliente: `/connect` Zen adiciona key sem remover a do Go. Sem key Zen, o `/models` esconde os pagos do Zen.

**UI impact: none.** Mudança de processo/tooling (agent, regras, skills). Nenhuma tela, rota, componente ou token do produto muda.

## Goals / Non-Goals

**Goals:**
- Rodar o contrato `design-critic` no `Status=Design` via subagent `design-planner` com grok 4.6 e effort **sempre `high`**.
- Documentar a segunda exceção de roteamento sem enfraquecer o gate (Design → Aprovação de Design → Pronto para Dev continua obrigatório).
- Critics A/B herdam o modelo da sessão de design designada, com igualdade observável.
- Manter pixels no `vision` e volume diário no Go/flash.
- Envelope de custo: grok só no spawn isolado do planner, nunca na sessão principal.

**Non-Goals:**
- Não trocar o modelo default da sessão principal.
- Não usar grok em Code Review, QA, Kaizen ou implementação (fora do escopo deste card).
- Não criar superfície visual de produto nem protótipo HTML.
- Não autoaprovar Design.

## Decisions

1. **Subagent fixo, nunca sessão principal.** Molde do `vision`. A sessão principal permanece no Go/flash e só delega um packet compacto. Evidência 2026-08-13: esta sessão de exploração (`Onde incluir Grok 4.6 no fluxo`) rodou `opencode/grok-4.6` variant `medium` como **sessão principal** e gastou ~$3,03–$3,30 (589k input, 8,5M cache_read). Isso **não** é o custo do gate Design — é o custo de orquestração/board/OpenSpec no frontier. Alternativa rejeitada: `/model grok` na sessão inteira.

2. **ID `openai/gpt-5.6-sol` (OpenAI via OAuth), effort `high` fixo.** Alan escolheu GPT Sol High e conectou o provider OpenAI; billing direto (sem Zen). Configurar `reasoningEffort: high` no agent; sem cycle operacional. Fallback `opencode-go/grok-4.5` + `high` só com autorização de Alan. Histórico: a primeira versão deste card usava `opencode/grok-4.6` (Zen); Alan trocou para GPT 5.6 Sol após o Done (rework mantém o status, regra de não regressão).

3. **Igualdade A/B = sessão de design designada.** Quando o pipeline Impeccable roda dentro do `design-planner`, A e B herdam GPT 5.6 Sol (modelo dessa sessão). Sem igualdade observável → `BLOCKED`. Alternativa rejeitada: A/B no flash enquanto o planner usa o frontier — perde o frontier na crítica.

4. **Escopo de escrita do planner:** só `openspec/changes/<change>/design.md` (e seções Impeccable), `frontend/public/prototypes/<slug>/` e espelho `openspec/changes/<change>/prototype/` quando UI. Proibido código de produção. Pixels → `vision`.

5. **Piloto obrigatório** em 1 card `UI impact: affected` depois da implementação, antes de tornar o roteamento obrigatório em todo card.

6. **Spawn isolado do planner.** O spawn do `design-planner` recebe packet fechado (proposal + `design.md` atual + contextFiles da change + trecho relevante de `DESIGN.md`). Proibido: AGENTS.md/rules.md inteiros, loops de `gh`/board, `openspec ff`, testes, restart. Flash faz OpenSpec/board/publicação. **Sem teto de custo por card** (decisão de Alan) — o isolamento é estrutural (frontier nunca como sessão principal), não financeiro. Effort `high` permanece, mas só nesse spawn curto.

## Risks / Trade-offs

- [OpenAI sem key/OAuth] → `BLOCKED (modelo indisponível)`; fallback só com autorização de Alan.
- [GPT 5.6 Sol é caro ($5/$30)] → spawn isolado e curto; custo acompanhado no uso (sem teto por card).
- [Custo: sessão principal no frontier queima cache (evidência grok 4.6: 8,5M read ≈ $3+)] → regra: frontier só no spawn isolado; flash orquestra.
- [Custo: effort `high` + packet grande] → packet compacto; custo observado no uso (sem teto por card).
- [Sessões em voo não pegam o modelo novo] → validar em sessão nova após merge (regra de troca de modelo).
- [Confusão de providers no `/models`] → documentar Zen vs Go no AGENTS.md.

## Migration Plan

1. Alan conecta OpenAI (OAuth) e confirma `openai/gpt-5.6-sol` no `/models`.
2. Implementar agent + emendas normativas na branch do card após `Pronto para Dev`.
3. Validar em sessão nova; piloto em 1 card UI.
4. Rollback: remover o agent e reverter as emendas; o fluxo volta a herdar só a sessão principal + `vision`.

## Open Questions

Nenhuma. Effort `high` e modelo GPT 5.6 Sol (OpenAI) já decididos por Alan.

## Prototype

N/A. Card de processo/tooling: nenhuma superfície visual de produto é criada, alterada ou removida. Não há protótipo HTML.

## Prototype Validation

N/A. Sem protótipo para abrir em navegador.

## Impeccable Brief

N/A. `UI impact: none` — sem superfície visual. Justificativa: o card altera agent/regras/skills, não UI do app.

## Impeccable Critique

N/A. Mesma justificativa.

## Impeccable Audit

N/A. Mesma justificativa.

## Impeccable Trace

N/A. Mesma justificativa.

## Design Critique

Dimensões cobertas (sem UI): escopo, regressão de produto, riscos operacionais, confirmação de ausência de superfície visual.

### Achados

- **Escopo:** fechado no gate Design + exceção de roteamento. Não vaza para implementação/QA. Sem P0/P1.
- **Regressão de produto:** nenhuma tela/API/banco muda. Risco residual: agente futuro editar código de produção no planner — mitigado por regra explícita no prompt e review do diff.
- **Operacional:** dependência do provider OpenAI autenticado. Sem credencial o planner não pode ser obrigatório. Mitigação: pré-requisito no card + `BLOCKED` + fallback autorizado.
- **Superfície visual:** confirmado `none`. Prototype N/A justificado. Impeccable N/A justificado.
- **Igualdade A/B neste card:** Impeccable N/A (sem UI); crítica feita na sessão principal. Sem necessidade de spawn A/B.

### Riscos não bloqueantes

- Custo de `high` no piloto pode surpreender; aceitável e observável no usage da OpenAI.
- Documentação precisa deixar claro que `/models` exige o provider OpenAI conectado para listar `openai/gpt-5.6-sol` (já no proposal).

### Referências

- Card: #491
- Change: `design-planner-grok-4-6`
- Prototype: N/A (processo/tooling)

Design Agent verdict: PASS
