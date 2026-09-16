## Why

Quem abre a análise pelos Favoritos vê as velas de todo o período do gráfico, mas as linhas da estratégia — médias e as outras que aquele gráfico já desenha — não estão calculadas nesse mesmo histórico. O preço cobre o período; os indicadores não. O mesmo furo vale no gráfico do Monitor.

## What Changes

- Análise aberta pelos Favoritos (`/combo/results`, «Ver análise completa») **e** gráfico do Monitor: as velas do período vêm **e** as linhas da estratégia estão calculadas nesse mesmo histórico — não basta pintar o preço.
- Recorte das linhas = velas que aquela tela já carregou. Favorito 6 meses ou 2 anos **não** alarga para todo o mercado. Se a série cobre anos, as linhas acompanham esses anos — não só o recorte recente.
- Entram as médias no gráfico de preço **e** as outras linhas da estratégia que aquele gráfico já desenha (incluindo o painel de baixo). Não se inventa linha que a estratégia não usa.
- Zoom inicial recente de leitura permanece (~180 velas). Ao abrir, as velas visíveis já têm as linhas (depois do aquecimento). Ao afastar / Menos / arrastar, as velas antigas da série também as têm. Resetar volta ao recorte recente sem apagar as linhas da série.
- O 1:1 lista↔setas do #917 permanece; o buraco à direita do #921 permanece fechado (linha **não** avança à frente da última vela); o período operacional do favorito do #949 não muda.

Fora: reabrir o aceite de #921, #917 ou #949; alargar 6 meses / 2 anos para todo o mercado; abrir já enquadrado em todas as velas; redesign do layout; recálculo de operações, métricas ou promoção; inventar médias ou outras linhas; esconder de novo as linhas no Monitor; ações / stocks.

## Capabilities

### New Capabilities

- `strategy-lines-cover-loaded-candles`: contrato visível de que, na análise dos Favoritos e no gráfico do Monitor, as linhas da estratégia (médias de preço e as outras que aquele gráfico já desenha, painel de baixo incluído) cobrem o mesmo histórico das velas já carregadas; 6 meses / 2 anos não viram «todo o mercado»; zoom recente ~180 permanece; ao afastar, as velas antigas também têm linha; recorte visível ao abrir já tem linha após aquecimento.

### Modified Capabilities

- `aligned-candle-ma-series`: o clip à última vela (#921) permanece; este card acrescenta o inverso — linhas calculadas no histórico das velas carregadas, não só no extremo recente.
- `chart-visualization`: overlays de preço e painéis inferiores da estratégia acompanham o recorte das velas carregadas ao afastar / Menos / arrastar / Resetar, nas duas telas.

## Impact

- Frontend: `StrategyChartSurface`, `strategyTransparency` (hoje só estende SMA/EMA de preço para a frente e clipa), `ComboResultsPage` / `FavoritesDashboard` (open da análise), `ChartModal` / gráfico do Monitor.
- Backend: só se o manifesto persistido das linhas cobrir menos velas do que a tela já carregou — recálculo visível sobre as velas carregadas, sem novo backtest de métricas.
- Sem redesign. Zoom ~180 e 1:1 do #917 intactos. Clip #921 intacto. Período do favorito #949 intacto.
- Protótipo: `frontend/public/prototypes/card-953-grafico-medias-periodo/index.html` (clone `/combo/results`) e extra `monitor.html` (clone `/monitor`).
