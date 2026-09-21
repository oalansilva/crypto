## Why

Quem liga o Scalp BTCUSDT do #1001 sofre em duas frentes: o Jev cicla a cada ~1 s sobre os próximos ~2 s só com bid, ask, inventário e teto — o Farol já recebe as quantidades do toque e deita-as fora, sem imbalance, microprice nem fluxo — e devolve HOLD; e mesmo a acertar o lado, a taxa Spot (10 bp por lado, 7,5 com BNB; ida e volta 20 bp) é maior que o movimento típico em 2 s (~1,4 bp), sem alvo, stop nem tempo máximo de saída.

## Problema

Quem liga o Scalp BTCUSDT do #1001 sofre em duas frentes: o Jev cicla a cada ~1 s sobre os próximos ~2 s só com bid, ask, inventário e teto — o Farol já recebe as quantidades do toque e deita-as fora, sem imbalance, microprice nem fluxo — e devolve HOLD; e mesmo a acertar o lado, a taxa Spot (10 bp por lado, 7,5 com BNB; ida e volta 20 bp) é maior que o movimento típico em 2 s (~1,4 bp), sem alvo, stop nem tempo máximo de saída.

## História

Como operador com o scalp ligado, quero que o Farol olhe sempre os últimos 15 min de mercado (tape + toque de agora, janela rolante via stream), pergunte ao Jev com o mercado a mexer — não a cada 15 min — e, se entrar, espere até 15 min para ver se a chamada estava certa (alvo 35 bp, stop −28 bp, ou o tempo), com pedido enriquecido (toque com tamanho, microestrutura já calculada, agregados desses 15 min) — para o resultado por trade (bp e US$) ser observável, em vez de taxa garantida nos ~2 s ou de um sono de 15 min que perde o momento, sem eu escolher 1/2/5 e sem esperar a régua do #1007.

## Entra

**Quem e o que fica do #1001**
- Interruptor, T = min(US$ 100, USDT livre), clip US$ 10, kill −2 % de T, post-only e chave Spot de Meu Perfil não mudam neste card.
- Hold continua o default. Código continua a recusar confiança < 0,7, livro tóxico, teto cheio; inventário 0 não vende o piso.
- Sem chave TypeSafe no painel, logs ou registo. Payload de mercado não inclui segredo.

