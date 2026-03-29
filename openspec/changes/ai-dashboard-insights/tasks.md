---
spec: openspec.v1
id: ai-dashboard-insights
title: Tasks - AI Dashboard + Insights
card: "#56"
change_id: ai-dashboard-insights
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Tasks: AI Dashboard + Insights

**Card:** #56 | `ai-dashboard-insights`

---

## Tarefas de Desenvolvimento

### Frontend (React)

- [ ] **T-001:** Criar componente AIDashboard (container principal)
- [ ] **T-002:** Implementar fetch paralelo das APIs (#53, #55, #57, #58)
- [ ] **T-003:** Criar componente AIInsightsCard
- [ ] **T-004:** Implementar regras de geração de insights
- [ ] **T-005:** Integrar FearGreedGauge de #58
- [ ] **T-006:** Criar IndicatorCards (RSI, MACD, Bollinger)
- [ ] **T-007:** Integrar SignalsList de #53
- [ ] **T-008:** Integrar StatsCards de #57
- [ ] **T-009:** Implementar estados de loading por seção
- [ ] **T-010:** Implementar graceful degradation
- [ ] **T-011:** Implementar responsividade (desktop, tablet, mobile)
- [ ] **T-012:** Adicionar botão de refresh manual

### Testes

- [ ] **T-013:** Teste de renderização com dados mock
- [ ] **T-014:** Teste de graceful degradation (API falhando)
- [ ] **T-015:** Teste de responsividade
- [ ] **T-016:** Teste de regras de AI insights

---

## Critérios de Conclusão

- [ ] Dashboard exibe dados de todas as 4 APIs
- [ ] AI insights gerados corretamente
- [ ] Seção com erro não quebra dashboard
- [ ] Responsivo em todos os breakpoints

---

## Dependencies

- Card #53 (sinais-de-trading-buy-sell-hold)
- Card #55 (indicadores-tecnicos)
- Card #57 (historico-sinais)
- Card #58 (sentiment-analysis-futuro)

## Dependentes

- Nenhum

---
