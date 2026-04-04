# Design — Card #77: Auto-Retrospective após cada Feature

## Visão Geral

Interface para visualização de retrospectivas automáticas geradas após cada feature ser homologada. **Público-alvo: o orquestrador (Alan)** — a retrospectiva existe para que ele identifique pontos de melhoria no workflow e implemente ações corretivas.

Prioridade: MVP com endpoint + arquivo Markdown (interface Kanban é future work).

---

## 1. Arquitetura de Renderização

### Estratégia
- **MVP:** Renderização server-side com template Markdown → HTML
- **Future work:** Componente React no dashboard Kanban

### Estrutura de Arquivo Persistido
```
/root/.openclaw/workspace/crypto/docs/retrospectives/
  2026-04-03-login-google-oauth.md
  2026-04-02-monitor-candles-async.md
  2026-04-01-portfolio-diversity-chart.md
```

> **Nota:** O arquivo `YYYY-MM-DD-{feature-slug}.md` é o artefato principal. Ele é lido pelo orquestrador e exposto via endpoint GET /retrospectives/{feature-slug}.

---

## 2. Template de Relatório (Markdown → HTML)

### Layout Base

```markdown
# 📋 Retrospective — {feature-slug}

**Card:** #{n} | **Data:** YYYY-MM-DD | **Classificação:** [{badge}]

---

## Resumo da Feature

| Campo | Valor |
|-------|-------|
| Nome | {feature-name} |
| Tipo | feature / bugfix / chore |
| Status | ✅ Homologada |
| Tempo Total | {total_time} |
| Homologada em | {homologated_at} |

---

## Métricas de Processo

| Stage | Tempo | Ciclos | Observação |
|-------|-------|--------|------------|
| PO | {po_time} | {po_cycles} | {po_note} |
| Design | {design_time} | {design_cycles} | {design_note} |
| Dev | {dev_time} | {dev_cycles} | {dev_note} |
| QA | {qa_time} | {qa_cycles} | {qa_note} |

**Tempo Total:** {total_time}

---

## 🔍 Análise de Processo (Para o Orchestrador)

### Onde o fluxo travou?
{process_analysis}

### O que melhorou em relação à feature anterior?
{improvement_from_previous}

### O que piorou em relação à feature anterior?
{regression_from_previous}

---

## 🎯 Recomendação para o Orchestrador

{actionable_recommendation_for_orchestrator}

---

## Classificação de Risco

| Indicador | Valor | Limite | Status | Implicação para o Fluxo |
|-----------|-------|--------|--------|--------------------------|
| Ciclos de Revisão | {cycles} | 3 | {badge} | {cycles_implication} |
| Blocker Total | {blocker_hours}h | 48h | {badge} | {blocker_implication} |
| Bugs Abertos | {open_bugs} | 2 | {badge} | {bugs_implication} |

**Resultado:** {classification}

---

## Blocker Events

| Início | Fim | Duração | Motivo | Stage |
|--------|-----|---------|--------|-------|
| {start} | {end} | {duration} | {reason} | {stage} |

---

## Histórico de Retrospectivas

| Data | Feature | Classificação | Pontos de Atenção |
|------|---------|---------------|-------------------|
| {date} | {slug} | {badge} | {attention_points} |

---

_Gerado automaticamente por auto-retrospective em {timestamp}_
```

**Nota sobre o template:** As seções **Análise de Processo** e **Recomendação para o Orchestrador** são as mais importantes — são o núcleo da value prop desta feature. O resto são dados de suporte.

---

## 3. Endpoint de Visualização

### GET /retrospectives

Lista todas as retrospectivas com paginação.

**Response:**
```json
{
  "retrospectives": [
    {
      "slug": "login-google-oauth",
      "card_id": 77,
      "feature_name": "Login Google OAuth",
      "date": "2026-04-03",
      "classification": "sem_problemas",
      "total_time": "6d 4h"
    }
  ],
  "total": 24,
  "page": 1,
  "per_page": 10
}
```

### GET /retrospectives/{feature-slug}

Retorna retrospectiva específica.

**Query params:**
- `format`: `markdown` | `html` (default: `html`)

**Response (HTML):**
```html
<!DOCTYPE html>
<html>
<head>
  <title>Retrospective — {feature-slug}</title>
  <!-- CSS inline com estilo consistente ao dashboard -->
</head>
<body>
  <!-- Template renderizado -->
</body>
</html>
```

---

## 4. Badges de Classificação

