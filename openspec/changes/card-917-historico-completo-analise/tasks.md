# Tasks — card-917-historico-completo-analise

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Origem das setas

- [ ] 1.1 — Em `/combo/results`, construir marcadores a partir da lista de operações da análise (`buildTradeMarkers` nas trades da janela), não como recorte exclusivo de `signal_history` do Monitor.
- [ ] 1.2 — `signal_history` só adiciona operação corrente não duplicada; nunca substitui nem encurta a lista/setas.
- [ ] 1.3 — 1:1 observável: cada linha da lista tem seta de entrada (e saída se fechada); não há seta de operação sem linha.

## 2. Viewport

- [ ] 2.1 — Zoom inicial permanece nas últimas ~180 velas quando a série é maior; não forçar `fitContent` de todas as barras ao abrir.
- [ ] 2.2 — Setas antigas ficam na série e aparecem com Menos, arrastar ou zoom out; Resetar volta o recorte sem dropar marcadores.
- [ ] 2.3 — Densidade: não cortar história; rótulos podem sumir no zoom afastado, setas não.

## 3. Contrato e evidência

- [ ] 3.1 — Resumo Operações = linhas fechadas da lista; vale para qualquer ativo/timeframe da tela.
- [ ] 3.2 — UI alinhada ao proto `frontend/public/prototypes/card-917-historico-completo-analise/index.html`.
- [ ] 3.3 — Playwright `/combo/results` desktop+mobile: lista completa, recorte 180, zoom revela setas anteriores a 05/01/26 (BTC 1d ou equivalente), Resetar preserva a série.
- [ ] 3.4 — `openspec verify` desta change.
