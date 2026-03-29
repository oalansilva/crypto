---
spec: openspec.v1
id: ai-dashboard-insights
title: AI Dashboard + Insights
card: "#56"
change_id: ai-dashboard-insights
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Proposal: AI Dashboard + Insights

**Card:** #56  
**change_id:** `ai-dashboard-insights`  
**Estágio:** PO  
**User Story:** Como trader, quero ver um dashboard com AI insights que combine sinais, indicadores e sentiment para tomar decisões melhores.

---

## 1. User Story & Objetivos

**User Story:**
> Como trader, quero ver um dashboard com AI insights que combine sinais, indicadores e sentiment para tomar decisões melhores.

**Critérios de aceite:**
- Dashboard principal com visão consolidada
- AI insights gerados automaticamente
- Cards de indicadores (RSI, MACD, Bollinger) por ativo
- Fear & Greed Index visível
- Histórico de sinais com métricas
- Resumo de posições e P&L

**Decisão-chave:** Este card é o consolidador — consome dados de #53 (sinais), #55 (indicadores), #57 (histórico), #58 (sentiment).

---

## 2. Conexões com Outros Cards

### Este card depende de:
- **Card #53** (sinais-de-trading-buy-sell-hold) — sinais BUY/SELL/HOLD para exibir
- **Card #55** (indicadores-tecnicos) — RSI, MACD, Bollinger Bands
- **Card #57** (historico-sinais) — métricas e histórico
- **Card #58** (sentiment-analysis-futuro) — Fear & Greed e sentiment

### Outros cards dependem deste:
- Nenhum (é um card final de exibição)

### Ordem de execução recomendada:
1. #55, #57, #58 devem existir antes de #56
2. #53 também deve existir
3. #56 é implementado por último, agregando tudo

---

## 3. Decisões Definidas

| Item | Decisão |
|------|---------|
| AI insights | Baseados em regras (não LLM real) |
| Refresh | Manual + auto a cada 5 min |
| Layout | Grid responsivo de cards |
| Infraestrutura | $0 — frontend + APIs existentes |

---

## 4. Escopo

### Dentro do escopo
- [ ] Dashboard principal consolidado
- [ ] Card de AI insights (regras)
- [ ] Cards de indicadores por ativo
- [ ] Fear & Greed gauge
- [ ] Resumo de sinais recentes
- [ ] Métricas de performance (hit rate, etc)

### Fora do escopo
- [ ] LLM para gerar insights (futuro)
- [ ] Alertas push
- [ ] Customização de layout

---

## 5. Arquitetura

```
┌──────────────────────────────────────────────────────┐
│                    AI Dashboard                      │
├────────────┬────────────┬────────────┬──────────────┤
│  #53 Sinais│ #55 Indic. │ #58 Sentim.│ #57 Histórico│
└────────────┴────────────┴────────────┴──────────────┘
```

**Stack:**
- Frontend: React + TypeScript
- Charts: Recharts
- State: React Query

---

## 6. Layout do Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  🤖 AI Insights                    [Fear & Greed: 45]  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ RSI: 45     │  │ MACD: Alta  │  │ BB: Normal  │     │
│  │ BTCUSDT     │  │ BTCUSDT     │  │ BTCUSDT     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│  📊 Sinais Recentes          📈 Métricas               │
│  BUY  BTC  82%              Hit Rate: 72%              │
│  SELL ETH  75%             Total Sinais: 150           │
│  HOLD SOL  68%             Avg Confidence: 78%          │
└─────────────────────────────────────────────────────────┘
```

---

## 7. API (Agregação)

O frontend consome múltiplas APIs já existentes:

- `GET /signals/latest` (#53)
- `GET /indicators/{asset}` (#55)
- `GET /sentiment` (#58)
- `GET /signals/stats` (#57)

---

## 8. Custos

| Recurso | Custo |
|---------|-------|
| Frontend (reativo) | $0 |
| APIs existentes | $0 |
| **Total** | **$0/mês** |

---

## 9. Riscos

| Risco | Mitigação |
|-------|-----------|
| Múltiplas APIs lentas | Parallel fetch + loading states |
| Dados indisponíveis | Graceful degradation por card |

---

## 10. Próximo Passo

Passar para DESIGN para especificação de layout detalhado.

---
