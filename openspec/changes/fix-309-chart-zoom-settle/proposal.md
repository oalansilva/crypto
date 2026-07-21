## Why

O zoom fantasma do gráfico do Monitor voltou após o fix parcial (#311): viewport ainda era reaplicado quando a contagem de velas mudava, e a roda do mouse no shell (painel/transparência) também dava zoom.

## What Changes

- Aplicar range default uma vez por `viewportResetKey` quando `viewportReady` for true.
- Não re-snap por mudança intermediária de contagem de candles.
- Listener de wheel só na área do gráfico (`chartRef`), não no shell inteiro.

## Capabilities

### New Capabilities
- (nenhuma)

### Modified Capabilities
- `chart-visualization`: viewport settled + wheel scoped ao canvas do gráfico.

## Impact

- `StrategyChartSurface`, `ChartModal`
- Testes de contrato / E2E de zoom
