# Proposal — Card #77: Auto-Retrospective após cada Feature

## Feature Overview

**Card:** #77
**Título:** Auto-Retrospective após cada Feature
**Change ID:** `auto-retrospective`
**Stage:** PO (Product Owner)
**Status:** Em elaboração

---

## Motivation

Após cada feature ser concluída e homologada, o processo atual não gera nenhum registro sistemático de lições aprendidas. Isso faz com que:

- Erros de processo se repitam em features futuras sem correção
- O orquestrador (Alan) não tenha visibilidade objetiva de onde o fluxo travou ou慢了
- A melhoria contínua dependa exclusivamente de memória individual
- Decisões de ajuste de workflow sejam tomadas sem dados reais

A **Auto-Retrospective** existe para que **Alan (orquestrador)** tenha um feedback loop concreto após cada feature homologada. Não é um relatório para arquivo — é um **input direto para melhorar o workflow do time**. O ciclo é:

```
Build → Homologa → Retro (gera) → Alan lê → Alan implementa melhoria no fluxo
```

---

## Feature Description

Após cada feature ser marcada como **homologada** no Kanban, o sistema executa automaticamente uma retrospectiva com foco em **insights acionáveis pelo orquestrador**:

1. **Coleta de dados contextuais:**
   - Tempo total entre início (primeiro commit) e homologação
   - Tempo gasto em cada stage (PO, DESIGN, DEV, QA)
   - Quantidade de ciclos de revisão/feedback por stage
   - Quantidade de bugs/tarefas abertas durante a implementação
   - Presença de blockers e tempo em blockers

2. **Análise automática:**
   - Identifica se o tempo por stage está dentro do esperado
   - Detecta sinais de risco (muitos ciclos de revisão, blockers longos)
   - Classifica a feature como: `sem problemas`, `com ressalvas`, `problemática`

3. **Geração de insights acionáveis pelo orquestrador:**
   - **O que falhou no processo?** (e não apenas na feature)
   - **Onde o fluxo travou?** (stage específico, tipo de blocker)
   - **O que melhorou em relação à feature anterior?**
   - **Recomendação concreta para o orquestrador:** (ex: "PO review precisa de deadline", "QA precisa de mais contexto antes", "Design tem gargalo em approvals")

4. **Armazenamento:**
   - Registra o relatório de retrospectiva no card/feature
   - Mantém histórico consultável em `/root/.openclaw/workspace/crypto/docs/retrospectives/`
   - **O relatório é lido pelo orquestrador — nunca é só arquivo morto**

**Nota:** O público-alvo da retrospectiva é o **orquestrador (Alan)**, não o time. O objetivo não é documentar para a equipe, mas dar ao orquestrador dados para melhorar o processo.

---

## Scope

### In Scope
- Trigger automático ao marcar feature como `homologada`
- Coleta automática de dados de tempo e ciclos via runtime/Kanban API
- Análise e classificação automática (sem problemas / com ressalvas / problemática)
- Geração de insights textuais via LLM (acpx codex ou API de IA)
- Persistência do relatório em arquivo markdown
- Exposição do relatório via endpoint ou consulta

### Out of Scope
- Integração com ferramentas externas (Jira, Linear, etc.)
- Retrospectiva manual colaborativa (sprint retrospective meeting)
- Métricas de código (sonarqube, coverage) — future work
- Alertas ou notificações em tempo real

---

## Technical Approach

1. **Trigger:** Hook no endpoint de update de stage do Kanban — ao mudar para `homologation` ou ao marcar `homologada`, dispara o pipeline de retrospective
2. **Coleta de dados:** Query na API de runtime/tasks e Kanban para extrair tempos e ciclos
3. **Análise:** Usa `acpx codex` ou API de IA para gerar insights estruturados a partir dos dados coletados
4. **Persistência:** Grava `.md` em `/root/.openclaw/workspace/crypto/docs/retrospectives/YYYY-MM-DD-{feature-slug}.md`
5. **API/Consulta:** Adiciona endpoint `GET /retrospectives/{feature-slug}` para consulta

---

## OpenSpec Artifacts

- `proposal.md` — este documento
- `review-ptbr.md` — review em português do Brasil
- `tasks.md` — tasks técnicas

---

## Dependencies

- Card #77 é auto-referente: a própria feature de auto-retrospective vai gerar sua própria retrospectiva quando homologada (meta!)
- Depende de: runtime/tasks API, Kanban API, `acpx codex` (para geração de insights)
- Não bloqueia nenhuma outra feature

---

## Open Questions

1. ~~O trigger deve ser no endpoint de homologation do orchestrator ou no Kanban API?~~ → ✅ já decidido: orchestrator
2. ~~Insights textuais devem ser gerados por LLM local (`acpx codex`) ou API externa?~~ → ✅ já decidido: acpx codex
3. ~~O relatório deve ser visível na interface do Kanban ou apenas em arquivo + endpoint?~~ → ✅ já decidido: endpoint + arquivo primeiro
4. ~~Features passadas devem ter retrospectiva gerada retroativamente?~~ → ✅ já decidido: não
5. **NOVO:** O orquestrador deve receber notificação (Telegram/chat) quando uma retrospective é gerada, ou basta verificar manualmente?

---

## Impacto Esperado

- **Positivo:** Alan tem dados concretos para justificar e implementar melhorias no workflow. Cada retrospectiva é um input direto para o próximo ciclo de melhoria.
- **Risco:** LLM gerando insights genéricos que não ajudam o orquestrador a agir
- **Mitigação:** O prompt do LLM deve ser explicitly focado em "processo" e "orquestrador", não em "lições aprendidas genéricas"

---

## Priority

**Alta** — Feature de suporte ao processo de melhoria contínua. Afeta todas as features futuras.
