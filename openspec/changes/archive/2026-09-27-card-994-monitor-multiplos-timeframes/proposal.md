## Why

No Monitor, um favorito crypto cujo timeframe nos Favoritos é 4h (ex.: BTC/USDT `Médias Móveis: Tendência em Virada`) aparece, filtra e abre o gráfico como se fosse 1d. O sinal da lista já é o da estratégia; o que falha é a ficha, o filtro, o minigráfico e o TF inicial do gráfico.

## Problema

O operador acompanha no Monitor uma estratégia cujo timeframe nos Favoritos não é 1d e vê, filtra e abre o gráfico como se fosse 1d.

## História

Como operador que usa Favoritos e Monitor no dia a dia, quero que o Monitor mostre, filtre e abra o gráfico no timeframe da estratégia (o mesmo da coluna TF dos Favoritos), para não tratar um 4h como 1d na hora de acompanhar e de abrir o gráfico.

## Entra

- Na lista do Monitor, o timeframe ao lado do par é o da estratégia — o mesmo valor da coluna TF daquela linha em `/favorites`.
- Na ficha (linha e expandida) há um só TF: o da estratégia. Não há segundo rótulo «Gráfico 1d» nem «tf 1d» nessa linha.
- O filtro de timeframe do Monitor lista os timeframes das estratégias crypto visíveis (como o filtro TF dos Favoritos: Todos + os TFs que existem na lista), não só 1d.
- Filtrar por 4h mostra só as estratégias 4h; filtrar por 1d mostra só as 1d; Todos mostra todas.
- O minigráfico da lista usa o TF da estratégia (linha 4h = velas 4h, não 1d). O rótulo 7d deixa de aplicar; o nome visível da coluna fica para Design.
- Abrir gráfico e Ver Trades usam sempre o TF da estratégia, não um TF fixo (1d). Um favorito 4h abre em 4h, não em 1d.
- **Como neste rework (fecha o fork Design):** o gráfico **não** oferece seletor de TF. Só exibe o TF da estratégia. Sem inspecção 15m/1h/1d. Abrir gráfico / Ver Trades abrem no TF da estratégia e **ficam** nesse TF. O TF aparece como rótulo só de leitura (chip `4h` ou texto `Estratégia · 4h`), não como seletor.
- Sinal, posição e stop continuam os da estratégia naquele timeframe (já é o comportamento da análise).
- Ação (stock) continua só em 1d.

Critérios:

- Given um favorito crypto BTC/USDT em 4h visível em `/favorites`, when o operador abre `/monitor`, then a ficha dessa estratégia mostra 4h ao lado do par e não mostra «Gráfico 1d» nem «tf 1d».
- Given a mesma lista com pelo menos um 4h e um 1d, when o operador escolhe o filtro 4h, then só as estratégias 4h permanecem visíveis.
- Given essa estratégia 4h, when o operador clica Abrir gráfico (ou Ver Trades), then o gráfico inicia e fica em 4h (velas e rótulo só de leitura), não em 1d, sem seletor de TF, e a lista continua a mostrar 4h ao lado do par.
- Given essa linha 4h, when o operador vê o minigráfico da lista, then as velas são 4h, não 1d.

## Não entra

- Mudar o timeframe gravado no favorito.
- Descoberta, Combo ou backtest.
- Recalcular sinal, stop ou métricas.
- Telegram.
- Gráfico de ação além de 1d.
- Segundo TF de preço na ficha («Gráfico 1d» / «tf 1d»).
- Gravar no Monitor o último TF olhado no gráfico.
- Seletor de TF no gráfico aberto a partir do Monitor.

## What Changes

- `/monitor` mostra ao lado do par o TF da estratégia (o mesmo da coluna TF em `/favorites`), não um 1d fixo.
- Ficha (linha e expandida): um só TF, o da estratégia. Somem «Gráfico 1d» e «tf 1d».
- Filtro de timeframe = Todos + os TFs das estratégias crypto visíveis (igual Favoritos). 4h mostra só 4h; 1d mostra só 1d; Todos mostra todas.
- Minigráfico da lista nas velas do TF da estratégia. Coluna deixa de chamar-se 7d.
- Abrir gráfico e Ver Trades abrem no TF da estratégia e ficam nesse TF. O gráfico só exibe o TF da estratégia: sem seletor, sem botões 15m/1h/1d/«Estratégia (4H)», sem inspecção noutro TF.
- Ação (stock) continua só em 1d.
- Sinal, posição e stop não mudam. Favoritos, Descoberta, Combo, backtest, Telegram e o TF gravado do favorito não entram.

## Capabilities

### New Capabilities

- `monitor-strategy-timeframe`: contrato visível do Monitor a respeitar o TF da estratégia na lista, no filtro da lista, no minigráfico, na ficha (um só TF) e no gráfico aberto a partir do Monitor (só exibe o TF da estratégia; sem seletor); ação (stock) só 1d.

### Modified Capabilities

- `monitor`: o TF ao lado do par, o filtro de timeframe da lista, o minigráfico e o gráfico aberto deixam de estar presos em 1d; passam a usar o TF da estratégia. Gráfico sem seletor de TF. Sem redesign da board (Status, Preço, Distância, Tags, Operar, Par / Estratégia). A coluna do minigráfico permanece; o rótulo 7d deixa de aplicar.
- `monitor-card-timeframe-pref`: a ficha deixa de expor um segundo TF de preço («Gráfico 1d» / «tf 1d»). Não há TF de inspecção para gravar.

## Impact

- Frontend: `MonitorStatusTab.tsx` (`resolveChartTimeframe` hoje devolve 1d; filtro `TimeframeFilter` só `all|1d`; sparkline naquele TF), `OpportunityCard.tsx` (rótulos «Gráfico {effectiveTimeframe}» e `tf {effectiveTimeframe}` presos em 1d), `ChartModal.tsx` (`initialTimeframe` de Abrir gráfico / Ver Trades; toolbar `aria-label="Selecionar timeframe do gráfico"` a esconder/remover nesse contexto). Sem mudança de copy em `/favorites`. Sem Descoberta/Combo/backtest/Telegram.
- Backend: o TF da estratégia no favorito e no sinal do Monitor já existem; este card não recalcula sinal, stop nem métricas.
- Ação (stock): gráfico de ação continua só 1d (fora desta cena crypto).
- Protótipo: clone `/monitor` canónico (lista BTC 4h + filtro da lista Todos/4h/1d + minigráfico 4h + ficha um TF + gráfico aberto em 4h sem seletor, só rótulo). Sem extra `/favorites`. Sem painel ANTES/DEPOIS no index.
