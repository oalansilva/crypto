## 1. Sync e contrato de estado

- [x] 1.1 Ajustar `loadMonitorSyncedTrades` para preferir cache do Monitor (`refresh=false`) e retornar `signal_history` + status (`ok`/`timeout`/`missing`/`empty`).
- [x] 1.2 Propagar `signal_history` e `monitor_sync_status` no navigate state de Favoritos → ComboResults.

## 2. UI de últimos sinais

- [x] 2.1 Extrair/reutilizar painel “Histórico de sinais” (lista últimos N, Compra/Venda, empty/erro) compartilhável entre ChartModal e ComboResults.
- [x] 2.2 Renderizar o painel em `ComboResultsPage` a partir de `signal_history`, com empty/erro explícitos.
- [x] 2.3 Preferir markers de `signal_history` no gráfico de Favoritos (paridade visual com Monitor).

## 3. Validação

- [x] 3.1 Testes frontend/E2E: Monitor tem sinais → Favoritos mostra os mesmos; timeout → estado explícito.
- [x] 3.2 Playwright visual Favoritos com últimos sinais (atualizar baseline se mudança intencional).
- [x] 3.3 Validar OpenSpec da change, build e runtime DEV; registrar evidências no card.
