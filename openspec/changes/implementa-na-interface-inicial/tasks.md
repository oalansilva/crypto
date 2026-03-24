## Escopo do Card #48 — Implementar interface inicial com dados reais

> **Override de constraint (Alan, 2026-03-24):** Alan rejeitou a remoção das seções "Runs recentes" e "Market watch". O objetivo é ter dados REAIS, não mock. Novos endpoints backend são necessários para viabilizar essas seções.

---

### Contexto da exploração (PO)

Mock data confirmado em `frontend/src/pages/HomePage.tsx`:

| Seção | Dado mock | Endpoint real disponível | Ação |
|---|---|---|---|
| KPI — Portfolio PnL | `+2.34%` hardcoded | Nenhum | Manter snapshot com label "valor ilustrativo" |
| KPI — Drawdown (30d) | `-6.10%` hardcoded | Nenhum | Manter snapshot com label "valor ilustrativo" |
| KPI — Melhor estratégia | `MA Crossover / +8.9%` hardcoded | `/api/favorites` (tem strategy_name, metrics) | Substituir por favorito mais recente |
| KPI — Data freshness | `200 candles` hardcoded | `/api/external/binance/spot/balances` | Substituir por dado real |
| Foco de hoje | 3 items hardcoded | `/workflow/kanban/changes` | Substituir por mudanças ativas |
| Runs recentes | tabela inteira hardcoded | **NENHUM** — PRECISA CRIAR | Restaurar seção com endpoint real |
| Market watch | BTC/ETH/SOL hardcoded | **NENHUM** — PRECISA CRIAR | Restaurar seção com endpoint real |

---

## Tarefas de DEV

### 1. KPI Grid — wired com endpoints reais + fallback

- [ ] 1.1 **Data freshness**: usar `/api/external/binance/spot/balances` → `updated_at` do snapshot mais recente
- [ ] 1.2 **Melhor estratégia (7d)**: buscar `/api/favorites` → mostrar strategy com melhor ROI ou mais recente; fallback: "Nenhuma estratégia favoritada"
- [ ] 1.3 **Portfolio PnL** e **Drawdown**: sem endpoint dedicado → manter como snapshot hardcoded com label VISÍVEL "valor ilustrativo"
- [ ] 1.4 Garantir estados: loading skeleton, error fallback ("não disponível"), empty state

### 2. Foco de hoje → "Mudanças ativas"

- [ ] 2.1 Buscar `/workflow/kanban/changes` (projeto ativo)
- [ ] 2.2 Mostrar até 3 mudanças mais recentes: título, status badge, data
- [ ] 2.3 Link "Ver tudo" → `/kanban`
- [ ] 2.4 Empty state: "Nenhuma mudança ativa no momento"

### 3. Runs recentes — REATIVADO (Alan, 2026-03-24)

**Requer novo endpoint:**

```
GET /api/lab/runs?limit=5

Query params:
  - limit (int, default=5, max=20): número de runs mais recentes a retornar

Response 200:
{
  "runs": [
    {
      "run_id":      string,   // ex: "run-abc123"
      "status":      string,   // "pending" | "running" | "completed" | "failed"
      "step":        string?,  // etapa atual (ex: "execution", "cp8_synthesis")
      "created_at_ms": int,   // timestamp ms de criação
      "updated_at_ms": int,   // timestamp ms da última atualização
      "viewer_url":  string,  // URL do frontend para abrir o run
    },
    ...
  ]
}
```

**Constraint de implementação:**
- Listar apenas os arquivos `*.json` mais recentes em `backend/logs/lab_runs/` via `_runs_dir()` (já existente em `lab.py`)
- **NÃO fazer scan histórico completo** — ordenar por `created_at_ms` descending e cortar em `limit`
- Não expor `trace_events`, `step_logs`, `outputs`, `budget`, `backtest`, `diagnostic` neste endpoint (dados pesados)
- Se `_runs_dir()` não existir ou estiver vazio: retornar `{"runs": []}`

