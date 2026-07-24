## Context

Fix #311 removeu zoom triplo e tentou preservar range, mas ainda reaplicava default quando `candlestickData.length` mudava (fetch → merge analysis) e o wheel capturava o shell inteiro. O fix #313 adicionou `viewportReady`, porém `analysisTradesLoading` iniciava em `false`; no primeiro render, `viewportReady` podia ficar `true` antes do effect iniciar a análise. O range era então aplicado aos candles iniciais e preservado após o merge, produzindo a aparência de zoom automático. Um `xl:h-full` também deixava a altura do canvas variar com o conteúdo assíncrono do modal.

## Goals / Non-Goals

**Goals:**
- Um único apply de viewport default por symbol/timeframe após dados settled.
- Estado de loading correto desde o primeiro render, sem janela falsa de readiness.
- Altura desktop estável durante carregamentos assíncronos.
- Wheel zoom apenas sobre o canvas do gráfico.

**Non-Goals:**
- Mudar default de 180 velas ou botões de zoom.

## Decisions

1. Nova prop `viewportReady` (default true). ChartModal passa `!loading && !analysisTradesLoading`.
2. Enquanto `!viewportReady`, atualiza `setData` sem marcar viewport aplicado.
3. Quando ready + key nova/não aplicada → `applyDefaultViewport` uma vez; updates seguintes só `setData`.
4. Wheel listener em `chartRef`, capture, passive false.
5. `analysisTradesLoading` inicia em `true`, pois a requisição de análise começa no mount.
6. Canvas desktop usa altura calculada e limitada (`calc(100vh - 330px)`, mínimo 420px, máximo 720px), evitando reflow por `h-full`.
7. A requisição de análise tem timeout de 15 segundos; timeout aplica o fallback de `signalHistoryTrades` e sempre libera `analysisTradesLoading`, enquanto unmount apenas cancela sem atualizar estado.

## Risks / Trade-offs

- Se analysis demorar, chart pode mostrar range “cru” até ready — curto e aceitável vs zoom fantasma.
- Favoritos/result chart sem `viewportReady` mantém default true (comportamento imediato).
- Se a API de análise travar, o timeout encerra o estado pendente e mantém o gráfico utilizável com o fallback local.