**Lookback, cadência e tempo da posição (três papéis)**
- Lookback fixo: sempre os últimos 15 min de negócios + o toque actual (janela rolante). Não é vela OHLCV de 15 min. Não é escolha do operador. O painel mostra «últimos 15 min» como facto (como T e clip), sem rádio 1/2/5.
- Cadência do Jev: com o scalp ligado e **sem** posição nem ordem de saída, consulta com o toque fresco (stream #1008). Um pedido de cada vez; o Farol espera a resposta do Jev até 1,5 s; resposta até 1,5 s + demais gates → o ciclo pode enviar; resposta > 1,5 s (ou timeout) → esse ciclo não envia. **Não** espera 15 min para perguntar. **Não** há teto de 1 consulta / 15 min.
- Com posição aberta ou ordem de saída no livro: não chama Jev para entrada nova; o código gere a saída.
- Tempo da posição: se entrar, 15 min para alvo / stop / tempo. Isso só conta **depois do fill**.

**Pedido ao Jev (enriquecido)**
- O código calcula e envia (não pede ao modelo para inferir): toque com tamanho (bid, ask, quantidades), meio, spread, microprice, imbalance do toque, idade do toque; agregados da janela rolante de 15 min a partir da memória do #1008 (retorno, vol, fluxo agressor, volume, spread médio); conta (inventário, teto, restante até T, taxa maker em uso).
- Perguntas: lado (BUY/SELL/HOLD), movimento esperado em bp nos próximos 15 min, livro tóxico. A pergunta sim/não «há vantagem depois da taxa» sai.
- Hurdle no código: só entra se o movimento esperado > 2 × taxa + spread (com BNB activo, 2 × 7,5). Painel mostra o hurdle em bp e a taxa em uso. Movimento esperado abaixo do hurdle → sem ordem mesmo com BUY.

**Entrada e saída**
- Entrada continua post-only no toque (compra no bid, venda no ask). Se não preencher em 10 s (configurável), cancela; não corre atrás do preço; não vira mercado.
- Saída obrigatória por posição, a primeira que vier: alvo (default 35 bp), stop (default −28 bp), tempo máximo = 15 min após o fill. Saída também post-only no toque; se não preencher até 15 min + 30 s, o painel mostra «posição presa» e o utilizador decide (Operar continua disponível). Sem ordem a mercado neste card.
- Uma posição de cada vez por utilizador. Não empilha compras enquanto há posição ou ordem de saída no livro.

**Painel deste card**
- Mostra: lookback «últimos 15 min» (facto, sem selector e sem «1 vez / 15 min»), hurdle, posição aberta (entrada, idade, alvo, stop), último resultado por trade em bp e em US$. Perda tão visível quanto ganho. Sem «estratégia lucrativa».
- Não ganha medidores extra de imbalance/microprice — isso vai no pedido ao modelo. Histórico de ciclos / régua (#1007) não entra neste momento.

**Calibração e pré-condição**
- #1007 está Cancelado e não será implementado neste momento. Este card não reaproveita régua, não espera calibração em 1 min / 5 min / 15 min, e não bloqueia Aprovação de Design à espera do #1007.
- Este card mostra lookback de 15 min e, por trade fechado, resultado em bp e US$. 0 acertos continua possível (não é DoD de P&L). Sem régua de acerto por horizonte neste card.

**Critérios observáveis**
- Scalp ligado **sem** posição: pode haver mais do que uma consulta Jev dentro de 15 min (toque fresco, um pedido de cada vez).
- Painel **não** mostra «Jev no máximo 1 vez / 15 min». Mostra lookback «últimos 15 min».
- Pedido ao Jev contém toque com quantidades, microprice, imbalance, agregados da janela rolante de 15 min e taxa em uso.
- Movimento esperado = 10 bp com taxa 10 bp → nenhuma ordem.
- Compra preenchida sem alvo/stop em 15 min → ordem de saída no livro e, se não preencher em 15:30, aviso «posição presa».
- Com posição ou saída no livro → nenhuma consulta Jev de entrada nova.
- Sem rádio 1/2/5 no painel.
- Nunca duas compras abertas. Inventário 0 + SELL continua a não vender o piso.
- Kill −2 % de T continua a cancelar tudo deste bot e parar.
- Sem chave TypeSafe no painel, logs ou registo.

**Para o Design fechar (*como*; não bloqueia a história)**
- Memória do #1008 para a janela rolante: ≥ 900 s de `aggTrade` + snapshots `bookTicker` a 1 Hz — sem REST de livro/trades neste card.
- Relógio de pergunta ao Jev = toque fresco do stream (não `horizon_s` como sleep). Um in-flight; o Farol espera até 1,5 s; > 1,5 s (ou timeout) skip. Relógio de 15 min só na posição aberta.
- Janela vazia → pular o ciclo; resting; BNB; nomes do payload — já fechados; não reabrir salvo o furo da cadência.

## Não entra

- Reabrir ou reescrever o #1001 (interruptor, T, clip US$ 10, kill, GTX, chave Spot).
- Calibração, régua e histórico de ciclos (#1007, Cancelado; não será implementado neste momento). WebSocket, idade do toque e recusa de fallback REST (#1008).
- Unificar #1007 ou #1008 neste card. Não reabrir o #1007.
- RSI / médias / Bollinger / velas OHLCV de 15 min; livro L2–L500; tape completo; notícias em texto.
- Ordem a mercado, IOC, trailing, martingale, DCA, alavancagem, futuros, segundo par.
- Horizonte escolhido pelo operador (rádio 1/2/5). Lookback ≠ 15 min neste card. Sono de 15 min (teto 1 consulta Jev / 15 min).
- Múltiplas posições simultâneas; formador de mercado; segundo pedido Jev em paralelo.
- Medidores extra de imbalance/microprice no painel do Monitor.
- Redesenhar o Operar; consola TypeSafe; backtest do Jev.
- Prometer P&L positivo: o DoD é o mecanismo observável, não o resultado.


## What Changes

- Três papéis de «15 min», descolados. **Lookback** = sempre os últimos 15 min de `aggTrade` + toque actual (janela rolante; memória #1008 ≥ 900 s + snapshots `bookTicker` 1 Hz). Não é vela OHLCV 15m. O painel mostra «últimos 15 min» como facto (como T e clip), sem rádio 1/2/5.
- **Cadência Jev** = com scalp ligado e **sem** posição nem ordem de saída: consulta com o **toque fresco** do stream. Um pedido de cada vez; o Farol espera a resposta até 1,5 s (espera HTTP e teto de atraso alinhados). Resposta até 1,5 s + demais gates → o ciclo pode enviar; > 1,5 s ou timeout → não envia. Depois da resposta, revalidar livro fresco (`age_ms` ≤ 500 do #1008) antes de enviar. **NÃO** `horizon_s` como sleep. **NÃO** teto 1 consulta / 15 min. **NÃO** sem teto. Relógio de pergunta permanece ~1 s / toque fresco. Com posição ou saída no livro: não chama Jev para entrada nova.
- **Hold** = 15 min **depois do fill** (alvo default 35 bp, stop default −28 bp, preso 15:30). Hurdle de entrada permanece `2 × fee_bp + spread_bp` e **não** define a saída.
- `horizon_s = 900` só lookback + hold, nunca cadência. Pedido ao Jev enriquecido: toque com tamanho, meio, spread, microprice, imbalance, idade; agregados da janela rolante a partir da memória #1008; conta. Perguntas: lado (BUY/SELL/HOLD), movimento esperado em bp nos próximos 15 min, livro tóxico. A pergunta sim/não «há vantagem depois da taxa» sai.
- Entrada continua post-only no toque; sem fill em 10 s (configurável) cancela; não corre atrás; não vira mercado. Saída obrigatória (primeira que vier): 35 / −28 / 15 min após o fill. Sem ordem a mercado. Uma posição de cada vez.
- Painel no módulo Scalp BTCUSDT já existente em `/monitor`: lookback «últimos 15 min» (facto), hurdle, taxa, alvo 35 bp, stop −28 bp, posição aberta (entrada, idade, alvo, stop) quando houver fill, último resultado por trade em bp e US$ (perda tão visível quanto ganho). **Não** mostra «Jev no máximo 1 vez / 15 min» nem relógio de sono. Sem medidores extra de imbalance/microprice. Sem régua #1007. Sem «estratégia lucrativa». Sem selector 1/2/5.
- Interruptor, T, clip, kill, GTX e chave Spot do #1001 não mudam. Copy landing/Ajuda não muda. #1008 permanece card separado (pré-requisito stream; memória ≥ 900 s). Sem REST de livro/trades neste card. Sem unificar #1008.

## Capabilities

### New Capabilities

- `scalp-jev-horizonte`: lookback rolante 15 min (`horizon_s = 900` só janela + hold), cadência = toque fresco (um in-flight, espera e teto de atraso alinhados em 1,5 s, sem teto 1×/15 min), payload enriquecido (toque + agregados da memória #1008 + conta), hurdle de entrada no código, saída post-only com alvo 35 bp / stop −28 bp / hold 15 min após o fill, uma posição, aviso «posição presa» em 15:30.
- `scalp-monitor-horizonte`: campos visíveis no módulo Scalp BTCUSDT já existente em `/monitor` (lookback «últimos 15 min» como facto, hurdle, taxa em uso, alvo 35 bp, stop −28 bp, posição aberta após fill, último resultado bp/US$, «posição presa») sem «1 vez / 15 min», sem redesenhar board nem Operar e sem rádio 1/2/5.

### Modified Capabilities

- `monitor`: o workbench `/monitor` continua a hospedar o módulo de scalp; a board (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) e o Operar permanecem; este card só acrescenta o delta de lookback 15 min / cadência toque fresco / hold após fill no módulo já existente.

## Impact

- Frontend: `ScalpModule` no `/monitor` autenticado mostra lookback «últimos 15 min» como facto, hurdle, taxa, alvo 35 bp, stop −28 bp, posição (idade/alvo/stop) quando houver fill e último trade. Sem selector. Sem copy «1 vez / 15 min». Board e Operar intactos. Sem extras landing/Ajuda. Sem rota nova.
- Backend: relógio de pergunta = toque fresco (~1 s; um in-flight; espera HTTP e teto de atraso alinhados em 1,5 s); após a resposta, revalidar `age_ms` ≤ 500 antes de enviar; `horizon_s = 900` só lookback + hold; payload Jev; hurdle de entrada; saída obrigatória 35/−28 / 15 min após o fill. Consome a memória do stream #1008 (janela ≥ 900 s). Sem REST de livro/trades. Sem reabrir T/clip/kill/GTX/chave Spot. Sem copy nova «1,5 s» no Monitor.
- Binance: continua Spot BTCUSDT post-only (GTX) da conta do utilizador. Sem mercado/IOC. Desconto BNB lido por conta (fora do caminho crítico).
- Protótipo: clone canónico de `/monitor` a partir do proto #1001 + delta só no módulo scalp. URL `frontend/public/prototypes/card-1006-scalp-jev-horizonte/index.html`.
- #1008 permanece separado. #1007 Cancelado — sem régua/calibração/histórico neste card.
