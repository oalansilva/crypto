## Why

O scalp BTCUSDT em DEV responde ao Jev e não compra: a fronteira de regime está vazia, a amostra ao vivo é impossível, a régua não resolve barreiras, o custo e a geometria são hostis e o sinal não mostrou vantagem. Abrir só a fronteira ou o limiar faria o scalp perder dinheiro de forma sistemática. Este card mede lucro líquido offline, aplica só o conjunto que paga, e completa um ciclo real em DEV.

## Problema

O scalp BTCUSDT está ligado em DEV e o Jev responde a cada ~30 s, mas nenhuma ordem saiu (`Calibração 0/25989`; zero `scalp cycle sent` no `backend/scalp_jev_diagnostic.log`). O bloqueio não é um único portão; são cinco camadas que se somam:

1. **Fronteira de regime nunca definida.** `SCALP_REGIME_BOUNDARY_BP` é configuração manual que ninguém preencheu e que nada calcula. Todo ciclo sai `market_regime=unknown`, `confidence_policy=closed` → `regime_closed`. O ajuste automático do #1045 só mexe na política de confiança, e o primeiro bloqueio de qualidade dele é justamente a fronteira ausente: é um beco sem saída.
2. **Amostra impossível de atingir ao vivo.** Janelas de 900 s sem sobreposição: 340 em cerca de 5 dias, 291 com preço, **1 elegível** (as outras não passam em hurdle, folga de custo e livro não tóxico). O mínimo são 200, o que ao vivo leva anos. A janela elegível ainda cai porque o modelo e a origem da confiança não foram identificados (824 respostas antigas sem `model`).
3. **A medição não resolve as barreiras.** Sem resolução em 23 de 23 alternativas de alvo e prazo, e 0 alvos, 0 stops e 0 saídas pelo prazo em 340 janelas. Candle ausente ou alvo e stop no mesmo candle deixam o resultado indeterminado, e com isso a viabilidade nunca é avaliada.
4. **Custo e geometria hostis.** Maker de 10 bp por perna (o desconto de BNB está habilitado, mas nunca é aplicado): cerca de 20 bp ida e volta, com saída a MARKET no fim do prazo. Com +35/−28 bp, o resultado líquido é +15 bp no alvo e cerca de −48 bp no stop, o que exige acertar cerca de 76%. Só ~3,7% das janelas de 15 min andam 35 bp ou mais (~14% andam 20 bp ou mais): o alvo quase nunca é tocado e a saída acaba sendo a mercado, como taker.
5. **O sinal não mostrou vantagem.** Acertou o lado em 48 de 100, igual a comprar e segurar, e não ganhou da escolha aleatória. Sugere compra em cerca de 92% das respostas. A confiança nunca passou de 0,3, contra o limiar em uso de 0,7, que bloquearia 100%. O movimento previsto vem em valores fixos (15/20/25 bp) em torno do hurdle de 20,1 bp.

Abrir só a fronteira ou baixar o limiar faria o scalp operar sem vantagem demonstrada, ou seja, perder dinheiro de forma sistemática.

## História

Como operador do scalp Jev, quero que o sistema meça se uma configuração (sinal, custo, alvo/stop, prazo, fronteira de regime e confiança) tem retorno líquido positivo, com amostra suficiente obtida fora do ao vivo. Quero que essa configuração seja aplicada ao robô em DEV, que complete um ciclo real compra→venda, e que o diagnóstico diário passe a promover e reverter também alvo, stop, prazo e recorte de regime junto com a confiança. Quero poder alongar o prazo se for isso que pagar. Enquanto nenhuma geometria neste par mostrar lucro líquido, o trabalho continua a variar prazo, alvo e stop até achar — sem desligar a confiança para operar às cegas.

## Entra

1. **Medição que resolve as barreiras.** A régua resolve alvo, stop e prazo pelo caminho real de preço (aggTrades ou candles de 1 s completos), não pelo OHLCV com buracos ou ambíguo. A amostra considera só as respostas com modelo e origem da confiança identificados.
   - Critério: nas mesmas janelas do relatório de 29/09, menos de 5% das alternativas ficam indeterminadas.
2. **Backtest ou replay offline** com aggTrades históricos da Binance, a mesma lógica de decisão do `scalp_engine` e as taxas reais da conta (maker; na saída, a taxa da limitadora quando ela fecha, ou a de mercado só se a limitadora não fechar, com teto de derrapagem). Saída: janelas sem sobreposição, comparação do sinal com o acaso na mesma proporção de compras, lado contra comprar e segurar, e retorno líquido por alvo/stop e por prazo — inclusive prazos maiores que 15 min.
   - Critério: pelo menos 200 janelas independentes por regime em uma execução, sem depender do log ao vivo.
3. **Custo real no hurdle.** O desconto de BNB entra quando há saldo de BNB suficiente para cobrir a taxa, e a tela passa a dizer "desconto aplicado". A saída no fim do prazo tenta primeiro uma limitadora; a saída a mercado vira último recurso, com teto de slippage.
   - Critério: a taxa em uso na tela e no hurdle bate com a taxa efetivamente cobrada nos fills.
