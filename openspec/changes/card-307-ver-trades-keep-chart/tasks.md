## 1. Layout

- [x] 1.1 Ajustar `StrategyChartSurface` para, com `belowContent`, manter o gráfico com altura estável e área rolável conjunta (chart+trades).
- [x] 1.2 Ajustar `ChartModal` (viewMode=trades): altura fixa do gráfico, sem painel gigante de transparência sob o canvas.

## 2. Validação

- [x] 2.1 E2E: Ver Trades → após load, gráfico e trades visíveis; assert de altura mínima do chart shell.
- [x] 2.2 Validar Abrir Gráfico / zoom sem regressão; testes Ver Trades passando.
- [ ] 2.3 Integrar em develop, `./restart`, evidência no card.
