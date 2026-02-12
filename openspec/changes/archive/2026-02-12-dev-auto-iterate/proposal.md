# Change Proposal: Dev Auto-Itera Antes do Trader

**Status:** 🟡 draft  
**Created:** 2026-02-12  
**Author:** amigoalan (OpenClaw)  
**Priority:** high  
**Type:** enhancement

---

## Why

O fluxo atual faz o Dev **testar apenas uma vez** e depois **entregar sugestões textuais**, sem auto‑aplicar ajustes. Isso gera rejeições evitáveis e passa trabalho manual para o Trader.

O Alan pediu explicitamente: **o Dev deve ajustar e retestar** antes de enviar ao Trader.

---

## 🎯 Objetivo

1. Dev deve **auto‑iterar** (1–3 vezes) quando métricas falharem.
2. Dev só envia ao Trader **após refinar** a estratégia.
3. Trader avalia apenas a versão melhorada.

---

## ✅ Critérios de Aceite

1. Dev aplica ajustes automaticamente ao detectar falha (0 trades, sharpe baixo, drawdown alto).
2. Backtest é reexecutado após cada ajuste.
3. Trader recebe versão já refinada.

---

## 📝 Notas

Ver `design.md` e `tasks.md`.
