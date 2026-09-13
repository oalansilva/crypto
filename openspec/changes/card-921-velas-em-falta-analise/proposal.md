## Why

Quem abre o gráfico na análise dos Favoritos ou no Monitor vê médias avançando até o presente e um vazio à direita: as velas pararam semanas ou meses atrás. Dá para achar que o ativo morreu ou que a estratégia está desatualizada.

## What Changes

- Na análise (`/combo/results`) e no gráfico do Monitor, a média (SMA/EMA ou equivalente) não avança à frente da última vela que a tela realmente carregou: sem buraco à direita com linha solta.
- Ao abrir a análise, se a série de mercado daquele par já está em dia, a última vela do gráfico coincide com a última vela de mercado — não fica no snapshot antigo (no BTC 1d medido: não para em 15/08 quando o mercado já está em 12/09).
- Este card enche todos os pares de mercado, mesmo os que não estão agora no Monitor nem nos Favoritos. Não é só BTC, nem só o que está no ecrã.
- Depois de encher, a série de mercado desses pares continua até o presente: não volta a ficar meses atrás.
- Entram todos os intervalos que essas duas telas deixam abrir (Monitor: 15m, 1h, 4h e 1d; análise: o intervalo do favorito). Se o 15m/1h/4h estiver parado, também entra.
- O 1:1 lista↔setas do #917 permanece; este card não o reabre.

Fora: redesign de layout; forçar todas as velas visíveis no zoom inicial (o recorte recente do #917 permanece); recálculo de operações, métricas ou promoção; ações/stocks.

## Capabilities

### New Capabilities

- `aligned-candle-ma-series`: contrato visível de velas e médias no mesmo recorte nas duas telas; série de mercado ao abrir quando já está em dia; enchimento de todos os pares de mercado nos intervalos dessas telas, com continuidade até o presente.

### Modified Capabilities

- `chart-visualization`: overlays de média no gráfico da análise e do Monitor deixam de pintar à frente da última vela carregada; a última vela visível coincide com o mercado quando a série já está em dia.
- `market-candles`: ingestão cobre todos os pares de mercado e os intervalos 15m, 1h, 4h e 1d; após o enchimento a série continua até o presente.
- `favorites`: abrir a análise não congela o snapshot antigo quando a série de mercado já está em dia.

## Impact

- Frontend: `FavoritesDashboard` (open da análise, merge de velas vs overlays), `ComboResultsPage` / `StrategyChartSurface`, `ChartModal` / gráfico do Monitor, `chartData` (intervalos que o Monitor abre).
- Backend: writer canónico / `ohlcv_storage` / universo de pares; API `/market/candles`.
- Sem redesign de layout. Zoom inicial recente do #917 permanece. 1:1 lista↔setas não é reaberto.
- Protótipo: `frontend/public/prototypes/card-921-velas-em-falta-analise/index.html` (clone `/combo/results`) e extra `monitor.html` (clone `/monitor`).
