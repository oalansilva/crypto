# Proposal: Marcar Tasks Concluídas + Corrigir Portfolio KPIs

## 0) One-liner

Implementar toggle de tasks no Kanban (sync bidirecional tasks.md ↔ DB) E corrigir as seções Portfolio PnL e Drawdown do HomePage para exibir dados reais em vez de valores ilustrativos.

---

## 1) Context

### Problema 1 — Task Checkbox
- O sistema atual permite visualizar tasks (parse de `tasks.md`) mas não permite marcá-las como concluídas via interface.
- A única forma de marcar uma task como done é editando manualmente o arquivo `tasks.md`.
- O PO anterior especificou o mecanismo de sync mas não detalhhou completamente os fluxos de erro e rollback.

### Problema 2 — Portfolio KPIs (identificado como gap do PO anterior)
- As seções **Portfolio PnL (hoje)** e **Drawdown (30d)** no HomePage mostram "valor ilustrativo" hardcoded (`+2.34%` / `-6.10%`) em vez de dados reais.
- **Causa raiz:** O PO anterior não especificou corretamente de onde viriam os dados nem criou o endpoint necessário.
- **Impacto:** Alan não tem visibilidade real do desempenho diário do portfolio na tela inicial.

---

## 2) Goals

### Goal 1: Task Checkbox Toggle
Implementar fluxo completo para marcar uma task como concluída a partir da interface Kanban:
1. **UI:** Checkbox clicável na `TaskTree` do `KanbanPage.tsx`
2. **Endpoint:** `PATCH /workflow/work-items/{work_item_id}` com `state: "done"` — atualiza DB E persiste em `tasks.md`
3. **tasks.md persistence:** Função `toggle_task_checkbox()` que faz toggle do checkbox (`- [ ]` → `- [x]`) no arquivo

### Goal 2: Portfolio KPIs Reais
Criar pipeline de dados completo para as duas KpiCards do HomePage:
1. **Endpoint:** `GET /api/portfolio/kpi` que agrega dados da Binance
2. **Historical tracking:** Tabela `portfolio_snapshots` para cálculo de drawdown
3. **Frontend:** Substituir valores hardcoded por dados reais da API

---

## 3) In Scope

### Task Checkbox
- Backend: função `toggle_task_checkbox(change_id, task_code, checked)` em `change_tasks_service.py`
- Backend: endpoint `PATCH /workflow/work-items/{work_item_id}` que também persiste em `tasks.md`
- Frontend: `TaskTree` checkbox com `onClick` handler que chama a API
- Feedback visual: loading state + rollback on error + toast de erro

### Portfolio KPIs
- Backend: endpoint `GET /api/portfolio/kpi` 
- Backend: tabela `portfolio_snapshots` para histórico de drawdown
- Frontend: query + renderização dos valores reais no HomePage
- Remoção do badge "valor ilustrativo"

---

## 4) Out of Scope

- Criação de novas tasks via UI
- Marcar múltiplas tasks de uma vez (bulk)
- Notificações ao marcar task
- Histórico de state changes
- Backtest de portfolio (dados de backtest vs. dados reais de exchange)

---

## 5) User Stories

- Como **agente/operador**, quero marcar tasks como concluídas na interface do Kanban para manter o `tasks.md` atualizado sem precisar editar arquivo manualmente.
- Como **Alan**, quero ver o progresso real das tasks no board e o PnL real do meu portfolio na tela inicial.

---

## 6) API / Contracts

### `PATCH /workflow/work-items/{work_item_id}`

Atualiza work item na DB **e** persiste o estado do checkbox em `tasks.md`.

**Request body:**
```json
{ "state": "done" }  // ou { "state": "queued" } para desmarcar
```

**Response (200):**
```json
{
  "id": "uuid",
  "type": "task",
  "title": "1.1 Descrição da task",
  "state": "done",
  "description": "code:1.1",
  ...
}
```

**Errors:** 404 (not found), 422 (invalid state)

### `GET /api/portfolio/kpi`

Retorna KPIs agregados do portfolio.

**Response (200):**
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

**On Binance error (200 with error flag):**
```json
{
  "pnl_today_pct": null,
  "pnl_today_vs_btc_pct": null,
  "drawdown_30d_pct": null,
  "drawdown_peak_date": null,
  "btc_change_24h_pct": null,
  "_history_insufficient": true,
  "error": "Binance unavailable"
}
```

### Service function — toggle_task_checkbox

```python
def toggle_task_checkbox(change_id: str, task_code: str, checked: bool) -> bool:
    """
    Toggle a task checkbox in tasks.md.
    task_code: e.g. "1.1", "2.3"
    checked: True = - [x], False = - [ ]
    Returns True if updated, False if task not found.
    Raises: FileNotFoundError if tasks.md doesn't exist.
    """
```

---

## 7) Data Model

### tasks.md (source of truth — arquivo texto)
```
## 1. Remoção da superfície de UI
- [x] 1.1 Remover `/arbitrage` de ...
- [ ] 1.2 Remover item, ícone...
```

### wf_work_items (DB)
```
- state: WorkItemState.done (quando checked=True)
```

### portfolio_snapshots (DB — nova tabela)
```sql
CREATE TABLE portfolio_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_usd REAL NOT NULL,
    as_of DATE NOT NULL UNIQUE
);
```

---

## 8) Acceptance Criteria

### Task Checkbox
- [ ] Clicar no checkbox de uma task na interface atualiza `tasks.md` (`- [ ]` → `- [x]`)
- [ ] Clicar novamente reverte (`- [x]` → `- [ ]`)
- [ ] A mudança persiste no arquivo e é visível após reload
- [ ] Work item na DB também é atualizado com `state: done`
- [ ] Loading state visível durante a chamada de API
- [ ] Erro tratado graciosamente (checkbox reverte + toast)

### Portfolio KPIs
- [ ] `GET /api/portfolio/kpi` retorna dados reais (não hardcoded)
- [ ] HomePage Portfolio PnL mostra valor real (ou "não disponível" se Binance falhar)
- [ ] HomePage Drawdown mostra valor real ou "dados insuficientes (30d)"
- [ ] Badge "valor ilustrativo" removido das duas KpiCards
- [ ] Loading state (KpiSkeleton) visível enquanto query carrega
- [ ] Refresh da página mantém dados corretos

---

## 9) Test Plan

### Task Checkbox
- Testar `toggle_task_checkbox` com task existente e inexistente
- Testar que regex de parsing mantém a estrutura do markdown intacta
- Testar rollback de transação se file write falhar
- **Smoke:** Kanban → selecionar card → clicar checkbox → verificar tasks.md

### Portfolio KPIs  
- **Smoke:** HomePage → verificar Portfolio PnL mostra valor numérico (não `+2.34%`)
- **Smoke:** HomePage → Drawdown mostra valor real ou "dados insuficientes"
- Error case: credentials inválidos → "não disponível" graceful
