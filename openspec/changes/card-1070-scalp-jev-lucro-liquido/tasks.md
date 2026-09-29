## 1. Caminho de preço e amostra identificada

- [x] 1.1 — Resolver alvo, stop e prazo em aggTrades (primeiro toque) ou candles de 1 s completos; OHLCV com buracos não decide barreira.
- [x] 1.2 — Amostra só com `model` e origem da confiança declarados; `unknown`/ausente fora.
- [x] 1.3 — Remedir as janelas do relatório de 29/09: menos de 5% das alternativas indeterminadas.

## 2. Backtest offline

- [x] 2.1 — Corredor read-only de replay com aggTrades históricos BTCUSDT, `decide_cycle` / `scalp_engine` iguais ao vivo, cache de respostas Jev por hash do estado.
- [x] 2.2 — Taxas: maker na limitadora que fecha; taker + teto de derrapagem só se a limitadora não fechar.
- [x] 2.3 — Janelas sem sobreposição; comparação com acaso na mesma proporção de compras, lado contra comprar e segurar, retorno líquido por alvo/stop e por prazo (incluindo >15 min).
- [x] 2.4 — Uma execução produz ≥200 janelas independentes por regime, sem o log ao vivo.

## 3. Custo real e BNB

- [x] 3.1 — `_fee_terms` aplica o desconto de BNB uma vez quando interruptor + símbolo + `spotBNBBurn` + `BNB.free` cobrem a taxa do clip de US$ 10.
- [x] 3.2 — Hurdle = `2 × fee_bp + spread_bp` com essa taxa. Sem saldo, taxa sem desconto e a tela não diz «desconto aplicado».
- [x] 3.3 — Taxa na tela e no hurdle bate com a commission do fill; desvio visível no diagnóstico.

## 4. Saída no fim do prazo

- [x] 4.1 — No fim do prazo aplicado: cancelar a passiva de alvo/stop e postar limitadora post-only no lado realizável. Sem MARKET nesse ciclo.
- [x] 4.2 — Último recurso: LIMIT IOC com teto de derrapagem da versão (10 bp sobre o mid fresco). Sem MARKET sem preço. Livro além do teto → não envia, tenta a limitadora no ciclo seguinte.
- [x] 4.3 — «posição presa» no analogado prazo+30 s; Operar continua.

## 5. Promoção do conjunto

- [x] 5.1 — Versão aplicada inclui política numérica de confiança (escala calibrada), fronteira de `vol_bp`, alvo, stop e prazo. Impressão digital única; não aplica duas vezes.
- [x] 5.2 — Promove só se a média líquida por janela independente no backtest tiver o limite inferior do IC 95% (BCa) acima de zero.
- [x] 5.3 — Não grava confiança `off` para obter fills. Sem prova, a geometria em uso fica e a grelha continua (alvo × stop × prazos 15 min / 1 h / 4 h / 24 h, depois prazos seguintes).
- [x] 5.4 — Fronteira = corte único na escala de `window.vol_bp` da amostra do backtest; fail-closed até a versão a gravar. Não preencher `SCALP_REGIME_BOUNDARY_BP` à mão.
- [x] 5.5 — Diagnóstico diário promove e reverte alvo, stop, prazo, recorte e confiança juntos.

## 6. Monitor (estado, taxa, P&L)

- [x] 6.1 — `ScalpModule` alinhado ao proto: «desconto aplicado» só quando o desconto entrou; P&L líquido por trade em bp e US$ (perda tão visível quanto ganho); estado com lookback/hurdle/taxa/alvo/stop da versão.
- [x] 6.2 — Diagnóstico em frase de trader: amostra do backtest, conjunto aplicado ou ainda a variar, sem desligar a confiança. Board (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) e Operar intactos. Sem rota nova. Sem landing/Ajuda.
- [x] 6.3 — Playwright `/monitor` contra o proto: landmarks da board, taxa com desconto quando aplica, P&L líquido negativo visível, interruptor/T/clip/kill intactos.

## 7. Ciclo DEV e fecho do card

- [x] 7.1 — Com a versão promovida, DEV envia post-only de US$ 10 e fecha compra→venda. T e clip não sobem.
- [x] 7.2 — A primeira volta pode fechar no prejuízo e ainda conta; `last_trade_*` líquidos aparecem na tela. O lucro líquido exigido continua o do backtest.
- [x] 7.3 — Enquanto neste par nenhuma geometria tiver IC acima de zero, não encerrar com recusa visível: continuar a variar prazo, alvo e stop. Geometria em uso permanece.
