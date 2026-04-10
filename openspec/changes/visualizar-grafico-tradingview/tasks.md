# Tasks: Visualizar gráfico de estratégia igual TradingView

## DEV Tasks

- [x] Adicionar click handler no item de estratégia em Monitor screen para abrir modal
- [x] Criar componente ChartModal com `lightweight-charts`
- [x] Implementar candlestick series com dados OHLC
- [x] Adicionar volume histogram abaixo dos candles
- [x] Implementar indicadores: SMA (9), EMA (21), RSI (14)
- [x] Adicionar seletor de timeframe: 1h, 4h, 1d
- [x] Implementar zoom/pan no chart
- [x] Adicionar crosshair para visualização de preço/tempo
- [x] Implementar botão de fechar modal
- [x] Testar em desktop com dados reais

## QA Tasks

- [ ] Validar que clique em estratégia abre modal com gráfico
- [ ] Validar que candles exibem OHLC correto
- [ ] Validar que volume bars aparecem abaixo dos candles
- [ ] Validar que indicadores SMA, EMA, RSI são exibidos (default: todos on)
- [ ] Validar que togglar indicador mostra/esconde linha no chart
- [ ] Validar que seletor de timeframe muda dados do gráfico
- [ ] Validar que zoom/pan funciona com mouse
- [ ] Validar que crosshair segue mouse e mostra tooltip com OHLC
- [ ] Validar que botão X fecha modal
- [ ] Validar que backdrop click fecha modal
- [ ] Validar que modal não abre se não houver dados de candles
