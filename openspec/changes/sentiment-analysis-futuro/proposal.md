---
spec: openspec.v1
id: sentiment-analysis-futuro
title: Sentiment Analysis (Future)
card: "#58"
change_id: sentiment-analysis-futuro
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Proposal: Sentiment Analysis (Future)

**Card:** #58  
**change_id:** `sentiment-analysis-futuro`  
**Estágio:** PO  
**User Story:** Como trader, quero saber o sentiment do mercado (Fear & Greed, notícias) para complementar sinais técnicos.

---

## 1. User Story & Objetivos

**User Story:**
> Como trader, quero saber o sentiment do mercado (Fear & Greed, notícias) para complementar sinais técnicos e ter uma visão mais completa.

**Critérios de aceite:**
- Fear & Greed Index exibido (0-100, labels: Extreme Fear, Fear, Neutral, Greed, Extreme Greed)
- Score de notícias por ativo (sentiment positivo/negativo/neutro)
- Média ponderada de sentiment disponível via API
- Atualização a cada 15 minutos
- Dados históricos de sentiment (7 dias)

**Decisão-chave:** Este é um card de FUTURO. A implementação depende de fontes de dados externas (Fear & Greed API, notícias). Marca o escopo para quando for implementado.

---

## 2. Conexões com Outros Cards

### Este card depende de:
- Nenhum (dados externos, não depende de outros cards)

### Outros cards dependem deste:
- **Card #56** (ai-dashboard-insights) — consome sentiment para exibir insights

### Ordem de execução recomendada:
1. #58 pode ser implementado independentemente
2. #56 vai consumir os dados de sentiment quando disponível

---

## 3. Decisões Definidas

| Item | Decisão |
|------|---------|
| Fear & Greed source | Alternative.me Crypto Fear & Greed Index (free API) |
| News source | A definir (mock para início) |
| Update frequency | A cada 15 minutos |
| Retention | 7 dias de histórico |
| Sentiment score | -1 (negative) to +1 (positive) |

---

## 4. Escopo

### Dentro do escopo
- [ ] Integração com Fear & Greed Index API
- [ ] Score de sentiment para ativos específicos
- [ ] API interna para servir sentiment
- [ ] Cache em memória
- [ ] Histórico de 7 dias

### Fora do escopo
- [ ] Implementação real de NLP para notícias (futuro)
- [ ] Alertas baseados em sentiment
- [ ] Correlação automática com sinais

---

## 5. Arquitetura

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Backend    │────▶│  Sentiment   │────▶│ Fear&Greed  │
│  FastAPI     │◀────│   Service    │◀────│    API       │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                     ┌─────▼─────┐
                     │   Cache   │
                     └───────────┘
```

**Stack:**
- Backend: FastAPI (existing service on :8003)
- External: Alternative.me Fear & Greed API
- Cache: in-memory dict

---

## 6. API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/sentiment` | Fear & Greed geral |
| GET | `/sentiment/{asset}` | Sentiment específico por ativo |

**GET /sentiment — Response:**
```json
{
  "fear_greed_index": 45,
  "label": "Fear",
  "timestamp": "2026-03-27T12:00:00Z",
  "previous_close": 42,
  "last_updated": "2026-03-27T11:45:00Z"
}
```

**GET /sentiment/{asset} — Response:**
```json
{
  "asset": "BTCUSDT",
  "news_sentiment": 0.25,
  "label": "Slightly Bullish",
  "sources_count": 12,
  "timestamp": "2026-03-27T12:00:00Z"
}
```

---

## 7. Custos

| Recurso | Custo |
|---------|-------|
| Fear & Greed API | $0 (free tier) |
| News API | $0 (mock inicial) |
| **Total** | **$0/mês** |

---

## 8. Riscos

| Risco | Mitigação |
|-------|-----------|
| API externa fora do ar | Cache + fallback para último valor |
| Dados de notícias indisponíveis | Mock com sentiment neutro |

---

## 9. Próximo Passo

Passar para DESIGN para especificação de UI.

---