4. **Alvo, stop e prazo recalibrados até pagar.** Só é promovida uma geometria cujo retorno líquido por trade seja positivo, com intervalo de confiança acima de zero no backtest. O prazo pode alongar além de 15 min se for isso que pagar. Enquanto nenhuma geometria neste par mostrar lucro líquido, este card continua a variar prazo, alvo e stop — não termina. A geometria em uso fica até achar uma que pague.
5. **Sinal no conjunto, sem operar às cegas.** A prova é do conjunto (sinal, custo, alvo/stop, prazo, recorte de regime e confiança). Não se desliga o filtro de confiança para operar sem vantagem do sinal. Quando o conjunto pagar, a confiança reportada é calibrada para a escala real dela, deixando de ser 0,0–0,3 comparada com 0,7.
6. **Fronteira de regime calculada, não manual.** A fronteira sai da distribuição de volatilidade do backtest, na mesma escala que a decisão usa, e fica gravada na versão aplicada junto com a política de cada regime, o alvo, o stop e o prazo. O diagnóstico diário passa a promover e reverter alvo, stop, prazo, recorte de regime e confiança juntos.
7. **Portão de promoção pelo backtest; o ao vivo confirma em DEV.** Os 200 do #1045 são contados no backtest. O lucro líquido exigido é o do backtest. Com a configuração promovida, o scalp em DEV envia pelo menos uma ordem post-only real de 10 dólares e fecha o ciclo compra→venda. Essa primeira volta pode fechar no prejuízo e ainda conta: basta comprar, vender e o resultado aparecer na tela. O diagnóstico do dia seguinte pode promover ou reverter essa geometria e o recorte de regime junto com a confiança, sempre que a prova do dia mostrar (ou deixar de mostrar) lucro líquido.
   - Critério: em DEV, com a configuração promovida, o scalp completa um ciclo compra→venda real. O P&L líquido por trade aparece na tela, mesmo negativo. O lucro líquido exigido continua o do backtest.

### Decisões fechadas (grelha 29/09)

- Quando a prova passa: aplica a configuração em DEV, completa um ciclo real, e o diagnóstico diário passa a promover e reverter também alvo, stop, prazo e recorte de regime junto com a confiança.
- O prazo pode alongar se o backtest mostrar lucro líquido; 15 min deixa de ser teto.
- Se a prova não mostrar lucro líquido, o card não termina: continua a variar prazo, alvo e stop neste par até achar lucro líquido.
- No fim do prazo tenta primeiro uma limitadora; mercado só como último recurso, com teto de derrapagem.
- A primeira ordem ao vivo é de 10 dólares.
- A primeira volta real em DEV pode fechar no prejuízo e ainda conta. Basta comprar, vender e o resultado aparecer na tela. O lucro líquido exigido continua o do backtest.

## Não entra

- Operar com a fronteira ou a confiança abertas antes de o backtest provar retorno líquido positivo.
- Aumentar o teto T ou o clip; saque.
- PROD. Continua valendo o T16 do lote.
- Trocar de exchange ou de par sem decisão do Alan. Verificar se a conta tem par de BTC ou tier com maker menor entra só como levantamento, dentro do item 3.
- Refazer a tela do Monitor além dos textos de estado, taxa e P&L citados acima.
- Desligar o filtro de confiança e operar sem vantagem do sinal.
- Encerrar este card com recusa visível enquanto ainda não houver geometria com lucro líquido neste par.
- Deixar o diagnóstico diário a mudar só a confiança: depois deste card, alvo, stop, prazo e recorte de regime também sobem e descem com a prova do dia.

## What Changes

