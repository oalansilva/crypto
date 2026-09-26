## Context

Card **#1006**, Status=Design. Rework **3** após T6 (Alan devolveu de Aprovação de Design). Briefing = issue grelhado (Problema, História, Entra, Não entra). O body do GitHub ainda diz 800 ms (Aprovação de Design era read-only); o P0 T6 **prevalece** sobre essas frases. Sem PATCH do issue. Sem reentrevista. Sem reabrir Qs grelhadas. Sem reabrir o selector 1/2/5. Sem voltar ao horizonte de previsão ~2 s do #1001. Sem reabrir lookback ≠ cadência ≠ hold.

O Scalp BTCUSDT do **#1001** (Done) já vive no `/monitor` autenticado: interruptor por utilizador, T/clip/kill, post-only GTX, chave Spot de Meu Perfil. O pedido ao Jev em `scalp_jev._systemone_payload` manda só `symbol`, `bid`, `ask`, `inventory_btc`, `t` e pergunta `edge_after_fees` (sim/não nos ~2 s). O relógio de *pergunta* é `JEV_TARGET_MS = 1000` (~1 s / toque fresco) e **não muda** neste rework. `RestingOrder` tem `client_order_id`/`side`/`price` — o código cancela se o preço saiu do toque; o payload **não** inclui resting. Não há detecção de BNB (`FEE_HEADROOM = 0.001`). Livro ainda vai por REST `bookTicker` neste HEAD; o stream é **#1008** (card separado, pré-requisito Done técnico): `bookTicker` + `aggTrade` em memória, `age_ms` ≤ 500 para enviar, fail-closed «livro indisponível», sem REST de livro/trades neste card.

Impeccable (Operate): audience = operador autenticado com o scalp do #1001; outcome = ver lookback «últimos 15 min» como facto, cadência = toque fresco (sem sono 15 min), hold 15 min depois do fill (hurdle/taxa, alvo 35 bp / stop −28 bp, posição, último resultado por trade e o aviso «posição presa» em 15:30); direction = clone `/monitor` a partir do proto #1001 + delta só no módulo scalp; `DESIGN.md` permanece autoridade visual. Não redesenhar o Monitor nem o Operar. Este P0 **não** pede ecrã novo: o painel já mostra ~1 s; o teto 1,5 s é **quando o ciclo pode enviar**.

UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. `COPIED:start`/`COPIED:end` nas regiões clonadas. Delta fora desses blocos: módulo Scalp BTCUSDT já existente (lookback «últimos 15 min» como facto, hurdle, taxa, alvo 35, stop −28, posição após fill, último trade, «posição presa» em 15:30; **sem** «Jev no máximo 1 vez / 15 min»; **sem** copy «1,5 s» / «800 ms»). Sem extras `landing.html`/`ajuda.html`. Nunca ANTES/DEPOIS como URL canónica.

## P0 deste rework 3