| Classificação | Cor | Badge |
|---------------|-----|-------|
| `sem_problemas` | verde | 🟢 Sem Problemas |
| `com_ressalvas` | amarelo | 🟡 Com Ressalvas |
| `problemática` | vermelho | 🔴 Problemática |

---

## 5. Componentes UI (Future Work — Kanban Integration)

> **Nota:** Estes componentes são para referência futura. Prioridade MVP é endpoint + Markdown.

### Componente 1: RetrospectiveCard

Exibido no hover ou clique de card homologado no Kanban.

```
┌─────────────────────────────────────┐
│ 📋 Retrospective                    │
├─────────────────────────────────────┤
│ Card #77 — Login Google OAuth       │
│ Homologada em: 2026-04-03          │
│                                     │
│ 🟢 Sem Problemas                    │
│                                     │
│ Tempo Total: 6d 4h                  │
│ ├─ PO: 1d 2h (1 ciclo)             │
│ ├─ Design: 8h (2 ciclos)           │
│ ├─ Dev: 3d 6h (2 ciclos)           │
│ └─ QA: 1d (1 ciclo)                │
│                                     │
│ [Ver Completa]                      │
└─────────────────────────────────────┘
```

### Componente 2: RetrospectivePanel

Painel lateral (drawer) com retrospectiva completa.

```
┌──────────────────────────────────────────────────────────┐
│ 📋 Retrospective — Login Google OAuth           [Fechar] │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Card #77 | 2026-04-03 | 🟢 Sem Problemas               │
│                                                          │
│ ══════════════════════════════════════════════════════  │
│                                                          │
│ 📊 Métricas de Tempo                                     │
│ ┌─────────────────────────────────────────────────────┐  │
│ │ PO         ████████████░░░░  1d 2h                 │  │
│ │ Design     ██████░░░░░░░░░  8h                     │  │
│ │ Dev        ████████████████████████████  3d 6h    │  │
│ │ QA         ████████████░░░░  1d                    │  │
│ └─────────────────────────────────────────────────────┘  │
│                                                          │
│ ✨ Pontos Positivos                                      │
│ • Review rápido, sem ciclos extras                      │
│ • Bugs mínimos em QA                                    │
│                                                          │
│ 🔧 Pontos de Melhoria                                    │
│ • Documentação inicial incompleta                        │
│ • Falta de testes E2E antes da PR                        │
│                                                          │
│ 📈 Classificação de Risco                                │
│ • Ciclos de Revisão: 6 (limite: 3) → 🟡                │
│ • Blocker Total: 4h (limite: 48h) → 🟢                  │
│ • Bugs Abertos: 1 (limite: 2) → 🟢                      │
│                                                          │
│ 📋 Ver Histórico Completa →                              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Componente 3: RetrospectiveTimeline

Exibido na view de retrospectivas (página dedicada).

```
┌─────────────────────────────────────────────────────────┐
│ 📊 Histórico de Retrospectivas                    [Filtros]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│ [🟢 Todos] [🟡 Com Ressalvas] [🔴 Problemáticas]       │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 2026-04-03  │ Login Google OAuth        │ 🟢      │ │
│ │             │ #77 · 6d 4h total         │         │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 2026-04-02  │ Monitor Candles Async     │ 🟡      │ │
│ │             │ #75 · 8d 2h total         │ 6 ciclos│ │
│ │             │                          │ revisão  │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 2026-04-01  │ Portfolio Diversity Chart │ 🟢     │ │
│ │             │ #73 · 4d total             │         │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ [← Anterior]  Página 1 de 3  [Próxima →]               │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Estados da Interface

### Estado: Loading
```
┌─────────────────────────────────────┐
│ 📋 Carregando retrospective...       │
│                                     │
│ ████████████░░░░░░░░░  60%          │
└─────────────────────────────────────┘
```

### Estado: Não Encontrada (404)
```
┌─────────────────────────────────────┐
│ ❌ Retrospective não encontrada      │
│                                     │
│ Card #XX ainda não possui           │
│ retrospective gerada.              │
│                                     │
│ [Voltar ao Histórico]              │
└─────────────────────────────────────┘
```

### Estado: Erro de Geração
```
┌─────────────────────────────────────┐
│ ⚠️ Erro na geração                  │
│                                     │
│ A retrospective foi triggerada    │
│ mas houve falha na geração.        │
│                                     │
│ [Tentar Novamente]                 │
└─────────────────────────────────────┘
```