- A régua resolve alvo, stop e prazo pelo caminho real de preço (aggTrades ou candles de 1 s completos). A amostra só conta respostas com modelo e origem da confiança identificados. Nas janelas do relatório de 29/09, menos de 5% das alternativas ficam indeterminadas.
- Um backtest/replay offline usa aggTrades históricos da Binance, a mesma lógica de decisão do `scalp_engine` e as taxas reais da conta. Produz ≥200 janelas independentes por regime numa execução, sem o log ao vivo. Compara o sinal com o acaso na mesma proporção de compras, com comprar e segurar, e o retorno líquido por alvo/stop e por prazo — inclusive prazos maiores que 15 min.
- O desconto de BNB entra no hurdle e na tela quando há saldo de BNB suficiente para cobrir a taxa; a tela diz "desconto aplicado". A taxa na tela e no hurdle bate com a cobrada nos fills. **BREAKING** face ao #1045: deixar de mostrar «BNB habilitado; desconto não aplicado» quando o desconto de facto entra.
- No fim do prazo a saída tenta primeiro uma limitadora; mercado só como último recurso, com teto de derrapagem. **BREAKING** face a `scalp-aggressive-exit`: a MARKET deixa de ser o primeiro e único escape sem teto.
- Só é promovida uma geometria com retorno líquido por trade positivo e intervalo de confiança acima de zero no backtest. O prazo pode alongar além de 15 min. A geometria em uso fica até achar uma que pague. **BREAKING** face ao #1045: o automático passa a gravar alvo, stop e prazo, não só a confiança. **BREAKING** face a `scalp-jev-horizonte` / `scalp-regime-gate`: 15 min deixa de ser teto do prazo.
- A prova é do conjunto. O filtro de confiança não se desliga para operar às cegas. Quando o conjunto pagar, a confiança reportada é calibrada à escala real.
- A fronteira de regime sai da distribuição de volatilidade do backtest, na mesma escala da decisão, e fica na versão aplicada. O diagnóstico diário promove e reverte alvo, stop, prazo, recorte de regime e confiança juntos.
- Os 200 do #1045 contam-se no backtest. O lucro líquido exigido é o do backtest. Com a configuração promovida, o scalp em DEV envia uma ordem post-only de 10 dólares e fecha o ciclo compra→venda. A primeira volta pode fechar no prejuízo e ainda conta; o P&L líquido por trade aparece na tela, mesmo negativo.
- No `/monitor`, só mudam os textos de estado, taxa e P&L. Board, Operar, T, clip, kill e interruptor ficam. Sem rota nova. Sem landing/Ajuda. Sem PROD (T16). Sem aumentar T ou clip. Sem desligar a confiança. O card não termina com recusa visível enquanto neste par não houver geometria com lucro líquido.

## Capabilities

### New Capabilities

- `scalp-jev-offline-backtest`: replay offline com aggTrades históricos, a mesma decisão do `scalp_engine`, taxas reais da conta, ≥200 janelas independentes por regime, retorno líquido por alvo/stop e por prazo.
- `scalp-jev-geometry-apply`: promoção e reversão de alvo, stop, prazo e recorte de regime junto com a confiança, só quando o backtest mostra lucro líquido por trade com intervalo de confiança acima de zero; ciclo DEV de 10 dólares; o card continua a variar até achar lucro líquido neste par.

### Modified Capabilities

- `monitor`: no módulo Scalp BTCUSDT, os textos de estado, taxa («desconto aplicado») e P&L líquido por trade; o diagnóstico passa a falar de alvo, stop, prazo e recorte de regime junto com a confiança.
- `scalp-maker-fee-hurdle`: o desconto de BNB entra na taxa em uso quando o saldo de BNB cobre a taxa; hurdle e tela batem com o fill.
- `scalp-jev-eval-ruler`: resolve barreiras pelo caminho real (aggTrades ou 1 s); amostra só com modelo e origem identificados; <5% indeterminadas nas janelas de 29/09.
- `scalp-jev-realized-measurement`: a medição realizada usa o caminho real de preço, não o OHLCV com buracos ou ambíguo.
- `scalp-jev-net-return-ruler`: o lucro líquido exigido para promover é o do backtest, com intervalo de confiança acima de zero; os 200 contam-se no backtest.
- `scalp-aggressive-exit`: no fim do prazo tenta primeiro a limitadora; mercado só como último recurso, com teto de derrapagem.
- `scalp-confidence-threshold-per-regime`: a fronteira sai da distribuição de volatilidade do backtest e fica na versão aplicada; fail-closed enquanto o backtest não a gravar.
- `scalp-jev-horizonte`: o prazo (hold após fill e janela da geometria) pode alongar além de 15 min quando o backtest mostrar lucro líquido; 15 min deixa de ser teto.
- `scalp-regime-gate`: o prazo deixa de estar fixo em 15 min; muda só pela versão promovida deste card.
- `scalp-monitor-horizonte`: lookback, alvo, stop e P&L líquido por trade na tela reflectem a versão aplicada; perda tão visível quanto ganho.

## Impact

- Frontend: delta de copy no `ScalpModule` em `/monitor` (estado, taxa, P&L). Board (`table.signals`) e Operar intactos. Sem landing, Ajuda ou rota nova.
- Backend / régua: caminho de preço em aggTrades ou 1 s; replay offline; `_fee_terms` aplica o desconto de BNB quando o saldo cobre; versão aplicada passa a incluir alvo, stop, prazo e fronteira; saída no fim do prazo tenta limitadora antes da MARKET com teto.
- Loop do scalp: lê a versão aplicada na entrada; a primeira ordem DEV é post-only de 10 dólares; o P&L líquido por trade (preço menos taxas das duas pernas) vai para a tela.
- Diagnóstico diário do #1045: deixa de aplicar só a confiança; promove e reverte o conjunto. A régua de avaliação do backtest continua sem escrever produto; a aplicação é etapa própria.
- Não reabre T, clip, kill, saque, exchange ou par. PROD continua T16.
- Protótipo: clone de `/monitor` com o delta de estado, taxa e P&L. `frontend/public/prototypes/card-1070-scalp-jev-lucro-liquido/index.html`.
