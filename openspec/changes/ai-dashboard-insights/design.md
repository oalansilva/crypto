---
spec: openspec.v1
id: ai-dashboard-insights
title: AI Dashboard + Insights - Design
card: "#56"
change_id: ai-dashboard-insights
stage: DESIGN
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Design: AI Dashboard + Insights

**Card:** #56 | `ai-dashboard-insights`

---

## 1. Visão Geral

Dashboard consolidado que agrega dados de múltiplos cards para dar visão unificada ao trader.

### Estrutura de Layout

```
┌─────────────────────────────────────────────────────────┐
│  🤖 AI Dashboard                              [Refresh] │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │ 💡 AI Insights - "RSI em sobrevenda, potencial   │   │
│  │    BUY para BTC se MACD cruzar"                  │   │
│  └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  Fear & Greed    │         Indicadores Ativo            │
│  ┌─────────┐     │  ┌─────────┬─────────┬─────────┐  │
│  │  Gauge  │     │  │   RSI   │  MACD   │   BB    │  │
│  │   45    │     │  │   45    │ bullish │  normal │  │
│  │  Fear   │     │  │  BTC    │  BTC    │   BTC   │  │
│  └─────────┘     │  └─────────┴─────────┴─────────┘  │
├─────────────────────────────────────────────────────────┤
│  Sinais Recentes         │  Métricas de Performance     │
│  ┌───────────────────┐   │  ┌───────────────────────┐   │
│  │ BUY  BTC  82%     │   │  │ Hit Rate: 72%         │   │
│  │ SELL ETH  75%     │   │  │ Total: 150 sinais     │   │
│  │ HOLD SOL  68%     │   │  │ Avg Confidence: 78%   │   │
│  └───────────────────┘   │  └───────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Componentes

### AIDashboard (container)

- Layout grid responsivo
- Gerencia fetch de todas as APIs
- Estados: loading (por seção), error (graceful), populated

### AIInsightsCard

- Texto gerado por regras
- Exemplo: "RSI < 30 = sobrevenda", "MACD crossover = bullish"
- Fallback: "Insights indisponíveis"

### FearGreedGauge

- Componente de #58
- Gauge circular com cores

### IndicatorCards

- 3 cards: RSI, MACD, Bollinger
- Componentes de #55
- Por ativo selecionado

### SignalsList

- Lista de sinais recentes
- Componente de #53
- Máximo 5 itens

### StatsCards

- Métricas de #57
- Hit rate, total, avg confidence

---

## 3. Regras de AI Insights

```
IF rsi > 70 THEN "RSI em sobrecompra - cautela com BUY"
IF rsi < 30 THEN "RSI em sobrevenda - potencial BUY"
IF macd_crossover == "bullish" THEN "MACD cruzou para alta"
IF fear_greed < 30 THEN "Mercado em medo extremo"
IF fear_greed > 70 THEN "Mercado em ganância extrema"
```

---

## 4. Estados

| Estado | UI |
|--------|-----|
| Loading | Skeleton em cada seção |
| Partial Error | Seção com erro mostra retry, resto funciona |
| Error All | Mensagem centralizada |
| Populated | Dashboard completo |

---

## 5. Responsividade

- Desktop: Grid 3 colunas
- Tablet: Grid 2 colunas
- Mobile: Stack vertical

---

## 6. Próximo Passo

Após DESIGN, passar para Alan approval.

---
