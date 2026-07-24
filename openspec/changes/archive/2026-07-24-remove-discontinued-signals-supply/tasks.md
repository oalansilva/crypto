## 1. Frontend removal

- [x] 1.1 Remover rotas e imports de `/signals`, `/signals/history` e `/supply-distribution` em `App.tsx`
- [x] 1.2 Remover links e títulos dessas telas em `AppNav.tsx` (e ícones órfãos se ficarem sem uso)
- [x] 1.3 Apagar páginas `SignalsPage`, `SignalsHistoryPage`, `SupplyDistributionPage`
- [x] 1.4 Apagar `components/signals/**` e `types/signals.ts` se exclusivos dessas telas
- [x] 1.5 Atualizar/remover E2E `supply-distribution.spec.ts` e ajustar `admin-menu-visibility.spec.ts`

## 2. Backend removal

- [x] 2.1 Remover router `/api/signals` (`routes/signals.py`) e registro/middleware em `main.py`
- [x] 2.2 Remover endpoint supply-distribution e schemas exclusivos em `onchain_metrics.py`
- [x] 2.3 Apagar `onchain_supply_distribution_service.py`
- [x] 2.4 Remover/ajustar testes unitários/integração exclusivos (`test_signals_endpoints`, supply distribution route/service)

## 3. Preserve and validate

- [x] 3.1 Confirmar preservação de Monitor/Favoritos/Combo `signal_history` (`SignalHistoryPanel`, `lib/signalHistory.ts`, ChartModal)
- [x] 3.2 Confirmar preservação de `glassnode_service` + mining/exchange-flows
- [x] 3.3 Rodar testes focados backend + build frontend
- [x] 3.4 Atualizar baselines Playwright visual se a nav mudar de forma intencional
