## Why

O Alan só tem estratégias validadas em 1D e 4h e quer mais rápidas, mas o day trade puro não sobrevive a taxa e slippage. Este card entrega a ferramenta na Descoberta que já existe: 1h e 15m, 3 templates das lacunas, VWAP nos templates, e slippage realista no backtest — sem varredura, sem filtro do gráfico diário, sem tela nova.

## Problema

O Alan só tem estratégias validadas em 1D e 4h e quer estratégias mais rápidas, mas não sabe quais delas sobrevivem aos custos. As estratégias populares de day trade não passam em teste honesto:

- Rompimento da abertura de NY em BTC/ETH: fator de lucro 0,65 e −44,8% em 12 meses, com custos.
- Reversão à VWAP em BTC: perde depois das taxas.
- Um estudo com mais de uma dúzia de sinais intradiários não achou vantagem depois de ~0,13% de custo por operação completa.

Além disso, o motor de combos tem limites que deixam o resultado em 1h otimista:

- Não modela slippage; só a taxa de 0,075% por lado (`TRADING_FEE` em `combo_optimizer.py`). A Descoberta grava rótulo de taxa 0,1% e slippage 0,1% que não bate com a conta.
- O stop do laço rápido só vale para operação comprada.
- Não tem VWAP, hora do dia nem stop por ATR.
- Em timeframes intradiários, o histórico é limitado a cerca de 900 dias.

Sem um teste com critérios fixos, qualquer estratégia "rápida" que pareça boa no backtest pode só estar ajustada ao passado.

## História

Como Alan, quero a Descoberta aceitando 1h e 15m e os 3 templates das lacunas disponíveis, a VWAP disponível nos templates, e o backtest descontando slippage realista por timeframe, para eu varrer qualquer moeda que eu escolher, com o selo e o placar que a Descoberta já usa, e promover à mão para Favoritos.

## Entra

1. **Descoberta aceita 1h e 15m.** A varredura roda na tela de Descoberta que já existe (`/combo/discovery`): preflight → sweep (produto cartesiano templates × pares × timeframes × direções) → otimiza cada combinação com split 70/30 fixo → placar → o Alan promove para favorito tier 3 pela própria tela. Hoje a Descoberta só aceita 4h e 1d (`DISCOVERY_SWING_TIMEFRAMES` em `backend/app/services/discovery_service.py` e na UI `DiscoveryPage.tsx`). As mudanças de código deste card são liberar 1h e 15m nessa lista, descontar slippage no backtest e acrescentar o indicador VWAP. Períodos que a tela já oferece: 6m, 2y, all (ou datas).
   - Critério: o preflight e a tela de Descoberta continuam a aceitar 4h e 1d e passam a aceitar também 1h e 15m.
2. **Templates que já existem + 3 novos nas lacunas.** Sem templates `lab_` soltos, sem script próprio, sem código de motor. Os 3 novos saem do editor/fluxo de templates que já existe. Templates não fixam timeframe.
   - Já existem e se parecem com as ideias da pesquisa: `Bollinger_Breakout` (rompimento da banda superior, sai na média); `volume_atr_breakout` e "Example: Breakout with Volume" (rompimento com volume); `RSI_EMA_Scalping` e `ema_rsi` (RSI curto a favor da tendência); `ema_rsi_fibonacci` (EMA longa + RSI, sem ADX); `bollinger_rsi_adx` (reversão na banda inferior com ADX).
   - Lacunas → 3 templates novos: canal de Donchian de N candles com volume; squeeze de Bollinger; pullback com média longa + RSI + ADX.
   - Critério: os 3 templates novos aparecem para escolha na Descoberta e rodam um backtest sem erro em 4h, 1h e 15m numa moeda qualquer, p.ex. BTC/USDT.
   - Critério: um template que a Descoberta já oferece hoje também completa um backtest sem erro em 1h e em 15m numa moeda qualquer.
3. **Veredito = selo e placar da Descoberta.** Vale a regra que a Descoberta já usa (`evaluate_discovery_go_nogo` em `backend/app/metrics/criteria.py`): no treino Calmar >= 1, fator de lucro >= 1,5, queda máxima <= 35%; no teste fora da amostra Sharpe > 0. Elegibilidade para promover: 30 operações ou mais e cobertura de dados >= 90%. Sem filtro ou limiar próprio deste card. Sem GO/NO-GO do Combo como veto. O Alan promove para Favoritos pela própria tela, como já faz hoje. Sem promoção automática.
   - Comparar estratégias continua na tela de Favoritos (até 3 por vez). Sem régua contra favorita, EMA 200 ou hold.
   - O 15m desconta 0,05% de slippage por lado; a taxa é 0,075% por lado. Em timeframes intradiários, o histórico é limitado a cerca de 900 dias.
4. **Slippage no backtest.** Em todo backtest (Combo, Descoberta, lote e revalidação de favoritos), igual para todos. Valor fixo por timeframe, por lado: 0,02% em 1d e 4h; 0,03% em 1h; 0,05% em 15m. A conta e o rótulo mostram o valor usado. Os números das estratégias de 1d e 4h já salvas vão cair um pouco na próxima atualização — o Alan aceitou isso. O rótulo de custo gravado pela Descoberta passa a mostrar a taxa e o slippage realmente usados.
   - Critério: a mesma estratégia, no mesmo período, dá retorno por operação menor do que antes na diferença esperada do slippage do timeframe.
   - Critério: Combo, Descoberta, lote e revalidação usam o mesmo valor para o mesmo timeframe.
   - Critério: o rótulo da Descoberta mostra 0,075% de taxa e o slippage do timeframe.
