## Why

As telas admin `/signals`, `/signals/history` e `/supply-distribution` foram descontinuadas em produção. Manter rotas, navegação e APIs exclusivas aumenta manutenção e confunde operadores, sem valor de produto.

## What Changes

- **BREAKING**: Remover rotas frontend `/signals`, `/signals/history` e `/supply-distribution`, links de navegação e páginas/componentes exclusivos.
- **BREAKING**: Remover API `/api/signals` e o endpoint `/api/onchain/glassnode/{asset}/supply-distribution`.
- Remover testes E2E/unitários exclusivos dessas superfícies e atualizar testes de navegação admin.
- Preservar Monitor/Favoritos/Combos (`signal_history` de oportunidades), Glassnode compartilhado e demais endpoints onchain ativos (mining/exchange-flows).
- Atualizar spec `backend` para deixar de exigir o endpoint de supply distribution.

## Capabilities

### New Capabilities

- `discontinued-admin-surfaces-removal`: Contrato de remoção das três superfícies admin descontinuadas (UI + APIs exclusivas) sem regressão nos fluxos ativos.

### Modified Capabilities

- `backend`: Remover o requirement que obriga o endpoint de supply distribution.

## Impact

- Frontend: `App.tsx`, `AppNav.tsx`, páginas Signals/Supply, `components/signals/**`, E2E `supply-distribution` e `admin-menu-visibility`.
- Backend: `routes/signals.py`, registro/middleware em `main.py`, endpoint e schemas de supply em `onchain_metrics.py`, serviço `onchain_supply_distribution_service.py`, testes associados.
- OpenSpec: delta em `backend` + nova capability de remoção.
- Fora de escopo desta change: purge completo de `signal_monitor`/AI dashboard/`SignalHistory` DB (ainda referenciados por runtime/AI); limpeza residual pode ser card futuro.
