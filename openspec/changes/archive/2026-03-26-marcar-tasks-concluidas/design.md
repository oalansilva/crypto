# Design: Marcar Tasks Concluídas + Portfolio KPIs

## Parte 1: Task Checkbox Toggle

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  KanbanPage.tsx                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  TaskTree (checkbox interativo)                     │   │
│  │  onToggle(taskCode, workItemId, checked)            │   │
│  └──────────────┬──────────────────────────────────────┘   │
└─────────────────┼──────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  PATCH /workflow/work-items/{work_item_id}                  │
│  Body: { state: "done" | "queued" }                        │
│                                                             │
│  workflow.py → update_task()                               │
│    1. Update wf_work_items DB (state)                       │
│    2. Call toggle_task_checkbox(change_id, code, checked)  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  change_tasks_service.py                                    │
│  toggle_task_checkbox(change_id, task_code, checked)        │
│    → Parse tasks.md                                         │
│    → Locate line by task_code regex                         │
│    → Replace [ ] ↔ [x] (preserve indentation)              │
│    → Write back to tasks.md                                 │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. User clicks checkbox in TaskTree
2. Frontend extracts `task_code` from work item's `description` (format: `code:1.1`)
3. Frontend calls `PATCH /workflow/work-items/{work_item_id}` with `{ state: "done" }` or `{ state: "queued" }`
4. Backend updates DB: `wf_work_items.state = done/queued`
5. Backend extracts `task_code` from `description` (regex: `/^code:\s*(\d+(?:\.\d+)+)$/`)
6. Backend calls `toggle_task_checkbox(change_id, task_code, True/False)`
7. Service locates line in `tasks.md` by task code (regex: `/^\s*-\s+\[\s?[xX]\s?\]\s+\d+\.\d+\s/` against `/^\s*-\s+\[\s?\s?\]\s+\d+\.\d+\s/`)
8. Service replaces `- [ ]` → `- [x]` (or vice-versa), preserving leading whitespace
9. Service writes file back
10. Success response to frontend
11. Frontend invalidates `tasksQuery` and `workItemsQuery`

### task_code Extraction

The task code (e.g., `1.1`) is stored in `wf_work_items.description` as `code:1.1` during sync.
Frontend uses regex `/^code:\s*(\d+(?:\.\d+)+)$/` to extract from description string.

### File Write Atomicity

- Read file → modify in memory → write back
- If write fails: rollback DB transaction (already done by SQLAlchemy session rollback)
- Acceptable for MVP (low concurrency on tasks.md files)

### Checkbox State in TaskTree

- Current state: parsed from tasks.md via `/coordination/changes/{id}/tasks` API
- After toggle: optimistic UI update (checkbox muda visualmente imediatamente)
- On API error: reverter para estado anterior + mostrar toast de erro

---

## Parte 2: Portfolio KPIs (HomePage)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  HomePage.tsx                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  useQuery(['portfolio-kpi'], fetchPortfolioKpi)     │   │
│  └──────────────┬──────────────────────────────────────┘   │
└─────────────────┼──────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  GET /api/portfolio/kpi                                     │
│  PortfolioRouter → get_portfolio_kpi()                      │
│    ├─ fetch_spot_balances_snapshot() [binance_spot]       │
│    │    → returns total_usd, balances[].pnl_usd, etc.    │
│    ├─ fetch BTC 24h change from /api/market/prices         │
│    └─ Query portfolio_snapshots for drawdown               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Response:                                                  │
│  {                                                          │
│    pnl_today_pct: float,        // aggregate PnL %         │
│    pnl_today_vs_btc_pct: float, // PnL vs BTC 24h         │
│    drawdown_30d_pct: float,     // drawdown from peak      │
│    drawdown_peak_date: string,   // ISO date of peak        │
│    btc_change_24h_pct: float,   // BTC 24h change          │
│    _history_insufficient: bool  // true if < 2 snapshots   │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

### Data Sources

| KPI | Source | Calculation |
|-----|--------|-------------|
| `pnl_today_pct` | `fetch_spot_balances_snapshot()` | `Σ(pnl_usd) / total_usd * 100` |
| `btc_change_24h_pct` | `/api/market/prices?symbols=BTCUSDT` | `prices[0].change_24h_pct` |
| `pnl_today_vs_btc_pct` | derived | `pnl_today_pct - btc_change_24h_pct` |
| `drawdown_30d_pct` | `portfolio_snapshots` table | `(peak_value - current) / peak_value * 100` |
| `drawdown_peak_date` | `portfolio_snapshots` table | date of peak value in 30d window |

### portfolio_snapshots Table

```sql
CREATE TABLE portfolio_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_usd REAL NOT NULL,
    as_of DATE NOT NULL UNIQUE
);
```

- Snapshot diario: job que roda todo dia às 23:59 UTC (ou sob demanda)
- Para MVP: endpoint `POST /api/portfolio/snapshots` para forçar snapshot manual
- A捷: criar script `workers/portfolio_snapshot.py` rodável via cron

### Error Handling

- Binance credentials missing → return `{ "error": "Binance unavailable" }` with null values
- Partial failure → return available data + `_partial: true`
- Insufficient history → return `_history_insufficient: true` + null for drawdown fields

### HomePage KPI Grid Changes

| KpiCard | Before | After |
|---------|--------|-------|
| Portfolio PnL (hoje) | hardcoded `+2.34%` / `vs. BTC: +0.40%` | Real from API: `pnl_today_pct` / `pnl_today_vs_btc_pct` |
| Drawdown (30d) | hardcoded `-6.10%` / `Pico: 12 Fev` | Real from API: `drawdown_30d_pct` / `drawdown_peak_date` |

Both cards: remove `label="valor ilustrativo"`. Show `KpiSkeleton` while loading.

---

## File Changes Summary

### Task Checkbox Toggle

| File | Change |
|------|--------|
| `backend/app/services/change_tasks_service.py` | Add `toggle_task_checkbox()` function |
| `backend/app/routes/workflow.py` | Update `update_task()` to call `toggle_task_checkbox` after DB update |
| `frontend/src/components/TaskTree.tsx` | Add `onToggle` prop; make checkbox interactive |
| `frontend/src/pages/KanbanPage.tsx` | Pass `onToggle` handler with API call; handle loading/error |

### Portfolio KPIs

| File | Change |
|------|--------|
| `backend/app/routes/portfolio.py` | **NEW** — `GET /api/portfolio/kpi` endpoint |
| `backend/app/api.py` | Import and register `portfolio_router` |
| `backend/app/services/binance_spot.py` | (already exists, reuse `fetch_spot_balances_snapshot`) |
| `workers/portfolio_snapshot.py` | **NEW** — daily snapshot job script |
| `backend/workflow.db` | Add `portfolio_snapshots` table (migration) |
| `frontend/src/pages/HomePage.tsx` | Add `portfolioKpiQuery`; replace hardcoded values |
