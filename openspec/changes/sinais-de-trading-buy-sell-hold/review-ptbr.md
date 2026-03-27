# Review PT-BR: Sinais de Trading BUY/SELL/HOLD

**Card:** #53  
**change_id:** `sinais-de-trading-buy-sell-hold`  
**Estágio:** PO → DESIGN

---

## O que é

Interface para exibir sinais de trading (BUY/SELL/HOLD) com confidence score, target price e stop-loss. Usa dados da Binance API + modelo LSTM+RandomForest (Card #55).

## Decisões-chave

| Item | Valor |
|------|-------|
| Threshold mínimo | 70% confidence |
| Data source | Binance API (gratuita) |
| Infra | $0 (PostgreSQL + cache in-memory no VPS) |
| Risk profile | 3 opções: Conservative / Moderate / Aggressive |
| Disclaimer | Sempre visível: "não é advice financeiro" |

## Escopo

**Dentro:** API de sinais, SignalCard, lista com filtros, confidence gauge, target/stop, risk selector.  
**Fora:** Implementação de indicadores (RSI/MACD/BB) — isso é Card #55.

## Arquitetura

- Backend: FastAPI em :8003
- Frontend: React em :5173
- Cache: 5 min TTL
- Endpoints: `GET /signals`, `GET /signals/{id}`, `GET /signals/latest`

## Modelo de ML (referência)

Ensemble LSTM + RandomForest que recebe dados de preço + indicadores e saída BUY/SELL/HOLD com confidence. Treinamento no Card #55.

## Custos

**Total: $0/mês** — tudo no VPS existente.

## Próximo passo

Passar para DESIGN para especificação de UI/UX e layout dos componentes SignalCard, lista de sinais, filtros e gauge de confidence.

## Status

✅ Proposal-approved (Card #51)  
⏳ Aguardando DESIGN  
🔗 Dependência: Card #55 (indicadores)
