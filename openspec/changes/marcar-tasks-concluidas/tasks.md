# Tasks: Marcar Tasks Concluídas na Interface + Portfolio KPIs

## 1. Backend — toggle_task_checkbox service

- [x] 1.1 Adicionar `toggle_task_checkbox(change_id, task_code, checked)` em `backend/app/services/change_tasks_service.py`
- [x] 1.2 Usar regex para localizar linha por task code em `tasks.md` e substituir checkbox (`- [ ]` ↔ `- [x]`)
- [x] 1.3 Preservar indentação original da linha durante substituição
- [x] 1.4 Retornar `True` se atualizado, `False` se task não encontrada
- [x] 1.5 Tratar arquivo não encontrado gracefulmente (retornar False, não exception)

## 2. Backend — PATCH work-items com persistência em tasks.md

- [ ] 2.1 Modificar `update_task` em `backend/app/routes/workflow.py` para chamar `toggle_task_checkbox` quando `state` muda para `done` ou `queued`
- [ ] 2.2 Extrair `task_code` do campo `description` (formato: `code:1.1` ou `code: 1.1`)
- [ ] 2.3 Obter `change_id` via lookup do `change_pk` do work item
- [ ] 2.4 Garantir que transação só commita se ambas operações (DB + file) succeed; se file write falhar, fazer rollback da DB
- [ ] 2.5 Testar: state=done → checkbox vira [x]; state=queued → checkbox volta para [ ]

## 3. Frontend — TaskTree checkbox interativo

- [ ] 3.1 Adicionar prop `onToggle?: (taskCode: string, workItemId: string, checked: boolean) => void` em `TaskTree`
- [ ] 3.2 Substituir checkbox passivo (só leitura) por `<input type="checkbox">` com handler
- [ ] 3.3 Handler: extrair `work_item_id` dos dados do work item, chamar `PATCH /workflow/work-items/{work_item_id}` com `{ state: checked ? "done" : "queued" }`
- [ ] 3.4 Mapear `task_code → work_item_id` usando dados já presentes nos work items (description contém `code:1.x`)
- [ ] 3.5 Mostrar loading state (checkbox desabilitado + spinner) durante chamada API
- [ ] 3.6 Em caso de erro: reverter checkbox visualmente, mostrar toast de erro via `toast()` do Shadcn
- [ ] 3.7 Invalidar `tasksQuery` e `workItemsQuery` do TanStack Query após sucesso
- [ ] 3.8 Não alterar aparência de seções/títulos — só os checkboxes das tasks individuais

## 4. Frontend — Resolver task_code → work_item_id

- [ ] 4.1 Work items já contêm `description` com formato `code:1.1` — usar regex para extrair
- [ ] 4.2 Criar utilitário `extractTaskCode(description: string): string | null` para parsing
- [ ] 4.3 Passar `workItemId` junto com cada task na renderização do TaskTree

## 5. Backend — GET /api/portfolio/kpi

- [ ] 5.1 Criar `backend/app/routes/portfolio.py` com router `APIRouter(prefix="/api/portfolio", tags=["portfolio"])`
- [ ] 5.2 Registrar o router em `backend/app/api.py` (importar e incluir no `APIRouter`)
- [ ] 5.3 Endpoint `GET /api/portfolio/kpi` — retornar:
  ```json
  {
    "pnl_today_pct": 1.23,
    "pnl_today_vs_btc_pct": -0.45,
    "drawdown_30d_pct": -3.45,
    "drawdown_peak_date": "2026-02-20",
    "btc_change_24h_pct": 1.68,
    "_history_insufficient": false
  }
  ```
- [ ] 5.4 Calcular `pnl_today_pct`:
  - Chamar `fetch_spot_balances_snapshot()` (já existente em `binance_spot.py`)
  - Agregar `sum(pnl_usd) / total_usd * 100` se `total_usd > 0`
  - Se `total_usd` for 0 ou indisponível, retornar `null`
