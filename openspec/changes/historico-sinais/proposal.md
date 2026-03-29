---
spec: openspec.v1
id: historico-sinais
title: Histórico de Sinais de Trading
card: "#57"
change_id: historico-sinais
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Proposal: Histórico de Sinais de Trading

**Card:** #57  
**change_id:** `historico-sinais`  
**Estágio:** PO  
**User Story:** Como trader, quero ver o histórico de sinais gerados para analisar padrões e desempenho passado.

---

## 1. User Story & Objetivos

**User Story:**
> Como trader, quero ver o histórico de sinais gerados para analisar padrões e desempenho passado.

**Critérios de aceite:**
- Lista de todos os sinais gerados com timestamp
- Filtros por ativo, tipo de sinal, período e confidence
- Detalhe de cada sinal mostrando indicadores no momento da geração
- Status do sinal (ativo, disparado, expirado)
- Métricas básicas de performance (sinais acertados vs errados)

**Decisão-chave:** O histórico depende dos sinais do Card #53 para existir, mas é independente para desenvolvimento.

---

## 2. Conexões com Outros Cards

### Este card depende de:
- **Card #53** (sinais-de-trading-buy-sell-hold) — fornece os sinais que serão armazenados no histórico

### Outros cards dependem deste:
- **Card #56** (ai-dashboard-insights) — consome histórico para exibir métricas e insights

### Ordem de execução recomendada:
1. Card #53 deve existir (ou pelo menos a estrutura) para que #57 possa consumir
2. #57 pode ser desenvolvido em paralelo com #53 se API for definida
3. #56 consome #57 após ambos existirem

---

## 3. Decisões Definidas

| Item | Decisão |
|------|---------|
| Retenção de dados | 90 dias (sinais mais antigos são arquivados) |
| Status de sinal | ativo, disparado, expirado, cancelado |
| Filtros disponíveis | ativo, tipo, data_inicio, data_fim, confidence_min |
| Dados por sinal | id, asset, tipo, confidence, target, stop_loss, timestamp, status, indicadores |
| Infraestrutura | $0 — PostgreSQL no VPS (já existente) |

---

## 4. Escopo

### Dentro do escopo
- [ ] Tabela de histórico de sinais no PostgreSQL
- [ ] CRUD de sinais históricos
- [ ] Endpoint GET /signals/history
- [ ] Filtros por ativo, tipo, período, confidence
- [ ] Status tracking (ativo → disparado/expirado/cancelado)
- [ ] Armazenamento dos indicadores no momento da geração

### Fora do escopo
- [ ] Visualização em gráficos (Card #56)
- [ ] Métricas avançadas de performance (Card #56)
- [ ] Backtesting automatizado
- [ ] Alertas ou notificações

---

## 5. Arquitetura

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │
│  (React)     │◀────│  FastAPI     │◀────│  (history)  │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                     ┌─────▼─────┐
                     │   Cache   │
                     └───────────┘
```

**Stack:**
- Frontend: React + TypeScript (existing codebase)
- Backend: FastAPI (existing service on :8003)
- Database: PostgreSQL on VPS

---

## 6. API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/signals/history` | Lista histórico de sinais com filtros |
| GET | `/signals/history/{id}` | Detalhe de um sinal histórico |
| PUT | `/signals/{id}/status` | Atualiza status de um sinal |
| GET | `/signals/stats` | Métricas básicas de performance |

**GET /signals/history — Query params:**
- `asset`: string ex: BTCUSDT (opcional)
- `type`: BUY | SELL | HOLD (opcional)
- `status`: ativo | disparado | expirado | cancelado (opcional)
- `data_inicio`: ISO date (opcional)
- `data_fim`: ISO date (opcional)
- `confidence_min`: int 0–100 (opcional)
- `limit`: int (default 50, max 200)
- `offset`: int (default 0)

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
      "status": "disparado",
      "indicators_snapshot": { "RSI": 35, "MACD": "bullish", "BB_position": 0.2 },
      "created_at": "2026-03-26T12:00:00Z",
      "triggered_at": "2026-03-26T14:30:00Z",
      "price_at_trigger": 97200.00
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

**GET /signals/stats — Response:**
```json
{
  "total_signals": 150,
  "by_type": { "BUY": 80, "SELL": 50, "HOLD": 20 },
  "by_status": { "disparado": 60, "expirado": 30, "ativo": 10, "cancelado": 5 },
  "hit_rate": 0.72,
  "avg_confidence": 78.5
}
```

---

## 7. Custos

| Recurso | Custo |
|---------|-------|
| PostgreSQL (VPS) | $0 (já existente) |
| Backend FastAPI | $0 (já existente) |
| **Total** | **$0/mês** |

---

## 8. Riscos

| Risco | Mitigação |
|-------|-----------|
| Volume grande de dados | Paginação + índices no banco |
| Dados antigos ocupam espaço | Archiving automático após 90 dias |

---

## 9. Próximo Passo

Passar para DESIGN para especificação de UI/UX do histórico.

---
