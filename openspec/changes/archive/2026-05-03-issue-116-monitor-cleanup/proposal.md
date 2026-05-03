## Why

O card 116 pede remover itens destacados no print da tela Monitor. Os elementos marcados adicionam ruído visual ou duplicam informação para o usuário comum.

## What Changes

- Remover o badge `Binance system` do topo.
- Remover o indicador `Binance · live` da barra do Monitor.
- Remover controles de ordenação `Risco` e `Par` da barra de filtros.
- Remover a coluna final duplicada de `Status`.
- Remover o botão de mais ações (`...`) das linhas do Monitor.

## Capabilities

### New Capabilities
- `issue-116-monitor-cleanup`: limpeza visual da tela Monitor conforme card 116.

### Modified Capabilities

## Impact

- Frontend: `frontend/src/components/AppNav.tsx`.
- Frontend: `frontend/src/components/monitor/MonitorStatusTab.tsx`.
- E2E: `frontend/tests/e2e/monitor-card-mode-and-portfolio.spec.ts`.
- Sem impacto em API, banco ou permissões.
