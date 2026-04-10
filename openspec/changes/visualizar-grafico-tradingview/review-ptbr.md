# Review PT-BR: Visualizar gráfico de estratégia igual TradingView

## Resumo

Card #87 propõe adicionar gráfico interativo estilo TradingView na tela Monitor. Quando usuário clicar em uma estratégia, abre modal com candles, volume e indicadores técnicos (SMA, EMA, RSI). Usa `lightweight-charts` (já presente no projeto).

**Mudança UI** — protótipo obrigatório antes de Alan approval.

## Decisão Necessária

Alan, a decisão é se approves o escopo conforme descrito no proposal.md.

## Tradeoffs

| Prós | Contras |
|------|---------|
| Análise visual profissional | Complexidade de implementação |
| Experiência TradingView familiar | Dados históricos apenas (MVP) |
| Biblioteca já no projeto | Desktop-first (mobile limitado) |

## Riscos

1. **Dados OHLCV** — confirmar se API fornece dados de candles; se não tiver, buscar de exchange é fora do escopo
2. **Performance** — muitos candles podem deixar gráfico lento; implementar lazy loading se necessário
3. **Indicadores** — lightweight-charts suporte a built-in indicators pode ser limitado; verificar versão

## Artefatos

- proposal.md: openspec/changes/visualizar-grafico-tradingview/proposal.md
- review-ptbr.md: openspec/changes/visualizar-grafico-tradingview/review-ptbr.md
- tasks.md: openspec/changes/visualizar-grafico-tradingview/tasks.md
