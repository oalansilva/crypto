---
spec: openspec.v1
id: indicadores-tecnicos
title: Review PT-BR - Indicadores Técnicos
card: "#55"
change_id: indicadores-tecnicos
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Review PT-BR: Indicadores Técnicos

**Card:** #55 | `indicadores-tecnicos`

---

## Resumo Executivo

Este card implementa o cálculo de indicadores técnicos (RSI, MACD, Bollinger Bands) que serão usados como base para os sinais de trading do Card #53.

### O que este card faz:
- Calcula RSI, MACD e Bollinger Bands em tempo real
- Disponibiliza via API interna
- Usa dados da Binance API
- Tem cache em memória

### O que este card NÃO faz:
- Não exibe gráficos (isso é do Card #56)
- Não gera sinais de trading (isso é do Card #53)
- Não envia notificações

---

## Pontos de Atenção

1. **Dependência crítica para Card #53:** O Card #53 (Sinais BUY/SELL/HOLD) depende diretamente dos indicadores aqui calculados. Sem #55, #53 não pode ir para DEV.

2. **Dados históricos:** Necessário mínimo de 100 candles para calcular indicadores corretamente.

3. **Performance:** O cache deve ser bem configurado para evitar recalcular a cada request.

---

## Checklist de Validação

- [ ] RSI com período 14 está correto
- [ ] MACD com padrão 12/26/9 está correto
- [ ] Bollinger Bands com 20 períodos e 2 desvios padrão está correto
- [ ] Cache TTL de 5 minutos é adequado
- [ ] API retorna todos os indicadores em um único endpoint
- [ ] Suporta múltiplos timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- [ ] Fallback graceful quando dados insuficientes

---

## Decisões de Design Confirmadas

| Item | Valor |
|------|-------|
| RSI período | 14 |
| MACD | 12, 26, 9 |
| Bollinger | 20, 2 |
| Cache TTL | 5 min |
| Mínimo candles | 100 |

---

## Status: PRONTO PARA APROVAÇÃO

Este card está pronto para avançar para DESIGN e subsequentemente para DEV.

---