5. **VWAP nos templates.** O template pode usar o indicador VWAP em duas formas: VWAP do dia, que zera à 00h UTC (faz sentido em 15m, 1h e 4h); e VWAP móvel dos últimos N candles (qualquer timeframe, inclusive 1d; N otimizável).
   - Critério: um template pode usar a VWAP do dia e a VWAP móvel numa regra de entrada ou saída e roda backtest sem erro em 15m, 1h e 4h.
   - Critério: a VWAP móvel roda também em 1d.
   - Critério: a VWAP do dia recomeça a cada 00h UTC.
   - Critério: o N da VWAP móvel pode ser otimizado como os outros parâmetros.
6. Este card acaba quando 1h e 15m estão liberados, os 3 templates estão disponíveis e validados, o slippage está aplicado no backtest, e a VWAP está disponível nos templates.

## Não entra

- Regra de hora do dia nos templates: decidido que não faz sentido agora (estratégias presas a horário perderam depois dos custos; risco de ajuste ao passado).
- Filtro de tendência do gráfico diário: 4h, 1h e 15m operam sozinhos, sem exigir tendência a favor no diário.
- Stop por ATR: o stop continua em % fixo.
- Funding e outras mudanças de motor além de slippage e VWAP.
- Campo na tela para mudar o slippage por rodada.
- Recalcular agora todos os favoritos existentes: os números mudam na próxima atualização normal.
- Filtro ou limiar próprio deste card. Vale o selo e o placar da Descoberta.
- GO/NO-GO do Combo como veto.
- Promoção automática para Favoritos.
- Régua contra favorita, EMA 200 ou hold. Comparar estratégias é a tela de Favoritos.
- Tela nova. Templates `lab_` soltos. Script próprio de varredura.
- Rodar varredura ou escolher moedas: o Alan roda depois na Descoberta, com a moeda que quiser.
- Estratégias vendidas (short).
- Operar ao vivo.
- Paper trading: card seguinte, se o Alan achar sinal depois de rodar.
- PROD (deploy só no fluxo normal do T16).

## What Changes

- A Descoberta (`/combo/discovery`) passa a aceitar 1h e 15m **e continua** a aceitar 4h e 1d. Copy do heading, checkboxes de timeframe, impedimento do preflight e filtro do leaderboard acompanham essa lista. Sem filtro de tendência do gráfico diário.
- Três templates novos nas lacunas (Donchian+volume, squeeze de Bollinger, pullback média longa+RSI+ADX) pelo editor que já existe; aparecem para escolha na Descoberta. Sem `lab_` soltos. Templates que a Descoberta já oferece também completam backtest sem erro em 1h e 15m.
- Todo backtest (Combo, Descoberta, lote, revalidação de favoritos) desconta slippage fixo por lado na tabela de Entra: 0,02% em 1d e 4h; 0,03% em 1h; 0,05% em 15m. **BREAKING** nos números de 1d/4h já salvos na próxima atualização normal (aceite no body). O rótulo da Descoberta mostra taxa 0,075% e o slippage do timeframe, em vez de 0,1% / 0,1%.
- Templates podem usar VWAP do dia (zera 00h UTC) e VWAP móvel de N candles (N otimizável, inclusive 1d).
- Veredito, promoção e placar ficam os da Descoberta. Sem limiar próprio, sem veto Combo, sem promoção automática, sem tela nova, sem varredura neste card, sem campo de slippage, sem short/ao vivo/paper/PROD.

## Capabilities

### New Capabilities

- `backtest-slippage-by-timeframe`: tabela única de slippage por lado (1d/4h 0,02%; 1h 0,03%; 15m 0,05%) em Combo, Descoberta, lote e revalidação; rótulo com taxa 0,075% e o slippage do timeframe.
- `combo-vwap-indicator`: VWAP do dia (reset 00h UTC) e VWAP móvel de N candles (N otimizável, inclusive 1d) usáveis em regras de template.

### Modified Capabilities

- `discovery-sweep`: preflight e snapshot aceitam 1h e 15m além de 4h e 1d; rejeitam intervalos fora dessa tabela como eixo da Descoberta.
- `discovery-three-modes`: copy e eixos visíveis de timeframe em Montar (4h, 1h, 15m, 1d); sem campo de slippage; sem filtro 1D.
- `discovery-leaderboard`: evidência de custo mostra taxa 0,075% e slippage do timeframe realmente usado; filtro inclui 1h e 15m; selo e placar inalterados.
- `discovery-catalog-selection`: os 3 templates das lacunas entram no catálogo escolhível da Descoberta, sem `lab_` soltos.
- `combo-optimizer`: o caminho de backtest/otimização aplica a tabela de slippage e calcula as duas VWAPs; 1h e 15m da tabela de Entra passam no mesmo caminho que 4h/1d.
- `favorite-backtest-refresh`: a próxima atualização normal usa a mesma tabela de slippage do timeframe do favorito; este card não dispara recálculo imediato.

## Impact

- Frontend: `DiscoveryPage.tsx` (lista de timeframes, heading, impedimento, filtro, rótulo `fees_slippage`). Sem rota nova. Sem campo de slippage. Combo continua com o seletor que já tem (inclui intervalos fora da tabela da Descoberta, sem valor novo neste card).
- Backend: `DISCOVERY_SWING_TIMEFRAMES`; evidência de custo no worker da Descoberta; slippage no motor de backtest (Combo, lote, revalidação); VWAP no editor/indicadores; 3 templates pelo fluxo existente.
- Favoritos: números de 1d/4h mudam na próxima atualização normal, não agora.
- Protótipo: clone de `/combo/discovery` em `frontend/public/prototypes/card-1074-swing-curto-1h-15m/index.html`.
- Skills do projeto (`.cursor/skills`, `.agents/skills`) no Apply quando couber. Gate de UI: Design → Aprovação de Design → Pronto para Dev.
