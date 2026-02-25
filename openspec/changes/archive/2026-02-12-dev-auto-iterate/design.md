# Design: Dev Auto-Itera Antes do Trader

**Change:** dev-auto-iterate  
**Author:** amigoalan  
**Date:** 2026-02-12

---

## 🏗️ Onde mudar

- `backend/app/services/lab_graph.py`
  - Ajustar o fluxo do Dev para iterar automaticamente:
    - Se `dev_needs_retry=true` ou métricas ruins → aplicar ajuste e re-testar
  - O loop já existe parcialmente, mas precisa **aplicar ajustes reais** antes do próximo backtest.

- `backend/app/routes/lab.py`
  - Permitir que o Dev reescreva `template_data` e reexecute backtest internamente
  - Atualizar `dev_summary` somente na versão final

---

## 🔄 Fluxo proposto

```
Dev cria template → backtest
if falha:
  Dev ajusta parâmetros → backtest
  (até 3x)
Dev envia versão refinada
Trader avalia
```

---

## 🔧 Ajustes automáticos sugeridos

- Relaxar RSI (ex: >55 → >50)
- Remover filtros de volatilidade excessivos
- Reduzir número de condições simultâneas

---

## 🧪 Testes

- Cenário com 0 trades deve gerar 2ª iteração
- Cenário com sharpe baixo deve gerar ajuste
- Dev só entrega versão final
