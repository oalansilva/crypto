---
spec: openspec.v1
id: indicadores-tecnicos
title: Indicadores Técnicos (RSI, MACD, Bollinger Bands)
card: "#55"
change_id: indicadores-tecnicos
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Proposal: Indicadores Técnicos (RSI, MACD, Bollinger Bands)

**Card:** #55  
**change_id:** `indicadores-tecnicos`  
**Estágio:** PO  
**User Story:** Como sistema de trading, preciso de indicadores técnicos (RSI, MACD, Bollinger Bands) para gerar sinais BUY/SELL/HOLD confiáveis.

---

## 1. User Story & Objetivos

**User Story:**
> Como sistema de trading, preciso de indicadores técnicos (RSI, MACD, Bollinger Bands) para gerar sinais BUY/SELL/HOLD com confiança.

**Critérios de aceite:**
- RSI calculado em tempo real (período 14 como default)
- MACD calculado com linha de sinal e histograma
- Bollinger Bands com média móvel e 2 desvios padrão
- Todos os indicadores disponíveis via API interna
- Dados históricos de no mínimo 100 candles para cálculo

**Decisão-chave:** Este card é PRÉ-REQUISITO para o Card #53 (Sinais de Trading BUY/SELL/HOLD). O Card #53 usa esses indicadores para gerar sinais.

---

## 2. Conexões com Outros Cards

### Este card depende de:
- Nenhum (é independente, não tem dependências de outros cards)

### Outros cards dependem deste:
- **Card #53** (sinais-de-trading-buy-sell-hold) — USA RSI, MACD, Bollinger Bands para gerar sinais BUY/SELL/HOLD
- **Card #56** (ai-dashboard-insights) — pode exibir indicadores no dashboard

### Ordem de execução recomendada:
1. Este card (#55) deve ser completado ANTES de #53 ir para DEV
2. #56 pode consumir dados deste card em paralelo ou após

---

## 3. Decisões Definidas

| Item | Decisão |
|------|---------|
| RSI período default | 14 |
| MACD padrão | 12, 26, 9 (fast, slow, signal) |
| Bollinger Bands | 20 períodos, 2 desvios padrão |
| Data source | Binance API (candles) |
| Update frequency | A cada novo candle (1m, 5m, 15m, 1h, 4h, 1d) |
| Infraestrutura | $0 — mesmo serviço FastAPI existente |

---

## 4. Escopo

### Dentro do escopo
- [ ] Cálculo de RSI (Relative Strength Index)
- [ ] Cálculo de MACD (Moving Average Convergence Divergence)
- [ ] Cálculo de Bollinger Bands
- [ ] API interna para servir indicadores por ativo/timeframe
- [ ] Suporte a múltiplos timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- [ ] Cache em memória dos indicadores calculados

### Fora do escopo
- [ ] Frontend de visualização (Card #56)
- [ ] Sinais de trading (Card #53)
- [ ] Alertas ou notificações
- [ ] Backtesting

---

## 5. Arquitetura

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Backend    │────▶│   Indicadores│────▶│  Binance API │
│  FastAPI     │◀────│   Service    │◀────│  (candles)   │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                     ┌─────▼─────┐
                     │   Cache   │
                     │ in-memory │
                     └───────────┘
```

**Stack:**
- Backend: FastAPI (existing service on :8003)
- Cálculos: pandas + ta-lib (ou numpy puro)
- Cache: in-memory dict com TTL

---

## 6. API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/indicators/{asset}` | Indicadores calculados para ativo |
| GET | `/indicators/{asset}/rs i` | Apenas RSI |
| GET | `/indicators/{asset}/macd` | Apenas MACD |
| GET | `/indicators/{asset}/bollinger` | Apenas Bollinger Bands |

**GET /indicators/{asset} — Query params:**
- `timeframe`: 1m | 5m | 15m | 1h | 4h | 1d (default 1h)
- `period`: int (default 14 para RSI, 20 para BB)

**Response:**
```json
{
  "asset": "BTCUSDT",
  "timeframe": "1h",
  "timestamp": "2026-03-27T12:00:00Z",
  "rsi": 45.3,
  "macd": {
    "macd_line": 150.25,
    "signal_line": 140.50,
    "histogram": 9.75
  },
  "bollinger_bands": {
    "upper": 97500.00,
    "middle": 96500.00,
    "lower": 95500.00
  }
}
```

---

## 7. Custos

| Recurso | Custo |
|---------|-------|
| Binance API | $0 (free tier) |
| Computação adicional | $0 (mesmo servidor) |
| **Total** | **$0/mês** |

---

## 8. Riscos

| Risco | Mitigação |
|-------|-----------|
| Binance rate limit | Cache + backoff exponencial |
| Dados incompletos para cálculo | Requer mínimo 100 candles |
| Performance com múltiplos ativos | Cache com TTL configurável |

---

## 9. Próximo Passo

Passar para DESIGN para especificação de como os indicadores serão exibidos (mesmo que seja para consumo interno de outros serviços).

---
