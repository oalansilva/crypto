## Context

O gráfico unificado (`StrategyChartSurface`) aplica `setVisibleLogicalRange` (últimas 180 velas) ou `fitContent` em todo update de `candlestickData`/`volumeData`. No Monitor, o `ChartModal` atualiza candles em etapas (iniciais → mercado → merge analysis), o que reaplica o viewport e parece zoom automático. Há também três caminhos de wheel zoom ao mesmo tempo.

## Goals / Non-Goals

**Goals:**
- Viewport estável após abertura até o usuário zoomar ou trocar symbol/timeframe.
- Um único caminho de zoom por roda, coerente com os botões +/-/reset.
- Manter default de 180 velas no reset explícito e na primeira renderização com dados.

**Non-Goals:**
- Alterar indicadores, markers, layout Ver Trades (#307) ou remoção de Signals (#309 original).
- Mudar contrato de API ou backend.
- Redesign dos controles de zoom.

## Decisions

1. **Reset key** — `viewportResetKey` (ex.: `${symbol}|${timeframe}`) no `StrategyChartSurface`. Quando muda ou dados voltam de vazio→não-vazio, aplica range default uma vez.
2. **Updates seguintes** — `setData` sem tocar em `setVisibleLogicalRange`/`fitContent`, preservando o zoom do usuário e evitando o “zoom fantasma”.
3. **Wheel único** — manter listener nativo `passive: false` no shell; remover `onWheel` React duplicado; desligar `handleScale.mouseWheel` e `handleScroll.mouseWheel` do lightweight-charts.
4. **Reset button** — continua usando `getDefaultLogicalRange` / `fitContent` (comportamento atual).

## Risks / Trade-offs

- Se o chart não remountar e a key falhar, timeframe antigo pode manter zoom — mitigado passando key do `ChartModal`.
- Desligar mouseWheel nativo muda o pan por roda; o handler custom só faz zoom (não pan horizontal). Aceitável: copy da UI já diz “Roda do mouse: zoom”.
- E2E de zoom deve continuar passando (botões + um wheel event = um passo).