- [ ] 5.5 Calcular `btc_change_24h_pct`:
  - Chamar `/api/market/prices?symbols=BTCUSDT`
  - Extrair `prices[0].change_24h_pct`
- [ ] 5.6 Calcular `pnl_today_vs_btc_pct`:
  - `pnl_today_pct - btc_change_24h_pct` (pode ser null se pnl_today_pct for null)
- [ ] 5.7 Calcular `drawdown_30d_pct`:
  - **Opção A (preferred):** Tabela `portfolio_snapshots` com coluna `total_usd` e `as_of` (date)
    - Criar tabela `portfolio_snapshots(id, total_usd, as_of)` em `workflow.db` ou `backtest.db`
    - Query: `SELECT peak_value FROM portfolio_snapshots WHERE as_of >= date('now', '-30 days') ORDER BY total_usd DESC LIMIT 1`
    - Drawdown = `(peak_value - current_total_usd) / peak_value * 100`
  - **Opção B (fallback):** Se não houver dados históricos suficientes (< 2 snapshots), retornar `_history_insufficient: true` e `drawdown_30d_pct: null`
- [ ] 5.8 Tratar erros:
  - Se Binance API falhar: retornar `{ "error": "Binance unavailable", ... }` com status 200 e valores nulos
  - Se qualquer parte falhar parcialmente, retornar o que for possível + `_partial: true`

## 6. Frontend — HomePage KPI Grid com dados reais

- [ ] 6.1 Adicionar query `portfolioKpiQuery` em `HomePage.tsx`:
  ```ts
  const portfolioKpiQuery = useQuery<PortfolioKpiResponse>({
    queryKey: ['portfolio-kpi'],
    queryFn: () => fetchJson('/api/portfolio/kpi'),
    refetchInterval: 5 * 60 * 1000, // refresh every 5 min
  })
  ```
- [ ] 6.2 Definir tipo `PortfolioKpiResponse` com todos os campos do endpoint
- [ ] 6.3 Substituir valores hardcoded na KpiCard "Portfolio PnL (hoje)":
  - Mostrar `pnl_today_pct` formatado com `formatPercent()` (existente em HomePage)
  - Mostrar `pnl_today_vs_btc_pct` como "vs. BTC: {value}%"
  - Se `pnl_today_pct` for `null`: mostrar "não disponível" e cor de erro
- [ ] 6.4 Substituir valores hardcoded na KpiCard "Drawdown (30d)":
  - Mostrar `drawdown_30d_pct` formatado com `%` (negativo)
  - Mostrar `drawdown_peak_date` como "Pico: {date}"
  - Se `_history_insufficient: true`: mostrar "dados insuficientes (30d)"
  - Se `drawdown_30d_pct` for `null` e não for insuficiente: mostrar "não disponível"
- [ ] 6.5 Remover `label="valor ilustrativo"` das duas KpiCards (substituir por loading state ou valor real)
- [ ] 6.6 Loading state: mostrar `<KpiSkeleton />` enquanto query carrega
- [ ] 6.7 Manter as demais KpiCards (Melhor estratégia, Data freshness) funcionando como antes
- [ ] 6.8 Testar que刷新 da página mantém valores corretos

## 7. Testes e validação

- [ ] 7.1 Testar `toggle_task_checkbox`: task existente → checkbox toggla; task inexistente → retorna False
- [ ] 7.2 Testar que regex preserva indentação ao substituir checkbox
- [ ] 7.3 Smoke test: abrir Kanban → clicar checkbox → verificar tasks.md atualizado
- [ ] 7.4 Smoke test: HomePage → Portfolio PnL mostra valor numérico real (não hardcoded)
- [ ] 7.5 Smoke test: HomePage → Drawdown mostra valor real ou "dados insuficientes"
- [ ] 7.6 Erro handling: com Binance credentials inválidos, HomePage mostra "não disponível" gracefulmente
