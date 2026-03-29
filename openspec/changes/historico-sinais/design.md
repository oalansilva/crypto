---
spec: openspec.v1
id: historico-sinais
title: Histórico de Sinais - Design
card: "#57"
change_id: historico-sinais
stage: DESIGN
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Design: Histórico de Sinais

**Card:** #57 | `historico-sinais`

---

## 1. Visão Geral

Interface para visualização do histórico de sinais de trading gerados pelo Card #53.

### Estrutura de Dados

```sql
CREATE TABLE signal_history (
    id UUID PRIMARY KEY,
    asset VARCHAR(20) NOT NULL,
    type VARCHAR(10) NOT NULL,  -- BUY, SELL, HOLD
    confidence INTEGER NOT NULL,
    target_price DECIMAL,
    stop_loss DECIMAL,
    status VARCHAR(20) NOT NULL,  -- ativo, disparado, expirado, cancelado
    indicators_snapshot JSONB,
    created_at TIMESTAMP NOT NULL,
    triggered_at TIMESTAMP,
    price_at_trigger DECIMAL,
    exit_price DECIMAL,  -- preço de saída (para cálculo PnL)
    pnl DECIMAL,  -- Profit and Loss: (exit_price - price_at_trigger) × quantidade
    quantity DECIMAL DEFAULT 1,
    updated_at TIMESTAMP
);

CREATE INDEX idx_signal_history_asset ON signal_history(asset);
CREATE INDEX idx_signal_history_created_at ON signal_history(created_at);
CREATE INDEX idx_signal_history_status ON signal_history(status);
```

---

## 2. API Design

### GET /signals/history

**Filtros:** asset, type, status, data_inicio, data_fim, confidence_min, limit, offset

**Response:** Lista paginada de sinais históricos.

### GET /signals/history/{id}

**Response:** Detalhe completo de um sinal histórico.

### PUT /signals/{id}/status

**Body:** `{ "status": "disparado", "price_at_trigger": 97200.00 }`

### GET /signals/stats

**Response:** Agregações de performance.

---

## 3. Componentes Frontend

### SignalHistoryList

- Lista de sinais com paginação
- Filtros na lateral
- Colunas: Ativo, Tipo, Confidence, Target, Stop Loss, Status, PnL, Data, Ações
- **PnL:** Exibido com cor verde (positivo) ou vermelho (negativo)
- Exemplo: `+2.34%` em verde ou `-1.21%` em vermelho

### SignalHistoryCard

- Expande para mostrar detalhes
- Snapshot dos indicadores no momento
- Timeline de eventos
- **Seção PnL:** Mostra valor absoluto e percentual, cor conforme sinal

### SignalStats

- Cards com métricas: total, hit rate, por tipo, por status
- Gráfico simples de distribuição

---

## 4. Estados

| Estado | Descrição |
|--------|-----------|
| Loading | Buscando histórico |
| Empty | Nenhum sinal encontrado |
| Error | Erro ao buscar |
| Populated | Lista com dados |

---

## 5. Próximo Passo

Após DESIGN, passar para Alan approval.

---
