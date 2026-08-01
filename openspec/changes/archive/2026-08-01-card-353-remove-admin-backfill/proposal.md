## Why

A superfície admin `/admin/backfill` não faz mais parte do fluxo operacional desejado do MVP e adiciona risco de uso manual desnecessário. Alan pediu a remoção dessa opção, preservando a ingestão histórica usada por candles/favorites.

## What Changes

- Remove a página, rota SPA e item de navegação **Backfill** (`/admin/backfill`).
- Remove a API admin dedicada `/api/admin/backfill/*` e schemas exclusivos dessa superfície.
- Remove/ajusta testes que cobrem apenas a superfície admin.
- **Preserva** `ohlcv_backfill_service`, store, scheduler opcional e o agendamento via `/market/candles?full_history`.

## Capabilities

### New Capabilities

- `admin-backfill-surface-removal`: remoção da superfície admin de backfill sem degradar ingestão histórica programática.

### Modified Capabilities

- `frontend-ux`: navegação admin deixa de listar Backfill; common/admin scenarios atualizados.

## Impact

- Frontend: `AppNav`, `App.tsx`, `AdminBackfillPage.tsx`, E2E `admin-menu-visibility`.
- Backend: `admin_backfill` router, `schemas/backfill.py`, `main.py` include, testes unitários admin.
- Sem impacto esperado em market candles, favorites full history, writer canônico ou flags `BACKFILL_SCHEDULER_*`.
- UI impact: affected (remoção de item de nav e rota admin). Autorização de implementação: pedido explícito de Alan (`implemente`).
