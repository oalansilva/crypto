---
spec: openspec.v1
id: historico-sinais
title: Tasks - Histórico de Sinais
card: "#57"
change_id: historico-sinais
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Tasks: Histórico de Sinais

**Card:** #57 | `historico-sinais`

---

## Tarefas de Desenvolvimento

### Backend (FastAPI)

- [ ] **T-001:** Criar tabela `signal_history` no PostgreSQL
- [ ] **T-002:** Adicionar índices em asset, created_at, status
- [ ] **T-003:** Implementar endpoint GET `/signals/history`
- [ ] **T-004:** Implementar endpoint GET `/signals/history/{id}`
- [ ] **T-005:** Implementar endpoint PUT `/signals/{id}/status`
- [ ] **T-006:** Implementar endpoint GET `/signals/stats`
- [ ] **T-007:** Adicionar filtros: asset, type, status, data_inicio, data_fim, confidence_min
- [ ] **T-008:** Implementar paginação (limit, offset)
- [ ] **T-009:** Configurar archiving automático após 90 dias
- [ ] **T-021:** Adicionar campo `pnl` à tabela `signal_history` (DECIMAL)
- [ ] **T-022:** Implementar cálculo PnL por sinal: (preço saída - preço entrada) × quantidade
- [ ] **T-023:** Endpoint GET `/signals/history` incluir campo pnl na resposta

### Frontend (React)

- [ ] **T-010:** Criar componente SignalHistoryList
- [ ] **T-011:** Criar componente SignalHistoryCard (detalhe)
- [ ] **T-012:** Criar componente SignalStats
- [ ] **T-013:** Implementar filtros na UI
- [ ] **T-014:** Implementar paginação na UI
- [ ] **T-024:** Exibir PnL na SignalHistoryList (coluna PnL com cor verde/vermelha)
- [ ] **T-025:** Exibir PnL no SignalHistoryCard (detail drawer)

### Integração

- [ ] **T-015:** Card #53 deve chamar API de histórico ao gerar sinal
- [ ] **T-016:** Documentar no swagger

### Testes

- [ ] **T-017:** Teste de CRUD de histórico
- [ ] **T-018:** Teste de filtros
- [ ] **T-019:** Teste de paginação
- [ ] **T-020:** Teste de archiving
- [ ] **T-026:** Teste de cálculo PnL por sinal

---

## Critérios de Conclusão

- [ ] Sinais são salvos automaticamente ao serem gerados
- [ ] Filtros funcionam corretamente
- [ ] Paginação performance OK com 1000+ registros
- [ ] UI exibe dados de forma clara
- [ ] PnL é calculado e exibido por sinal
- [ ] PnL positivo exibido em verde, negativo em vermelho

---

## Dependencies

- Card #53 (sinais-de-trading-buy-sell-hold) — fornece sinais

## Dependentes

- Card #56 (ai-dashboard-insights) — consome histórico

---
