## Why

Após abrir o gráfico do Monitor, a área visível muda sozinha como se o usuário estivesse dando zoom com a roda do mouse. Isso quebra a leitura do gráfico e foi reportado no card #309 (rework pós-Done).

## What Changes

- Preservar o range lógico visível após a primeira aplicação ao abrir/trocar `symbol|timeframe`.
- Não reaplicar `fitContent` / default de 180 velas a cada update assíncrono de candles (mercado + merge de analysis).
- Eliminar zoom duplicado na roda (um único handler custom + desligar `mouseWheel` nativo do lightweight-charts).
- Manter botões de zoom/reset e o default de 180 velas no reset explícito.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `chart-visualization`: estabilidade do viewport do gráfico unificado após abertura e updates de dados; zoom por roda sem aplicação múltipla.

## Impact

- Frontend: `StrategyChartSurface`, `ChartModal` (chave de reset de viewport).
- Testes E2E de zoom do Monitor/Favoritos.
- Sem mudança de API/backend.
