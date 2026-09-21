# Tasks — card-994-monitor-multiplos-timeframes

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Lista: TF ao lado do par

- [x] 1.1 — `resolveChartTimeframe` / `pair-tf` usa `opportunity.timeframe` (TF da estratégia, o mesmo da coluna TF em `/favorites`). BTC/USDT 4h mostra 4h, não 1d.
- [x] 1.2 — Mobile card e ficha expandida mostram o mesmo TF da linha. Sem segundo rótulo «Gráfico 1d» nem «tf 1d».

## 2. Filtro de timeframe

- [x] 2.1 — Opções = Todos + os TFs das estratégias crypto visíveis (como Favoritos), não hardcoded Todos/1d.
- [x] 2.2 — Filtrar 4h mostra só 4h; filtrar 1d mostra só 1d; Todos mostra todas.

## 3. Minigráfico

- [x] 3.1 — Sparkline pede velas no TF da estratégia (linha 4h = velas 4h, não 1d).
- [x] 3.2 — Coluna permanece; th visível = **Gráfico** (rótulo 7d deixa de aplicar). Status/Preço/Distância/Tags/Operar/Par / Estratégia intactos.

## 4. Abrir gráfico / Ver Trades

- [x] 4.1 — `initialTimeframe` de Abrir gráfico e Ver Trades = TF da estratégia. BTC 4h abre em 4h (velas e rótulo só de leitura), não em 1d, e fica nesse TF.
- [x] 4.2 — ChartModal (aberto de Abrir gráfico / Ver Trades no Monitor) sem seletor; só rótulo do TF da estratégia; `initialTimeframe` = TF da estratégia. Sem toolbar `aria-label="Selecionar timeframe do gráfico"`; sem botões 15m / 1h / 1d / «Estratégia (4H)». O filtro da lista Todos / 4h / 1d permanece.

## 5. Ficha um TF e ação 1d

- [x] 5.1 — `OpportunityCard` deixa de pintar «Gráfico 1d», `tf 1d` e o toggle group só-1d. Um só TF: o da estratégia.
- [x] 5.2 — Ação (stock) continua só 1d. Sinal, posição e stop não se recalculam. Favoritos / Descoberta / Combo / Telegram / TF gravado do favorito intactos.

## 6. UI, testes e evidência

- [x] 6.1 — `/monitor` alinhado ao proto `frontend/public/prototypes/card-994-monitor-multiplos-timeframes/index.html` (desktop + mobile): BTC 4h, filtro da lista com 4h, minigráfico 4h, ficha sem segundo TF, gráfico inicia e fica em 4h sem seletor (só rótulo).
- [x] 6.2 — Testes dos critérios Given/When/Then do issue #994 e Playwright desktop+mobile. Fora: redesign da board, extra `/favorites`, stock além de 1d.
- [x] 6.3 — `openspec verify` desta change.
