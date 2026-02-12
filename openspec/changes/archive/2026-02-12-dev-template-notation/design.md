# Design: Dev Template Notation (auto-correção)

**Change:** dev-template-notation  
**Author:** amigoalan  
**Date:** 2026-02-12

---

## 🏗️ Onde mudar

- `backend/app/services/lab_graph.py`
  - Atualizar `DEV_SENIOR_PROMPT` com regras explícitas:
    - Proibir texto livre em `entry_logic`/`exit_logic`
    - Exigir operadores booleanos (`AND`, `OR`, comparações numéricas)
    - Exigir `stop_loss` float
    - Instruir auto-checagem e correção

---

## 🧪 Validação

- Dev deve reavaliar a própria saída antes de responder.
- Se detectar palavras como "cruza", "quando", "retorna", deve converter para comparação válida.

---

## 🔄 Exemplo esperado

**Entrada inválida:**
```
entry_logic: "rsi14 cruza acima de 55"
exit_logic: "sair quando rsi voltar para 45–55"
stop_loss: "stop em 2x ATR"
```

**Saída corrigida:**
```
entry_logic: "rsi14 > 55 AND close > ema50"
exit_logic: "rsi14 < 45 OR close < ema50"
stop_loss: 0.03
```
