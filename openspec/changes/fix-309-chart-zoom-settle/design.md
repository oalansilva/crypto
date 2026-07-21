## Context

Fix #311 removeu zoom triplo e tentou preservar range, mas ainda reaplicava default quando `candlestickData.length` mudava (fetch → merge analysis) e o wheel capturava o shell inteiro.

## Goals / Non-Goals

**Goals:**
- Um único apply de viewport default por symbol/timeframe após dados settled.
- Wheel zoom apenas sobre o canvas do gráfico.

**Non-Goals:**
- Mudar default de 180 velas ou botões de zoom.

## Decisions

1. Nova prop `viewportReady` (default true). ChartModal passa `!loading && !analysisTradesLoading`.
2. Enquanto `!viewportReady`, atualiza `setData` sem marcar viewport aplicado.
3. Quando ready + key nova/não aplicada → `applyDefaultViewport` uma vez; updates seguintes só `setData`.
4. Wheel listener em `chartRef`, capture, passive false.

## Risks / Trade-offs

- Se analysis demorar, chart pode mostrar range “cru” até ready — curto e aceitável vs zoom fantasma.
- Favoritos/result chart sem `viewportReady` mantém default true (comportamento imediato).
