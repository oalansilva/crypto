## 1. Frontend surface removal

- [x] 1.1 Remover item Backfill e título de página em `AppNav.tsx` (e import `Play` se ficar órfão)
- [x] 1.2 Remover rota `/admin/backfill` e import de `AdminBackfillPage` em `App.tsx`
- [x] 1.3 Remover `frontend/src/pages/AdminBackfillPage.tsx`
- [x] 1.4 Atualizar E2E `admin-menu-visibility.spec.ts` para não exigir Backfill

## 2. Backend admin API removal

- [x] 2.1 Remover include do router `admin_backfill` em `main.py`
- [x] 2.2 Remover `backend/app/routes/admin_backfill.py` e `backend/app/schemas/backfill.py`
- [x] 2.3 Remover `backend/tests/unit/test_admin_backfill_routes.py`
- [x] 2.4 Confirmar que `ohlcv_backfill_service`, scheduler em `main.py` e `ensure_history_job` em `api.py` permanecem

## 3. Validation

- [x] 3.1 Rodar testes unitários focados do serviço de backfill e regressão de candles/full history
- [x] 3.2 Rodar build frontend e E2E de menu admin (ou suíte visual quando aplicável)
- [x] 3.3 Validar OpenSpec da change (`openspec validate card-353-remove-admin-backfill`)
