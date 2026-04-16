# Review PT-BR — Card #92

## Resumo

**Card:** #92 — Unificar Sinais  
**Projeto:** crypto  
**Mudar:** Criar UM sinal consolidado por ativo que combina AI Dashboard, On-chain e Signals

---

## ⚠️ Mudança de Escopo (Alan)

**Abordagem rejeitada:**
- Sinais separados por fonte com badges
- Filtros por fonte

**Abordagem nova:**
- Um único sinal por ativo (não três)
- Interface mostra apenas o sinal final unificado
- Indicação de quais fontes contribuíram

---

## O que é

Card de **consolidação de sinais** — criar UM sinal único por ativo que combina:
- `/ai-dashboard` — sinais de IA
- `/signals/onchain` — sinais on-chain
- `/signals` — sinais gerais

**Resultado:** BTC tem UM sinal consolidado, não três sinais separados.

---

## Decisão Necessária

1. **Lógica de consolidação?** Voting, weighted, ou outro algoritmo?
2. **Breakdown visível?** Mostrar contribuição de cada fonte ou só o resultado?
3. **O que acontece se fontes conflitam?** Ex: AI bullish, On-chain bearish

---

## Tradeoffs

| | Prós | Contras |
|---|---|---|
| **Consolidado** | Decisão simples, sem confusão | Perde granularidade |
| **Separado** | Mais informação | Usuário precisa interpretar |

---

## ⚠️ Prototype Obrigatório

**Este card requer protótipo UI antes de Alan approval.**

DESIGN deve criar protótipo mostrando:
- Um sinal por ativo (não três)
- Sinal consolidado com indicação de direção/força
- Breakdown opcional por fonte

---

## Próximo Passo

**DESIGN → Prototype** → Alan approval → DEV

---

## Artefatos

- `openspec/changes/unifiicar-sinais/proposal.md`
- `openspec/changes/unifiicar-sinais/review-ptbr.md`
- `openspec/changes/unifiicar-sinais/tasks.md`