**Tarefas DEV:**
- [ ] 3.1 Criar `GET /api/lab/runs` em `backend/app/routes/lab.py` (lista recente de runs)
- [ ] 3.2 Restaurar seção "Runs recentes" no `HomePage.tsx`, consumindo `/api/lab/runs?limit=5`
- [ ] 3.3 Mostrar: nome do run (ou run_id truncado), status badge, data/hora relativa
- [ ] 3.4 Cada row é um link para `/lab/runs/{run_id}` (frontend route já existe)
- [ ] 3.5 Loading/error/empty states: skeleton rows, erro "não disponível", empty "Nenhum run ainda"

### 4. Market watch — REATIVADO (Alan, 2026-03-24)

**Requer novo endpoint:**

```
GET /api/market/prices?symbols=BTCUSDT,ETHUSDT,SOLUSDT

Query params:
  - symbols (string, optional): símbolos separados por vírgula (default: "BTCUSDT,ETHUSDT,SOLUSDT")

Response 200:
{
  "prices": [
    {
      "symbol":   string,  // ex: "BTCUSDT"
      "price":    string,  // ex: "67432.50" (precisão completa da Binance)
      "change_24h_pct": string?  // ex: "+2.34" ou null se indisponível
    },
    ...
  ],
  "fetched_at": string  // ISO timestamp da consulta
}
```

**Constraint de implementação:**
- Dados: Binance public API — `GET https://api.binance.com/api/v3/ticker/24hr?symbols=[...]`
  - Sem API key necessária (public endpoint)
  - Symbols devem ser URL-encoded: `["BTCUSDT","ETHUSDT","SOLUSDT"]` → `["BTCUSDT","ETHUSDT","SOLUSDT"]` no query param
- **Cache**: cache em memória (dicionário simples) com TTL de 30 segundos para evitar rate limit
  - Se cache hit e não expirou: retornar do cache
  - Se cache miss ou expirado: fazer nova requisição à Binance
- Se Binance API falhar: retornar `{"prices": [], "fetched_at": null}` com status 200 (graceful degradation)
- Timeout na chamada Binance: 5 segundos

**Tarefas DEV:**
- [ ] 4.1 Criar `GET /api/market/prices` em `backend/app/routes/` (novo arquivo `market_prices.py`)
- [ ] 4.2 Registrar o router em `backend/app/main.py` com prefixo `/api/market`
- [ ] 4.3 Restaurar seção "Market watch" no `HomePage.tsx`, consumindo `/api/market/prices`
- [ ] 4.4 Mostrar: símbolo, preço atual, variação 24h (colorido: verde/vermelho)
- [ ] 4.5 Loading/error/empty states: skeleton, erro "preços indisponíveis", empty "Nenhum par monitorado"

### 5. Hero, Quick Actions, Atalhos — sem alterações

- [ ] 5.1 Já funcionais — não precisam de mudança

### 6. Estados de loading/error em todas as seções

- [ ] 6.1 Cada seção assíncrona: skeleton/loading, error, empty state
- [ ] 6.2 Nenhuma área deve ficar em branco

### 7. Testes e regressão

- [ ] 7.1 Testes unitários para componentes que consomem endpoints
- [ ] 7.2 Playwright E2E: HomePage desktop e mobile com fallback visual
- [ ] 7.3 Verificar que labels "ilustrativo"/"snapshot" estão visíveis nas seções sem dado real

---

## Out of scope

- Criar endpoints para Portfolio PnL ou Drawdown (sem fonte de dados identificada)
- Reformulação visual do layout
- Alterações em outras páginas
- Cache persistente (Redis/DB) para prices — usar cache em memória com TTL 30s
- Historical scan de runs (só os N mais recentes por created_at_ms)

## Dependências

- `GET /api/lab/runs` precisa ser criado em `lab.py` (este card)
- `GET /api/market/prices` precisa ser criado como novo route (este card)
- Ambos endpoints devem existir ANTES da iteração de frontend (seções 3.2 e 4.3)
