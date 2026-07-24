## Why

No Monitor, **Ver Trades** abre o gráfico e, quando a lista de trades carrega, o gráfico some. O trader perde o contexto de preço exatamente quando precisa cruzar trades com o candle.

## What Changes

- Garantir que, no `viewMode=trades`, o gráfico mantenha altura estável e permaneça visível após o carregamento dos trades.
- Ajustar o layout do modal para o gráfico não competir em flex com a tabela (trades com scroll próprio).
- Cobrir com E2E: gráfico + trades visíveis após o load.

## Capabilities

### New Capabilities

- `monitor-trades-chart-layout`: contrato de UX do modal Ver Trades — gráfico permanente + lista de trades sem colapso.

### Modified Capabilities

- (nenhum)

## Impact

- `frontend/src/components/monitor/ChartModal.tsx`
- `frontend/src/components/charts/StrategyChartSurface.tsx`
- testes E2E do Monitor (Ver Trades)
