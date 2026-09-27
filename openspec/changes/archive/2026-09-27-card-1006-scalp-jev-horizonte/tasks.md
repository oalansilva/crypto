# Tasks — card-1006-scalp-jev-horizonte

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa. Pré-requisito #1008 (memória do stream ≥ 900 s). Não unificar #1008. Não reabrir #1001 (interruptor, T, clip, kill, GTX, chave Spot). Não reabrir #1007.

## 1. Lookback fixo 15 min (não cadência)

- [x] 1.1 — `horizon_s = 900` constante só para lookback rolante (últimos 15 min de `aggTrade` + toque actual; não vela OHLCV) e hold após fill. Sem selector no painel. Ligar A não muda o lookback de B (ambos últimos 15 min).
- [x] 1.2 — Interruptor, T, clip, kill, GTX e chave Spot de Meu Perfil permanecem como no #1001. Sem chave TypeSafe no painel, logs ou payload.

## 2. Cadência toque fresco e pedido Jev

- [x] 2.1 — Relógio de pergunta = toque fresco do stream (~1 s; não pedir ao Jev para ser mais rápido). Um pedido de cada vez; espera HTTP e teto de atraso **alinhados em 1,5 s**. Resposta até 1,5 s + demais gates → o ciclo pode enviar; > 1,5 s ou timeout → esse ciclo não envia. Depois da resposta, **antes** de enviar, revalidar livro fresco (`age_ms` ≤ 500 do #1008; fail-closed «livro indisponível»). **Não** sem teto. **Não** `horizon_s` como sleep. **Não** teto 1 consulta / 15 min. Com scalp ligado e sem posição: mais do que uma consulta dentro de 15 min é permitido. Com posição ou ordem de saída no livro → não chama Jev para entrada nova.
- [x] 2.2 — Payload exacto da decisão 5 do `design.md`: `horizon_s = 900` (lookback/hold, nunca cadência), `touch` (bid, ask, bid_qty, ask_qty, mid, spread_bp, microprice, imbalance, age_ms), `window` (horizon_s, trade_count, ret_bp, vol_bp, aggressor_flow, volume, spread_bp_mean), `account` (inventory_btc, t, remaining_to_t, fee_bp, bnb_fee_active), `resting` null ou `{side, price, age_ms, role}`. Perguntas: `side`, `expected_move_bp`, `book_toxic`. Sem `edge_after_fees`. Sem REST de livro/trades. Memória #1008 ≥ 900 s; janela vazia → pular o ciclo.
- [x] 2.3 — Hurdle de entrada no código: só entra se `expected_move_bp` > `2 × fee_bp + spread_bp`. `fee_bp` = 7,5 se `spotBNBBurn` e BNB livre > 0, senão 10. Movimento 10 bp com taxa 10 bp → nenhuma ordem. Hurdle de entrada não define alvo/stop.
- [x] 2.4 — Hold default; confiança < 0,7, livro tóxico, teto cheio e inventário 0 + SELL continuam a recusar.

## 3. Entrada e hold após fill

- [x] 3.1 — Entrada post-only no toque; sem fill em 10 s (configurável) cancela; não corre atrás; não vira mercado.
- [x] 3.2 — Saída obrigatória, a primeira: alvo default 35 bp, stop default −28 bp, tempo máximo 15 min **depois do fill**. Saída post-only. Sem fill até 15:30 → «posição presa». Sem ordem a mercado. Uma posição de cada vez. Kill −2 % de T continua a cancelar este bot.

## 4. Painel no Monitor

- [x] 4.1 — Módulo Scalp BTCUSDT no `/monitor` alinhado a `frontend/public/prototypes/card-1006-scalp-jev-horizonte/index.html`: lookback «últimos 15 min» como facto (como T/clip), hurdle, taxa em uso, alvo 35 bp, stop −28 bp, posição aberta (entrada, idade, alvo, stop) quando houver fill, último resultado bp e US$ (perda tão visível quanto ganho), aviso «posição presa» em 15:30. Sem rádio 1/2/5. **Sem** «Jev no máximo 1 vez / 15 min». Sem relógio de sono. **Sem** copy nova «1,5 s» / «800 ms» no Monitor (o painel já mostra ~1 s; o teto 1,5 s é comportamento de envio). Ligado sem posição: copy de toque fresco.
- [x] 4.2 — Sem medidores extra de imbalance/microprice. Sem régua #1007. Sem «estratégia lucrativa». Board intacta (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia). Operar intacto. Sem extras landing/Ajuda.

## 5. Testes e evidência

- [x] 5.1 — Testes dos critérios observáveis do issue #1006 (cadência toque fresco sem teto 1×/15 min, espera/teto 1,5 s: resposta a tempo + gates → pode enviar; > 1,5 s ou timeout → não envia; livro revalidado `age_ms` ≤ 500 depois da resposta; payload, hurdle 10 bp, posição presa 15:30 após fill, nunca duas compras, inventário 0 + SELL, kill, sem TypeSafe, sem rádio 1/2/5, painel sem «1 vez / 15 min» e sem copy «1,5 s»).
- [x] 5.2 — Playwright desktop+mobile do delta no `/monitor` contra o proto (lookback facto «últimos 15 min», toque fresco no ligado, hurdle/taxa, alvo 35, stop −28, posição após fill, último resultado negativo, «posição presa» 15:30).
- [x] 5.3 — `openspec verify` desta change.

## 6. T18 — SystemOne `expected_move_bp` como Score

- [x] 6.1 — Payload SystemOne: `expected_move_bp.type=score` com `criteria` ordenados (2–10 níveis em bp; hurdle ~20 e alvo 35 representáveis). Resposta: mapear `answers.expected_move_bp.score` → bp por interpolação linear entre índices; fallback legado `number`/`value`; sem score → 0. Testes unitários scalp Jev actualizados.