---

## 7. Fluxo de Integração (Homologação → Retrospective)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Kanban     │     │ Orchestrator│     │  Background  │
│ Homologação  │────▶│   Hook      │────▶│    Job       │
│  (Alan)      │     │             │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          ▼                          │
                    │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
                    │  │   Coletor    │▶│ Classificador │▶│   LLM     │ │
                    │  │   (Task 2)   │  │   (Task 3)   │  │ (Task 4)  │ │
                    │  └──────────────┘  └──────────────┘  └───────────┘ │
                    │                          │                          │
                    │                          ▼                          │
                    │  ┌──────────────┐  ┌──────────────┐                 │
                    │  │ Persistência │  │  Endpoint    │                 │
                    │  │ (Task 5)     │  │  (Task 6)    │                 │
                    │  └──────────────┘  └──────────────┘                 │
                    │          │                                           │
                    │          ▼                                           │
                    │  ┌──────────────────────────────┐                    │
                    │  │  /docs/retrospectives/       │                    │
                    │  │  YYYY-MM-DD-{slug}.md        │                    │
                    │  └──────────────────────────────┘                    │
                    └──────────────────────────────────────────────────────┘
```

---

## 8. Prompt Guiding para Geração de Insights (acpx codex)

O prompt para o LLM deve ser **explícitamente orientado ao processo e ao orquestrador**. Exemplo de estrutura:

```
Você é um Scrum Master que analiza retrospectivas de features.
O público-alvo é o ORQUESTRADOR (Alan), não o time de desenvolvimento.

Sua tarefa: gerar a seção "Análise de Processo" e "Recomendação para o Orchestrador" de uma retrospectiva.

Regras:
1. Foque em COMO o processo funcionou, não em O QUE foi construído
2. Identifique padrões que o orquestrador pode corrigir (ex: "PO review sem deadline", "QA descobrindo bugs tarde", "Design com múltiplos ciclos")
3. Compare com a retrospectiva anterior quando existir
4. Seja específico: "Design precisou de 4 ciclos" é melhor que "Design teve problemas"
5. A recomendação DEVE ser acionável pelo orquestrador (mudar processo, adicionar gate, ajustar expectativa)

Input:
- Dados de tempo por stage: {}
- Ciclos por stage: {}
- Blockers: {}
- Retrospectiva anterior (se houver): {}

Output: JSON com campos: process_analysis, improvement_from_previous, regression_from_previous, actionable_recommendation_for_orchestrator
```

---

## 9. Checklist de Implementação

### Fase 1 — MVP (Prioridade)
- [ ] Task 5: Persistência em Markdown (template acima)
- [ ] Task 6: Endpoint GET /retrospectives/{slug}
- [ ] Renderização HTML server-side
- [ ] Task X: Prompt de LLM focado em processo/orquestrador (não genérico)

### Fase 2 — Completude
- [ ] Task 1-4: Pipeline de geração
- [ ] Task 7: Execução assíncrona
- [ ] Task 8: Testes E2E

### Fase 3 — Interface (Future Work)
- [ ] Componente RetrospectiveCard (hover/click no Kanban)
- [ ] Componente RetrospectivePanel (drawer lateral)
- [ ] Componente RetrospectiveTimeline (página histórica)

---

## 9. Dependências Visuais

O design usa:
- **Cores do tema existente** do dashboard (variables.css)
- **Ícones:** Lucide Icons (já usado no projeto)
- **Tipografia:** mesma do dashboard
- **Badges:** chips com borda arredondada e cor de fundo

### Variáveis CSS Recomendadas
```css
:root {
  --retro-success: #10b981;   /* verde */
  --retro-warning: #f59e0b;   /* amarelo */
  --retro-danger: #ef4444;    /* vermelho */
  --retro-bg-success: #d1fae5;
  --retro-bg-warning: #fef3c7;
  --retro-bg-danger: #fee2e2;
}
```

---

## 10. Responsabilidades por Arquivo

| Arquivo | Responsável |
|---------|-------------|
| `src/pages/RetrospectivePage.tsx` | DEV |
| `src/components/RetrospectiveCard.tsx` | DEV (future work) |
| `src/components/RetrospectivePanel.tsx` | DEV (future work) |
| `src/components/RetrospectiveTimeline.tsx` | DEV (future work) |
| `src/styles/retrospective.css` | DEV |
| `backend/routes/retrospectives.py` | DEV |
| Template Markdown | DESIGN (este arquivo) |
