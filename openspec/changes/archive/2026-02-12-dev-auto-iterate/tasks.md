# Tasks: Dev Auto-Itera

**Change:** dev-auto-iterate  
**Estimated:** ~4h  
**Priority:** high

---

## ✅ Tarefas

1. Implementar loop de auto-ajuste do Dev
   - Detectar falhas (0 trades, sharpe baixo, drawdown alto)
   - Aplicar ajuste automático
   - Reexecutar backtest

2. Atualizar `dev_summary`
   - Só retornar versão final refinada

3. Testes
   - Garantir que 0 trades gera nova iteração
   - Garantir que sharpe baixo gera ajuste

---

## ✅ Critérios de Aceite

- Dev auto-iterando antes do Trader
- Trader recebe versão refinada
- 1–3 iterações automáticas
