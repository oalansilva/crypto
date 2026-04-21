# Coordination — Card #77: Auto-Retrospective após cada Feature

## Status

| Stage | Owner | Status | Data |
|-------|-------|--------|------|
| PO | PO Agent | ✅ done (revisado com novo entendimento) | 2026-04-03 14:47 |
| DESIGN | DESIGN Agent | ✅ done (subagent review: ajustes mínimos) | 2026-04-03 15:05 |
| DEV | — | pending | — |
| QA | — | pending | — |
| Homologation (Alan) | — | pending | — |

## Card Type
`process` — este é um card de melhoria de processo/workflow, não uma feature de produto.

## Change ID
`auto-retrospective`

## Card
`#77`

## Links

- **Proposal:** `/root/.openclaw/workspace/crypto/openspec/changes/auto-retrospective/proposal.md`
- **Review PT-BR:** `/root/.openclaw/workspace/crypto/openspec/changes/auto-retrospective/review-ptbr.md`
- **Tasks:** `/root/.openclaw/workspace/crypto/openspec/changes/auto-retrospective/tasks.md`
- **Design:** `/root/.openclaw/workspace/crypto/openspec/changes/auto-retrospective/design.md`

---

## Novo Entendimento (Alan — 2026-04-03 14:46)

**Objetivo da Feature:** A retrospectiva não é só um relatório — é um **feedback loop para o ORQUESTRADOR (eu)** ler e implementar melhorias no workflow do time.

Após cada feature ser homologada:
1. Sistema gera auto-retrospective automaticamente
2. **Eu (orquestrador) leio a retrospectiva** e identifico pontos de melhoria no processo
3. **Eu implemento as melhorias** no workflow do time

Ou seja: **Build → Homologa → Retro → Improve → Repete**

O PO deve revisar o design com esse novo entendimento — o foco é que a retrospectiva seja **acionável por mim** para melhorar o fluxo.

---

## Decisions

### Decisão 1: Trigger
**Decisão:** O trigger de retrospective será no endpoint de homologação do **orchestrator** (não no Kanban API plugin).
**Rationale:** Mais controlável, não depende de plugin externo, já existe lógica de handoff no orchestrator.
**Status:** ✅ Definido

### Decisão 2: Engine de Insights LLM
**Decisão:** Usar **`acpx codex`** para geração de insights textuais.
**Rationale:** Já está no fluxo, não requer API externa, custo zero.
**Status:** ✅ Definido

### Decisão 3: Visibilidade
**Decisão:** Implementar **endpoint + arquivo Markdown primeiro**. Interface Kanban é future work.
**Rationale:** Escopo mínimo viável. Interface pode ser adicionada sem mudar o core.
**Status:** ✅ Definido

### Decisão 4: Retroativo
**Decisão:** **Não** gerar retrospectivas retroativas para features passadas.
**Rationale:** Custo-benefício baixo. Focar em gerar retrospectivas a partir da data de implementação desta feature.
**Status:** ✅ Definido

### Decisão 5: Execução
**Decisão:** Execução **assíncrona** (background job) — não bloqueia homologação.
**Rationale:** Não adicionar latência no fluxo principal.
**Status:** ✅ Definido

---

## blockers

Nenhum blocker no momento.

---

## Próximo Passo

**Owner:** PO Agent
**Ação:** Revisar proposal/design com novo entendimento — a retrospectiva deve ser acionável pelo orquestrador para melhorar o workflow.
