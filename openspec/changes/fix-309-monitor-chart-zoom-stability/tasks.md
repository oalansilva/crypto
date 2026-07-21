## 1. Viewport estável

- [x] 1.1 Adicionar `viewportResetKey` em `StrategyChartSurface` e aplicar default range só na 1ª carga / mudança de key
- [x] 1.2 Passar `viewportResetKey={`${symbol}|${timeframe}`}` no `ChartModal` (e demais call sites se necessário)

## 2. Zoom único na roda

- [x] 2.1 Remover `onWheel` React duplicado; manter um listener nativo
- [x] 2.2 Desligar `handleScale.mouseWheel` e `handleScroll.mouseWheel` do lightweight-charts

## 3. Validação

- [x] 3.1 Teste focado/unitário ou asserção de código cobrindo preservação de range
- [x] 3.2 Rodar E2E de zoom do Monitor (ou trecho equivalente) e validar OpenSpec da change
