# Proposal: Sinais de Trading BUY/SELL/HOLD

**Card:** #53  
**change_id:** `sinais-de-trading-buy-sell-hold`  
**Estágio:** PO  
**User Story:** Como trader, quero ver sinais BUY/SELL/HOLD com confiança para saber quando entrar/sair de posições.

---

## 1. User Story & Objetivos

**User Story:**
> Como trader, quero ver sinais BUY/SELL/HOLD com confiança para saber quando entrar/sair de posições.

**Critérios de aceite:**
- Sinais BUY/SELL/HOLD exibidos com confidence score (0–100%)
- Apenas sinais com confidence ≥ 70% são exibidos
- Target price e stop-loss visíveis por sinal
- Lista filtrável por tipo, confidence e ativo
- Disclaimer sempre visível

**Decisão-chave:** O modelo é um ensemble LSTM + RandomForest. A implementação completa dos indicadores (RSI, MACD, Bollinger Bands) será tratada no Card #55.

---

## 2. Decisões Definidas (Card #51)

| Item | Decisão |
|------|---------|
| Data source | Binance API (free tier) |
| Confidence threshold | 70% (mínimo para exibir) |
| Risk profile | Escolha do usuário (conservative / moderate / aggressive) |
| Infraestrutura | $0 — PostgreSQL no VPS + cache in-memory |
| Disclaimer | "Isenção de responsabilidade: este não é advice financeiro." |

---

## 3. Escopo

### Dentro do escopo
- [ ] API de sinais (GET /signals) retornando BUY/SELL/HOLD com confidence
- [ ] SignalCard — componente visual de sinal individual
- [ ] Lista de sinais com filtros (tipo, confidence, ativo)
- [ ] Confidence gauge (0–100%, threshold 70%)
- [ ] Target price e stop-loss por sinal
- [ ] Risk profile selector (conservative/moderate/aggressive)
- [ ] Disclaimer fixo na interface

### Fora do escopo (Card #55)
- Implementação completa dos indicadores RSI, MACD, Bollinger Bands
- Machine learning model training pipeline

---

## 4. Arquitetura

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  Binance API │
│  (React)     │◀────│  FastAPI     │◀────│  (market)    │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                     ┌─────▼─────┐
                     │ PostgreSQL │
                     │ + Cache    │
                     └───────────┘
```

**Stack:**
- Frontend: React + TypeScript (existing codebase)
- Backend: FastAPI (existing service on :8003)
- Database: PostgreSQL on VPS
- Cache: in-memory (Redis ou dict Python)

---

## 5. API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/signals` | Lista sinais com filtros (type, confidence_min, asset, risk_profile) |
| GET | `/signals/{id}` | Detalhe de um sinal |
| GET | `/signals/latest` | Últimos sinais gerados |

**GET /signals — Query params:**
- `type`: BUY | SELL | HOLD (opcional)
- `confidence_min`: int 0–100 (default 70)
- `asset`: string ex: BTCUSDT (opcional)
- `risk_profile`: conservative | moderate | aggressive
- `limit`: int (default 20, max 100)

**Response:**
```json
{
  "signals": [
    {
      "id": "uuid",
      "asset": "BTCUSDT",
      "type": "BUY",
      "confidence": 82,
      "target_price": 97500.00,
      "stop_loss": 91000.00,
      "indicators": { "RSI": 35, "MACD": "bullish" },
      "created_at": "2026-03-26T12:00:00Z",
      "risk_profile": "moderate"
    }
  ],
  "total": 1
}
```

---

## 6. Custos

| Recurso | Custo |
|---------|-------|
| Binance API | $0 (free tier — 1200 requests/min) |
| PostgreSQL (VPS) | $0 (já existente) |
| Cache in-memory | $0 |
| **Total** | **$0/mês** |

---

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| Binance rate limit | Cache + backoff exponencial |
| Sinais falsos (over-trading) | Threshold 70% + risk profile |
| Dados desatualizados | TTL curto no cache (5 min) |
| Sem dados históricos | Fallback graceful + mensagem |

---

## 8. Próximo Passo

Passar para DESIGN para especificação de UI/UX e layout dos componentes.