Alan devolveu o design **só** para isto: o Entra manda skip se o Jev passar de 800 ms. Em DEV o Jev remoto (TypeSafe HTTP) anda **~1 s** (relógio do #1001; painel arredonda a 1 s; timeouts SSL/leitura ~0,97–1,16 s). Resultado observável: ciclos incrementam sinal, **0 envios**. Isto é contrato visível (**quando** o ciclo pode enviar), não detalhe de Apply nem ecrã novo.

Contrato que substitui as frases de 800 ms:

1. Cadência: um pedido de cada vez; o Farol **espera a resposta do Jev até 1,5 s** (acima do ~1 s do relógio e dos timeouts vistos).
2. Resposta **até 1,5 s** + demais gates (hold default, confiança, livro não tóxico, hurdle, teto, livro fresco #1008) → o ciclo **pode enviar**.
3. Resposta **> 1,5 s** (ou timeout) → esse ciclo **não envia**.
4. Espera HTTP e teto de atraso **alinhados** em 1,5 s. **Não** é sem teto.
5. Relógio de pergunta permanece ~1 s / toque fresco. **Não** pedir ao Jev para ser mais rápido.
6. `age_ms` ≤ 500 do #1008 **não** relaxa: revalidar livro fresco **depois** da resposta, **antes** de enviar.

Painel: **não** ganha copy «1,5 s» nem «800 ms». Continua «toque fresco» + lookback «últimos 15 min».

Teto 1+1+1: slot 1 = rework 1 (15 min fixo / selector); slot 2 = rework 2 (cadência ≠ lookback ≠ hold). Este 3.º rework só existe por este P0 novo de produto, justificado no prompt do pai.

## P0 fechado no rework 2 (não reabrir)

Alan recusou colar a cadência do pedido ao lookback/hold. Copy «Jev no máximo 1 vez / 15 min» **ausente**. Lookback rolante ≠ cadência toque fresco ≠ hold após fill. Sem sono 15 min. Sem teto 1 consulta / 15 min.

## P0 fechado no rework 1 (não reabrir)

Alan recusou o horizonte **escolhido pelo operador** (rádio 1/2/5). Continua travado: lookback **15 min fixos** (`horizon_s = 900` na janela e no hold). Sem selector. Sem voltar a 1/2/5. Sem voltar a prever ~2 s.

Geometria de saída: **alvo 35 bp**, **stop −28 bp**, hold 15 min após o fill, «posição presa» em **15:30**. Hurdle de *entrada* permanece `2 × fee_bp + spread_bp` e **não** define a saída.

## Goals / Non-Goals

**Goals:**

- Lookback fixo «últimos 15 min» (`horizon_s = 900` só na janela rolante e no hold). Não é escolha do operador. Painel mostra «últimos 15 min» como facto.
- Relógio de pergunta ao Jev = toque fresco do stream (~1 s). Um in-flight; espera HTTP e teto de atraso alinhados em **1,5 s**. Resposta até 1,5 s + demais gates → o ciclo pode enviar; > 1,5 s ou timeout → não envia. Depois da resposta, revalidar `age_ms` ≤ 500 antes de enviar. Com scalp ligado e sem posição/saída: pode haver mais do que uma consulta dentro de 15 min. **Não** teto 1 consulta / 15 min. **Não** `horizon_s` como sleep.
- Com posição ou saída no livro: não chama Jev para entrada nova; o código gere a saída. Hold = 15 min depois do fill.
- Pedido enriquecido com toque (quantidades + microprice + imbalance + idade) e agregados da janela rolante de 15 min a partir da memória do #1008; hurdle de entrada no código; pergunta «há vantagem depois da taxa» sai.
- Saída obrigatória post-only: alvo default 35 bp, stop default −28 bp, tempo máximo 15 min após o fill. Aviso «posição presa» se não preencher até 15:30. Uma posição de cada vez.
- Painel: lookback «últimos 15 min», hurdle, taxa em uso, alvo 35 bp, stop −28 bp, posição aberta (entrada, idade, alvo, stop) quando houver fill, último resultado por trade em bp e US$ (perda tão visível quanto ganho). Sem «1 vez / 15 min». Sem relógio de sono. Sem copy nova do teto 1,5 s.

**Non-Goals:**

- Reabrir interruptor, T, clip, kill, GTX, chave Spot (#1001).
- WebSocket, idade do toque no conector, recusa de fallback REST (#1008). Unificar #1008 neste card. Relaxar `age_ms` ≤ 500.
- Régua / calibração / histórico (#1007 Cancelado).
- Medidores extra de imbalance/microprice no painel. Copy nova «1,5 s» / «800 ms» no Monitor. Copy landing/Ajuda. Rota nova. Redesign da board ou do Operar.
- Ordem a mercado / IOC / trailing. Horizonte escolhido pelo operador (rádio 1/2/5). Lookback ≠ 15 min neste card. Sono de 15 min (teto 1 consulta Jev / 15 min). Segunda posição. Prometer P&L positivo. Voltar ao horizonte de previsão ~2 s do #1001.
- Pedir ao Jev para ser mais rápido. Mudar o relógio de pergunta (~1 s / toque fresco). Remover o teto (não é «sem limite»).
- Reabrir Qs grelhadas nem os *como* já fechados (janela vazia = pular, resting, BNB, nomes do payload, cadência ≠ lookback) salvo o **furo do teto 800 ms**.

## Decisions

1. **Janela de memória para lookback 15 min = 900 s no processo do stream #1008.** *(fechado no rework 1; lookback = rolante, não vela)*
   Contrato conjunto: o processo partilhado do stream retém **≥ 900 s** de `aggTrade` BTCUSDT **e** um anel de snapshots `bookTicker` a 1 Hz (≥ 900 s) para `spread_bp_mean`. Toque corrente continua a ser o último `bookTicker` (`age_ms` = agora − event time). Lookback = **sempre os últimos 15 min** de tape + toque de agora (janela rolante). **Não** é vela OHLCV de 15 min. Este card **não** abre WebSocket, **não** chama REST de livro/trades, **não** unifica o #1008. O Apply do #1008 alarga o buffer para 900 s; o Apply deste card só *lê* essa memória. Orçamento: BTCUSDT ~10² prints/s → ~9×10⁴ trades / 15 min + 900 snapshots; scan O(n) da janela de 900 s, **sem** deitar o tape cru no Jev.
   Alternativa rejeitada — **REST `/api/v3/aggTrades` por ciclo:** o Entra e o #1008 proíbem REST de livro/trades neste card.
   Alternativa rejeitada — **ficar nos ~5 s ou nos 300 s do pacote 1/2/5:** agregados de 15 min mentem; o *como* do issue pede ≥ 900 s.
   Alternativa rejeitada — **rádio 1/2/5 com buffer 300 s:** P0 do rework 1; Alan travou 15 min fixos.
   Alternativa rejeitada — **vela 15m OHLCV:** o Entra pede tape + toque de agora, não OHLCV.

2. **Janela sem negócios → pular o ciclo.** *(fechado; não reabrir)*
   Zero `aggTrade` na janela rolante de 15 min → não chama Jev, não envia ordem (`skip_reason = window_empty`). Zeros pareceriam «sem movimento»; omitir campos pediria ao modelo para inferir (o Entra manda o código calcular e enviar). Em BTCUSDT uma janela de 15 min vazia é quase sempre stream morto; o #1008 já segura se `age_ms` > 500.
   Alternativa rejeitada — **enviar zeros:** o modelo trata 0 como observação.
   Alternativa rejeitada — **omitir `window`:** inferência.

3. **Resting entra no payload; o código continua a cancelar/segurar.** *(fechado; não reabrir)*
   Hoje o payload não manda resting; `decide_cycle` cancela se `resting.price != toque`. Fecha-se: se houver ordem deste scalp no livro, `state.resting = { side, price, age_ms, role }` com `role` = `entry` | `exit`. Cancelar stale, recusar empilhar compra com posição ou saída no livro, e o timeout de fill (10 s entrada; 15 min + 30 s saída) **continuam no código**. O modelo vê o resting e **não** decide cancelar.
   Alternativa rejeitada — **só o código, omitir resting:** o Entra pede toque+conta visíveis ao modelo; uma limitadora no livro é estado de mercado.
   Alternativa rejeitada — **o modelo manda cancelar:** fura o contrato de Hold/código do #1001.

4. **BNB activo = `spotBNBBurn` e BNB livre > 0, cache com os saldos.** *(fechado; não reabrir)*
   HEAD não consulta BNB. `GET /api/v3/account` (já usado para USDT/BTC) traz `BNB.free`. `GET /sapi/v1/bnbBurn` (`USER_DATA`) traz `spotBNBBurn`. `bnb_fee_active` = os dois; `fee_bp` = `7.5` se activo, senão `10`. Cache fora do caminho crítico (mesma cadência dos saldos do #1008: cada N s ou após fill). Falha do `bnbBurn` → `fee_bp = 10` (sem desconto). O bot **não** liga o interruptor da Binance e **não** vende BNB. Hurdle de *entrada* = `2 × fee_bp + spread_bp` do toque actual (`spread_bp = (ask − bid) / mid × 10000`). Com BNB: `2 × 7,5 + spread`. Movimento esperado 10 bp com taxa 10 bp → nenhuma ordem (10 ≯ 20 + spread). Este hurdle **não** define alvo/stop.
   Alternativa rejeitada — **só `commissionRates` da account:** a taxa de VIP não reflecte o desconto BNB no fill.
   Alternativa rejeitada — **assumir 7,5 sempre:** o FAQ do #1001 exige BNB na Spot *e* o interruptor da Binance.

5. **Nomes exactos do payload (substitui `_systemone_payload`).** *(fechado; `horizon_s = 900` = lookback/hold, nunca cadência)*
   `state.symbol` = `BTCUSDT`. `state.horizon_s` = `900` (fixo; **não** ∈ `{60, 120, 300}`; **não** é intervalo de sleep entre pedidos).
   `state.touch`: `bid`, `ask`, `bid_qty`, `ask_qty`, `mid`, `spread_bp`, `microprice`, `imbalance`, `age_ms`.
   `microprice = (bid × ask_qty + ask × bid_qty) / (bid_qty + ask_qty)`; `imbalance = (bid_qty − ask_qty) / (bid_qty + ask_qty)`.
   `state.window`: `horizon_s`, `trade_count`, `ret_bp`, `vol_bp`, `aggressor_flow`, `volume`, `spread_bp_mean` — agregados da janela **rolante** dos últimos 900 s.
   `ret_bp` = `(last_price / first_price − 1) × 10000`; `vol_bp` = desvio-padrão dos retornos log × 10000; `aggressor_flow` = soma `qty` com sinal (+ taker buy / − taker sell, `aggTrade.isBuyerMaker`); `volume` = soma `qty`; `spread_bp_mean` = média dos snapshots 1 Hz.
   `state.account`: `inventory_btc`, `t`, `remaining_to_t`, `fee_bp`, `bnb_fee_active`.
   `state.resting` = `null` ou `{ side, price, age_ms, role }`.
   `questions`: `side` (BUY/SELL/HOLD), `expected_move_bp` (número, movimento esperado em bp nos próximos 900 s), `book_toxic` (bool). **Sem** `edge_after_fees`. Payload **sem** segredo TypeSafe. Orçamento: JSON < 2 KiB; montagem = um scan da janela de 900 s + toque corrente + conta em cache.

6. **Cadência = toque fresco; um in-flight. Hold = 15 min depois do fill. Painel descola os três papéis.** *(P0 do rework 2, fechado; único *como* reaberto então: cadência ≠ lookback)*
   Relógio de *pergunta* Jev = **toque fresco** do stream #1008. Com scalp ligado e **sem** posição nem ordem de saída: o loop consulta quando há toque fresco. **Um** pedido de cada vez (um in-flight). **Não** usa `horizon_s` como sleep. **Não** há teto de 1 consulta / 15 min: com o mercado a mexer pode haver mais do que uma consulta dentro de 15 min. Com posição aberta ou ordem de saída no livro: **não** chama Jev para entrada nova (o código gere a saída); não empilha compras. O teto de atraso da *resposta* (quando o ciclo pode enviar) é a decisão 7.
   `horizon_s = 900` **só** lookback (janela rolante) **e** hold (15 min depois do fill). Nunca cadência.
   Entrada: post-only no toque; sem fill em 10 s (configurável) → cancela; não corre atrás; não vira mercado. Saída, a primeira: alvo = **35 bp** (default), stop = **−28 bp** (default), tempo máximo = 15 min **após o fill**; também post-only no toque. Sem fill até **15:30** → painel «posição presa»; o utilizador decide; Operar continua. Kill −2 % de T continua a cancelar tudo deste bot.
   Painel acrescenta no módulo #1001: facto «últimos 15 min» (mesmo vocabulário dt/dd de T/clip; **sem** rádio 1/2/5; **sem** «Jev no máximo 1 vez / 15 min»; **sem** relógio de sono), hurdle, taxa em uso, alvo 35 bp, stop −28 bp, posição (entrada, idade, alvo, stop) **quando houver fill**, último resultado bp e US$ (`.neg`/`.pos` incumbentes), banner «posição presa» com 15:30. Calibração hits/signals do #1001 pode permanecer (não é a régua #1007). Sem medidores de imbalance/microprice. Sem copy landing/Ajuda neste card.
   Alternativa rejeitada — **1 consulta / 15 min (`horizon_s` como sleep):** P0 do rework 2; Alan recusou cola cadência↔lookback; o Jev perde o momento.
   Alternativa rejeitada — **voltar a `JEV_TARGET_MS = 1000` a prever ~2 s:** o problema do #1001 era o horizonte de previsão, não perguntar com o toque fresco; o pedido deste card é enriquecido sobre 15 min rolantes.
   Alternativa rejeitada — **selector 1/2/5:** P0 do rework 1.

7. **Espera HTTP e teto de atraso alinhados em 1,5 s; revalidar livro fresco depois da resposta.** *(P0 deste rework 3; único *como* reaberto agora: teto 800 ms)*
   Um pedido de cada vez. O Farol **espera a resposta do Jev até 1,5 s**. Espera HTTP e teto de atraso **alinhados** nesse 1,5 s — o mesmo número nos dois sítios, não dois relógios. **Não** é sem teto.
   Resposta **até 1,5 s** + demais gates (hold default, confiança, livro não tóxico, hurdle, teto de T, livro fresco #1008) → esse ciclo **pode enviar**. Resposta **> 1,5 s** ou timeout → esse ciclo **não envia**.
   Relógio de *pergunta* permanece o toque fresco / ~1 s (`JEV_TARGET_MS = 1000` do #1001). **Não** pedir ao Jev para ser mais rápido. **Não** mudar esse relógio.
   Depois da resposta e **antes** de enviar: revalidar livro fresco `age_ms` ≤ 500 (#1008, fail-closed «livro indisponível»). A espera de 1,5 s pode envelhecer o toque; o bound **não** relaxa.
   Painel: **não** acrescenta copy «1,5 s» nem «800 ms». O ~1 s visível continua a ser o relógio de pergunta; este P0 é comportamento de envio.
   Alternativa rejeitada — **manter skip 800 ms:** em DEV o Jev ~1 s (timeouts SSL/leitura ~0,97–1,16 s) → ciclos incrementam sinal e 0 envios.
   Alternativa rejeitada — **sem teto / esperar à vontade:** o Entra substitui 800 ms, não o remove.
   Alternativa rejeitada — **pedir ao Jev para ser mais rápido ou mudar o relógio ~1 s:** fora deste card; o relógio de pergunta já serve.
   Alternativa rejeitada — **relaxar `age_ms` ≤ 500 para caber a espera:** fura o fail-closed do #1008.

## Risks / Trade-offs

- [Risco] Apply deixa skip 800 ms ou timeout HTTP < 1,5 s → 0 envios com Jev ~1 s. Mitigação: P0 deste rework 3; decisão 7; spec de espera/teto alinhados em 1,5 s.
- [Risco] Apply espera 1,5 s mas envia com livro velho. Mitigação: revalidar `age_ms` ≤ 500 depois da resposta; #1008 fail-closed.
- [Risco] Apply remove o teto («sem limite»). Mitigação: decisão 7; spec «SHALL still be a cap».
- [Risco] Apply cola cadência a 900 s ou deixa copy «1 vez / 15 min». Mitigação: P0 do rework 2; decisão 6; spec de cadência = toque fresco; proto sem essa frase.
- [Risco] Apply volta ao relógio ~1 s a prever 2 s ou ao selector 1/2/5. Mitigação: Non-Goals; proto sem rádio; `horizon_s = 900` só lookback+hold.
- [Risco] Apply deixa `edge_after_fees` no payload. Mitigação: decisão 5; pergunta sai.
- [Risco] Apply amarra alvo/stop ao hurdle (pacote 1/2/5). Mitigação: P0 do rework 1; defaults 35/−28 no spec e no proto.
- [Risco] Painel ganha medidores de imbalance/microprice, régua #1007, ou copy «1,5 s». Mitigação: Non-Goals; proto sem esses textos.
- [Risco] «posição presa» vira ordem a mercado. Mitigação: Entra; spec; Operar continua a ser o caminho humano.
- [Risco] Landmark `7d` some no clone. Mitigação: COPIED do proto #1001; `data-landmark="7d"`.
- [Risco] Copy «estratégia lucrativa». Mitigação: ban no spec e no proto.

## Migration Plan

Sem coluna de horizonte escolhido pelo operador. `horizon_s = 900` constante no código para lookback e hold (MAY gravar o constante em `scalp_user_states` para telemetria — P3). Cadência **não** persiste intervalo de 15 min; o loop pergunta no toque fresco. Espera/teto de resposta = 1,5 s (P3: onde gravar o número). Default do interruptor continua desligado. Rollback = esconder o delta de lookback/saída, voltar à cadência #1001, cancelar resting deste bot. Chaves Spot intactas. Sem migração de favoritos. Sem copy landing/Ajuda a reverter.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-1006-scalp-jev-horizonte/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- `/monitor` (`index.html`): módulo Scalp BTCUSDT acima dos KPIs; lookback **«últimos 15 min»** como facto (como T/clip), **sem** rádio 1/2/5; **sem** «Jev no máximo 1 vez / 15 min»; **sem** relógio de sono; **sem** copy «1,5 s» / «800 ms»; hurdle em bp + taxa em uso; alvo default 35 bp e stop default −28 bp visíveis; posição aberta (entrada, idade, alvo, stop) quando houver fill; último resultado por trade em bp e US$ (perda tão visível quanto ganho); aviso «posição presa» em 15:30; sem medidores extra de imbalance/microprice; sem régua #1007; sem «estratégia lucrativa»; landmarks `table.signals` + Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia; coluna Operar e modal Operar intactos.
- Interruptor / T / clip / kill / GTX / chave Spot do #1001 intactos.
- Sem extras landing/Ajuda. Sem rota nova.
- `horizon_s = 900` só lookback + hold. Cadência = toque fresco, um in-flight; espera HTTP e teto de atraso alinhados em 1,5 s; resposta a tempo + gates → pode enviar; > 1,5 s ou timeout → não envia; revalidar `age_ms` ≤ 500 depois da resposta. Sem teto 1 consulta / 15 min. Memória #1008 ≥ 900 s. Hurdle de entrada = `2 × fee_bp + spread_bp`. Saída 35 / −28 / 15 min após o fill.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Persistência do constante `horizon_s = 900` vs só constante no código; colunas `position_opened_at` / `rest_opened_at` / `last_trade_bp` / `last_trade_quote` / `stuck`.
- Mapeamento SystemOne de `expected_move_bp` (número vs choice).
- Fórmula exacta de `vol_bp` (amostra vs população) e unidade de `aggressor_flow` (qty vs quote).
- TTL da cache `bnbBurn` + saldos.
- Wording exacto do facto «últimos 15 min», do status «toque fresco» e do banner «posição presa» (o proto manda o visível).
- Overlay vs faixa do módulo — incumbente #1001.
- Detector `side-tab` / clip Operar 1280 — incumbente do clone.
- Fixtures do proto («Simular posição», «Simular preso», kill, sem chave).
- Nome interno da espera/teto de 1,5 s (HTTP e skip alinhados no mesmo número; não inventar nome no issue).

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-1006-scalp-jev-horizonte/` → `frontend/public/prototypes/card-1006-scalp-jev-horizonte/index.html`. Clone da página viva `/monitor` (base proto #1001 + incumbente `MonitorStatusTab` / `DESIGN.md`) + delta só no módulo scalp (selector 1/2/5 **ausente**; lookback «últimos 15 min»; **sem** «1 vez / 15 min»; **sem** copy «1,5 s» / «800 ms»; alvo 35; stop −28; preso 15:30; posição após fill). HTML **não** contradiz o contrato de envio (o teto 1,5 s não é ecrã); sem delta HTML neste rework 3.
- Sem extras landing/Ajuda. Sem painel ANTES/DEPOIS no index.
- `cp`/clone = copied; delta de lookback/cadência/saída/resultado = generated.

## Prototype Validation

- **Comando (autor rework 3):** verificação limitada (não onda A/B) — Playwright Chromium contra `https://dev.criptofarol.com.br/prototypes/card-1006-scalp-jev-horizonte/` (servidor de protos lê o worktree; live == local). Desktop 1280×800 e mobile 390×844. Default lookback «últimos 15 min» + desligado → ligar (toque fresco, **sem** «1 vez / 15 min», **sem** «1,5 s» / «800 ms») → posição (alvo 35 / stop −28 / hold após fill) → último resultado negativo → «posição presa» 15:30 → kill → sem chave. Selector 1/2/5 ausente. Digest e `clone_gate_ok` no disco após o proto.
- **URL canónica:** `frontend/public/prototypes/card-1006-scalp-jev-horizonte/index.html` (HTTP DEV: `https://dev.criptofarol.com.br/prototypes/card-1006-scalp-jev-horizonte/`). Sem extras landing/Ajuda. HTML não vai no Gist.
- **Digest (UTF-8 sha256, gate deste autor):**
  - `index.html` `41a906cfe8f7f605389bed6c132323cec331111410295ceb90aa596988f1c766` · 51522 B = 21077 copied + 30445 generated. Pares `COPIED:start`/`COPIED:end`: 10/10; soma UTF-8 copiada 21077 (> 0). T5 mede só este index.html. `design_clone_gate.classify` = PASS; landmarks `/monitor` ok. `clone_gate_ok` local True.
- **browser_gate:** verificação limitada do autor rework 3 · viewports 1280×800 e 390×844 · screenshots em `.impeccable/critique/1006-rework3-autor-*-off|on|pos|loss|stuck|kill|nokey.png`. Assessment A/B no pai.
- **Detector Impeccable:** `detect.mjs --json` → advisory `em-dash-overuse` (8 em-dashes, placeholders «—» de vazio; exit 0). Não é P0 de produto.

## Open Questions

Nenhuma. Fronteira veio grelhada. Os *como* já fechados (janela vazia = pular, resting, BNB, nomes do payload, cadência = toque fresco) mantêm-se. O furo do teto 800 ms fecha neste rework 3: espera HTTP e teto de atraso alinhados em 1,5 s; livro fresco revalidado depois da resposta.

## Impeccable

Mode Operate. `DESIGN.md` não sobrescrito. Snapshot curto do autor rework 3; onda A/B no pai.

- audience: operador autenticado no Monitor com o scalp do #1001
- outcome: lookback «últimos 15 min» (facto), cadência toque fresco (sem sono 15 min), hold 15 min após fill, hurdle/taxa, alvo 35 / stop −28, posição, último trade, «posição presa» em 15:30; envio possível com Jev até 1,5 s (sem copy nova no painel)
- direction: clone `/monitor` + delta no módulo scalp; tokens incumbentes; sem selector; sem «1 vez / 15 min»; sem copy «1,5 s»
- scope: lookback rolante 15 min + cadência toque fresco + espera/teto 1,5 s + pedido enriquecido + hold 35/−28 após fill; board e Operar intactos; landing/Ajuda fora

Design Agent verdict: PASS (autor rework 3; crítica dual no pai)

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla + 1 rework (slot 1 = rework 1, 15 min fixo; slot 2 = rework 2, cadência ≠ lookback). **Rework 3** com P0 novo de produto justificado no prompt (Alan / skip 800 ms → espera e teto 1,5 s / 0 envios em DEV). Sem quarto rework; sem P0 novo após esta dupla ⇒ sem segundo rework desta visita.

Relatórios rework 3: `.impeccable/critique/1006-card-1006-scalp-jev-horizonte-assessment-A.md` · `1006-card-1006-scalp-jev-horizonte-assessment-B.md`. Snapshot T7 = Assessment A. Verdict A/B: **PASS**.

**P0:** nenhum
**P1:** nenhum
**P2:** nenhum

**P0 deste rework 3 (fechado no OpenSpec; ecrã intocado):** skip 800 ms sai. Espera HTTP e teto de atraso alinhados em 1,5 s. Resposta a tempo + gates → pode enviar. > 1,5 s ou timeout → não envia. Livro fresco revalidado depois da resposta. Sem copy nova «1,5 s» no Monitor.

**P0 rework 2 (fechado):** «Jev no máximo 1 vez / 15 min». Lookback rolante ≠ cadência toque fresco ≠ hold após fill.

**P0 rework 1 (fechado):** rádio 1/2/5; 15 min fixos; alvo 35 bp; stop −28 bp; preso 15:30.

**P3 (aceitos, detalhe de Apply — não reabrir como P0/P1):**
- Fixtures proto («Simular posição» / «Simular preso» / kill / nokey / BNB).
- Clip Operar a 1280/1440; busca truncada a 390; cards mobile; thead «Gráfico» + `data-landmark="7d"` vs yaml `7d`; th Operar vs `actions-cell` — incumbente do clone.
- `DELTA:start=0`; detector `em-dash-overuse`; stitch Playwright mobile `fullPage`.
- Persistência `horizon_s = 900` (lookback+hold), payload Jev, cadência toque fresco / um in-flight / espera-teto 1,5 s, revalidar `age_ms` ≤ 500 e memória #1008 ≥ 900 s — Apply.
- Nome interno da espera/teto 1,5 s (`JEV_LATE_MS` HEAD 800) — Apply alinha HTTP e teto em 1,5 s.
- stuck/kill sem `role=alert` próprio; calibração #1001 permanece (não é régua #1007).
- Body do GitHub ainda diz 800 ms (Aprovação de Design era read-only); Gist/OpenSpec mandam 1,5 s.

**Disposition:** P3 → Apply. Não reabrir Qs grelhadas, interruptor/T/clip/kill, #1007, unificar #1008, extra `/favorites` / landing, selector 1/2/5, previsão ~2 s, sono 1 consulta / 15 min, skip 800 ms.

**Tokens (rubrica D4):** `UI impact: affected` · `live_route: /monitor` · `surface: existing`. Clone `/monitor` + delta só no módulo scalp. Proto HTTPS 200, digest `41a906cfe8f7f605389bed6c132323cec331111410295ceb90aa596988f1c766` · 51522 B = 21077 copied + 30445 generated. Landmarks PASS.

Spawns (rework 3): 3
proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
