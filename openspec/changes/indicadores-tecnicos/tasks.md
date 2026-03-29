---
spec: openspec.v1
id: indicadores-tecnicos
title: Tasks - Indicadores Técnicos
card: "#55"
change_id: indicadores-tecnicos
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Tasks: Indicadores Técnicos

**Card:** #55 | `indicadores-tecnicos`

---

## Tarefas de Desenvolvimento

### Backend (FastAPI)

- [ ] **T-001:** Criar módulo `indicadores_calculator.py` com funções RSI, MACD, Bollinger
- [ ] **T-002:** Implementar cálculo de RSI com período 14
- [ ] **T-003:** Implementar cálculo de MACD com padrão 12/26/9
- [ ] **T-004:** Implementar cálculo de Bollinger Bands (20 períodos, 2 desvios)
- [ ] **T-005:** Criar cache em memória com TTL configurável
- [ ] **T-006:** Implementar endpoint GET `/indicators/{asset}`
- [ ] **T-007:** Implementar endpoints específicos `/indicators/{asset}/rsi`, `/macd`, `/bollinger`
- [ ] **T-008:** Adicionar suporte a múltiplos timeframes
- [ ] **T-009:** Tratar erro quando dados históricos < 100 candles
- [ ] **T-010:** Adicionar logging e métricas

### Integração

- [ ] **T-011:** Garantir que Card #53 pode consumir `/indicators/{asset}` corretamente
- [ ] **T-012:** Documentar API interna no swagger (/docs)

### Testes

- [ ] **T-013:** Teste unitário para RSI com dados conhecidos
- [ ] **T-014:** Teste unitário para MACD com dados conhecidos
- [ ] **T-015:** Teste unitário para Bollinger Bands com dados conhecidos
- [ ] **T-016:** Teste de integração com Binance API (mock)

---

## Critérios de Conclusão

- [ ] Todos os 3 indicadores (RSI, MACD, Bollinger) calculando corretamente
- [ ] API respondendo em < 200ms com cache
- [ ] Testes unitários passando
- [ ] Documentação no swagger

---

## Dependencies

- Nenhuma (este card não depende de outros)

## Dependentes

- Card #53 (sinais-de-trading-buy-sell-hold) — precisa dos indicadores
- Card #56 (ai-dashboard-insights) — pode consumir indicadores

---
