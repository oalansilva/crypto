## Context

Card **#1025**, Status=Design, cliente dsh. Briefing = issue grelhado (`## Problema`, `## História`, `## Entra`, `## Não entra` + `## Critérios observáveis` + `## Evidência`), copiado **verbatim** em `proposal.md`; sem reentrevista. Relacionado com **#1015** (log de diagnóstico do Jev — a evidência de 23/09, 766 respostas / 17 min, é deste card), **#1006** (horizonte de 900 s), **#1008** (estado fresco) e **#1001** (scalp direcional); #1001/#1006/#1008 não se reabrem e a régua #1007 fica como está (**Cancelado**) — o **Card A** substitui-a com os dados do log do #1015. **SEM-TELA** (backend/harness: régua, custo, gates e saída do scalp Jev).

Factos do código actual (lidos no repo, sem alterar nada):

- `backend/app/services/scalp_engine.py` é o módulo **puro** (sem I/O, sem env) das regras do scalp — bloco de constantes em `scalp_engine.py:11–26`: `CONFIDENCE_MIN = Decimal("0.7")`, `HORIZON_S = 900`, `JEV_LATE_MS = 1500`, `JEV_FLOOR_MS = 400`, `JEV_TARGET_MS = 1000`, `ENTRY_REST_TIMEOUT_S = 10`, `EXIT_TARGET_BP = Decimal("35")`, `EXIT_STOP_BP = Decimal("-28")`, `HOLD_AFTER_FILL_S = 900`, `STUCK_AFTER_FILL_S = 930`, `ORDER_TYPE = "LIMIT"`, `TIME_IN_FORCE = "GTX"`.
- `decide_cycle` (l.164–382) fecha o ciclo, por ordem, com os tokens `halted`/`switch_off` → `no_spot_key` → `kill` → `position_open` → `jev_in_flight` → `jev_unavailable` → `jev_target` (`last_jev_elapsed_ms < JEV_TARGET_MS`, l.250) → `need_jev` → `jev_late` (`jev.latency_ms > JEV_LATE_MS`, l.267) → `hold` (`side is None`, l.282) → `low_confidence` (`confidence < CONFIDENCE_MIN`, l.285) → `hurdle` (`not passes_entry_hurdle(jev.expected_move_bp, fee_bp, spread_bp)`, l.293) → `toxic_book` (l.306) → `t_zero` → `ceiling_reduce_only` → `zero_inventory` → `would_cross` → `dust`. Não há **nenhum** gate de regime explícito: a previsão só é comparada com o custo no `hurdle` (sem folga).
- `decide_exit_cycle` (l.415–493): `halted`/`switch_off` → `exit_resting` → **`stuck`** (`should_mark_stuck`, `seconds_since_fill >= 930`, l.411 — devolve `send=False` **sem ordem**) → `hold_position` → `would_cross`. `should_post_exit` (l.399–408) posta a saída passiva quando `ret_bp >= 35` **ou** `ret_bp <= -28` **ou** `seconds_since_fill >= 900` (fim da janela de espera). **Ordem que prende a posição:** o ramo `if resting is not None → skip_reason="exit_resting"` (l.445–452) devolve **antes** do `if stuck:` (l.453–460); com a saída passiva postada aos 900 s e não preenchida, o ciclo fecha em `exit_resting` e o ramo do `stuck` nunca é alcançado — é este corte que tem de ser reordenado para o escape agressivo ser alcançável (decisão 6). A marca `stuck` (`should_mark_stuck`, l.411) alimenta apenas o indicador «posição presa» do painel/status (`scalp_service.py` l.669–670 e l.1099) e mantém esse significado.
- `backend/app/services/scalp_window.py`: `entry_hurdle_bp(fee_bp, spread_bp) = 2 × fee_bp + spread_bp` (l.118–119) e `passes_entry_hurdle(expected_move_bp, …) = expected_move_bp > hurdle` (l.122–123). `window_metrics` produz `trade_count`, `ret_bp`, `vol_bp` (σ dos log-returns), `aggressor_flow`, `volume`, `spread_bp_mean`; `touch_metrics` produz `spread_bp`, `microprice`, `imbalance`, `age_ms`.
- `backend/app/services/scalp_service.py::_fee_terms` (l.249–251) é **stub**: devolve sempre `(Decimal("10"), False)` (docstring: «failure → 10 bp without discount»). É chamado em `_run_cycle` (l.655) e no construtor do status (l.1085), onde `hurdle_bp = entry_hurdle_bp(fee_bp, spread_bp)` (l.1095) e a mensagem mostra «7,5 if bnb_fee_active else 10 bp» (l.1111). `tick_user` (l.547) fecha o ciclo via `_run_cycle` e regista a recusa (`log_cycle_refusal`) quando `result.skipped` é não nulo. No caminho pós-chamada, `decide_cycle` recebe `last_jev_elapsed_ms=max(JEV_TARGET_MS, int(signal.latency_ms))` (l.856) e `state.last_jev_latency_ms = int(signal.latency_ms)` (l.829).
- `backend/app/services/scalp_jev.py`: a ladder vive em `_EXPECTED_MOVE_BP_LEVELS_BP = (0, 5, 10, 15, 20, 25, 30, 35, 50, 80)` (l.36) e `_bp_from_score` (l.48–64) interpola linearmente. `_systemone_payload` (l.151–182) monta `state` + `model: jev-latest` + `questions` com `side` (choice), `expected_move_bp` (type `score`, cujo campo `criteria` são as 10 frases longas de `_expected_move_bp_criteria`) e `book_toxic` (type `noul`). `_side_confidence` (l.189–200) lê `side_answer.confidence` e, se ausente, `probabilities[choice]`. Em `request_jev` (l.263) o cronómetro `started = time.perf_counter()` abre **antes** de `log_call_entry` (l.283) — o registo de entrada do #1015 corre **dentro** da latência medida que alimenta o gate fail-closed `jev_late` (é o P1 residual do review do #1015).
- `backend/app/services/scalp_jev_payload.py::build_jev_payload` transporta `state` = símbolo, `horizon_s`, `touch{...}`, `window{agregados}`, `account{inventory_btc, t, remaining_to_t, fee_bp, bnb_fee_active}` e `resting`; recusa com `no_book`/`window_empty` antes de chamar o Jev. O `window` já vai como agregados — o corpo fixo do `questions`/`criteria` é o que engordou o input: as 10 frases do Score entraram em `0a14cb49` (`fix(#1006): mapear expected_move_bp como Score no SystemOne`), a acompanhar o crescimento medido no #1015 (467 → 1.158 tokens; a medição exacta faz-se no Apply).
- `backend/app/services/scalp_loop.py`: `interval = max(JEV_FLOOR_MS/1000.0, 0.4)` = 0,4 s, e o loop corre **uma** chamada em voo por utilizador. Instala o log de diagnóstico do #1015 (`install_diagnostic_log`, armado por `RUN_SCALP_LOOP`).
- `backend/app/services/scalp_jev_log.py` (#1015, já existe): ficheiro **único** com tecto `MAX_LOG_BYTES = 200 * 1024 * 1024` e truncagem de cauda, caminho `backend/scalp_jev_diagnostic.log` (`SCALP_JEV_LOG_FILE`), nível `SCALP_JEV_LOG_LEVEL`, armado por `SCALP_JEV_LOG_ENABLED`/`RUN_SCALP_LOOP`, registos com `%(asctime)s` (logo, há timestamp para a régua). Expõe `log_call_entry` / `log_call_return` (com `side`, `expected_move_bp`, `score`, `book_toxic`, `confidence`), `log_call_error` e `log_cycle_refusal` (token cru).
- `backend/app/services/scalp_binance.py` só tem caminho **passivo**: docstring «Post-only LIMIT/GTX only», `place_post_only` (mais cancel/query). **Não existe** ordem `MARKET`/IOC no cliente de scalp.
- `backend/app/services/binance_spot_orders.py::signed_request` (l.55) aceita `path` arbitrário sobre `BINANCE_BASE_URL` (default `https://api.binance.com`), logo serve `GET /api/v3/account` (`commissionRates.maker`) e `GET /sapi/v1/bnbBurn` (`spotBNBBurn`, SAPI) — há precedente de `/sapi/v1/...` em `binance_spot.py` (l.91–92). `public_get`, `get_symbol_info`, `fetch_free_balance`, `list_open_orders` completam o cliente.
- Dados para a régua: `scripts/scalp_jev_eval.py` **não existe** (o Card A cria-o); `backend/scalp_jev_diagnostic.log` ainda não existe no worktree (nasce no runtime-worker DEV). O realizado a 900 s sai do OHLCV já existente (`backend/app/services/ohlcv_storage.py::read_recent_candles`/`read_all_candles`, `canonical_candle_service`, `binance_service.get_klines`).
- DEV: `ops/systemd/criptofarol-dev-runtime-worker.service` arma `RUN_SCALP_LOOP=1` (o mesmo flag que arma o log de diagnóstico do #1015).

UI impact: none
live_route: N/A backend/harness do scalp Jev; não há tela de produto neste card
surface: new

Sem rota autenticada, sem landing, sem HTML. Nunca emprestar `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select` nem `landing`. Prototype N/A. Impeccable N/A. Nota de leitura do gate: `surface: new` refere-se à **nova capability de backend** (régua de avaliação, custo maker, gates de entrada e escape de saída do scalp Jev — um contrato de decisão novo), **não** a uma superfície de tela nova; `UI impact: none` e `live_route: N/A` mantêm-se, e não há tela, rota ou protótipo neste card.

## Vocabulário

- **Régua / Card A:** `scripts/scalp_jev_eval.py`, read-only, sobre o log de diagnóstico do #1015 e o realizado a 900 s; reporta o que a confiança e a previsão efectivamente valem. **Gate** de todas as calibrações deste card.
- **Janela de espera:** os 15 min após o fill (`HOLD_AFTER_FILL_S = 900 s` — valor de **produto** fixado na grelha de 23/09, fora da recalibração do Card A) — o período em que a saída é passiva; no seu fim a posição não pode ficar sem tentativa de saída.
- **Escape agressivo:** ordem de saída `MARKET`/IOC **sem teto de preço**, disparada no **primeiro ciclo em que o fim da janela de espera é atingido** sem preenchimento passivo (não na marca `stuck` dos 930 s).
- **Gate de regime (`skip_reason="regime"`):** não entrar quando a previsão não cobre o **custo maker + 50% de folga** (`entry_hurdle_bp × 1,5`).
- **Custo maker real:** taxa maker por perna lida da conta (`commissionRates.maker`) com o estado BNB (`spotBNBBurn`), em vez do stub taker de 10 bp; o hurdle continua `2 × fee_bp + spread` → **12–16 bp**.
- **Payload cru (opt-in):** registo, ligado por env, das respostas cruas do Jev que explicam de onde sai `confidence` (`side_answer.confidence` vs `probabilities[choice]`), sem segredos.
- **Ladder `score → bp`:** `(0, 5, 10, 15, 20, 25, 30, 35, 50, 80)` — **não muda** neste card.
- **DEV / runtime-worker:** entrega e evidência no unit DEV (`RUN_SCALP_LOOP=1`); PROD é T16, no lote.

## Goals / Non-Goals

**Goals:**

- A régua multi-dia (Card A) existe primeiro e é ela que escolhe o limiar de confiança e a geometria de alvo/stop; amostra insuficiente é declarada, não concluída.
- O hurdle reflecte a fee **maker** real (12–16 bp) e cai no fallback conservador `(10 bp, False)` quando a API de fee falha.
- O `confidence` do Jev deixa de matar 100% das decisões: registo cru opt-in → limiar calibrado pelo Card A **ou** queda do gate (decisão fechada na grelha 23/09).
- No regime calmo **nenhuma** entrada (skip visível `regime`); no regime activo entradas permitidas — previsão ≥ custo maker + 50% de folga.
- Nenhuma posição fica presa: no fim da janela de espera sem preenchimento passivo, o escape agressivo (MARKET/IOC, sem teto de preço) fecha a posição, com registo visível.
- Consulta proporcional ao horizonte: `JEV_TARGET_MS` por env com default **30 s**, payload resumido com input/call ≤ ~500 tokens, e `latency_ms` sem o custo do registo de entrada.
- Os drivers do `book_toxic` ficam registados para distinguir opinião do modelo de mapeamento errado.

**Non-Goals:**

- Reabrir #1006 (lookback), #1008 (stream) ou #1001 (interruptor/T/clip/kill); a régua #1007 fica como está (Cancelado).
- Painel/Monitor: a recusa e o motivo continuam **só no log** (decisão do #1015) — expor no painel é card novo.
- Base de dados nova, dashboard, exportação/Drive, backtest.
- Produção: tudo nasce e é validado no DEV (PROD é T16, no lote).
- Mudar a ladder `score → bp` `(0, 5, 10, 15, 20, 25, 30, 35, 50, 80)` — só se o Card A mostrar que está capada.
- Retunar o limiar `noul ≥ 0,5` do `book_toxic` (G só regista drivers).
- Segredos em qualquer artefacto, registo ou evidência.

## Decisions

1. **A régua é a primeira entrega e é um gate, não um relatório decorativo.** `scripts/scalp_jev_eval.py` é read-only (não escreve produto nem base de dados), lê o log de diagnóstico (`SCALP_JEV_LOG_FILE`, default `backend/scalp_jev_diagnostic.log`) e junta o realizado a 900 s do OHLCV existente. Reporta previsão vs realizado com janelas **não sobrepostas** (a evidência do #1015 é de 17 min e sobrepõe horizontes de 900 s — não serve para expectancy), segmentação por regime, acerto das barreiras +35/−28 bp, expectancy líquida por bucket de `score`/`confidence` e a curva de calibração. Nenhuma mudança de limiar em C/D existe antes deste relatório; se a amostra não chegar, o relatório **declara insuficiência** e o limiar/geometria ficam como estão.
   Alternativa rejeitada — **calibrar já com a amostra de 17 min do #1015**: 766 respostas mas ~49 janelas completas de 900 s sobrepostas e num só regime; violaria o próprio Critério («amostra insuficiente tem de ser declarada, não concluída»).
   Alternativa rejeitada — **régua a escrever em base de dados / dashboard**: Não entra (base de dados nova, dashboard).
   Alternativa rejeitada — **régua em `backend/tests`**: seria um teste com I/O de ficheiro multi-dia, não um instrumento read-only operável pelo dono.

2. **Custo maker real em `_fee_terms`, com cache por utilizador e fallback conservador.** `_fee_terms` (`scalp_service`) passa a ler `GET /api/v3/account` (`commissionRates.maker`) e `GET /sapi/v1/bnbBurn` (`spotBNBBurn`) por `signed_request` (cliente que já serve `/sapi/v1/...` noutro módulo), com **cache por utilizador** e **fallback `(10 bp, False)`** em falha. A shape `(fee_bp, bnb_fee_active)` e a fórmula `entry_hurdle_bp = 2 × fee_bp + spread` **não mudam** — o que muda é o `fee_bp` ser a taxa maker real por perna (a soma das duas pernas maker medida no #1015 é 12–16 bp), pelo que o hurdle cai de ~20 bp para 12–16 bp e o `/api/scalp/status` mostra a taxa em uso.
   Alternativa rejeitada — **hard-coded 7,5/6/8 bp**: a taxa é por conta e muda (VIP, BNB); o Entra pede explicitamente a API.
   Alternativa rejeitada — **sem cache, a cada ciclo**: uma chamada assinada extra por ciclo (~0,4 s) e um segundo modo de falha dentro do caminho de decisão.
   Alternativa rejeitada — **fallback «maker presumido»**: o Entra fixa o fallback conservador `(10 bp, False)` (hurdle ~20 bp) — falhar para mais caro é o lado seguro.
   Alternativa rejeitada — **mover o cálculo do hurdle para dentro do ciclo com `spread_bp` da memória apenas**: a fórmula e a fonte do `spread_bp` ficam como estão; este card só muda a fee.

3. **Confiança: medir antes de mexer no número — e removê-la é uma saída válida.** Registo **opt-in por env** (no log do #1015, sem segredos) com o payload cru das respostas: `side_answer.confidence`, `probabilities[choice]`, o `score` cru e o `noul`. `CONFIDENCE_MIN` passa a ser **configurável por env**; o valor sai do Card A (bucket com expectancy líquida positiva, nunca acima do alcance observado). **Se o Card A mostrar que a confiança não separa trades bons de maus, o gate cai** (decisão fechada na grelha 23/09): a decisão passa a ser previsão × custo × regime e o `low_confidence` desaparece do caminho — não fica um limiar decorativo a 0,05.
   Alternativa rejeitada — **baixar 0,7 para 0,2/0,05 «porque o máximo é 0,39»**: o valor tem de vir da expectancy por bucket, não do alcance observado (o alcance só dá o tecto do que é representável).
   Alternativa rejeitada — **manter o gate como desempate**: não implementa a decisão fechada (o gate cai quando não separa).
   Alternativa rejeitada — **registar o payload cru sempre**: flood + custo; o Entra diz opt-in por env.
   Alternativa rejeitada — **trocar de modelo/prompt do Jev neste card**: fora do Entra; o diagnóstico serve para localizar escala/parsing.

4. **Gate de regime explícito com maker + 50% de folga, com token próprio e ordem fixada.** `decide_cycle` ganha o token `skip_reason="regime"`: entrada só quando a previsão (`expected_move_bp`) cobre o custo maker com folga de 50% — `expected_move_bp >= entry_hurdle_bp × 1,5`. A ordem dos gates mantém-se e o `regime` entra **depois** do `hurdle` (que continua a ser o teste sem folga) e **antes** do `toxic_book`, para que os tokens contem a história certa: `hurdle` = «não cobre o custo»; `regime` = «cobre o custo, mas sem a folga de 50%». Não há switch por env que desligue o gate — o Critério «no regime calmo nenhuma entrada (skip visível `regime`)» tem de ser sempre observável.
   Alternativa rejeitada — **ter o σ da janela (`vol_bp`) como primary input do gate**: o σ é estatística da janela, não a previsão que a decisão usa; a grelha fixa «custo maker + 50% de folga» sobre a previsão. O σ pode entrar como condição secundária/fallback (P3) depois de a régua segmentar por regime.
   Alternativa rejeitada — **`regime` absorver o `hurdle` (um único token)**: perderia a distinção entre «não paga o custo» e «paga sem folga», que é exactamente o que o operador vai ler no log.
   Alternativa rejeitada — **classificador de regime novo (tabela/modelo)**: Não entra (base de dados nova, dashboard) e o gate é observável com a previsão que já existe.
   Alternativa rejeitada — **gate ligado por env**: tornaria o critério observável opcional.

5. **Geometria de alvo/stop vem da régua; a janela de espera é decisão de produto e não entra na recalibração.** `EXIT_TARGET_BP` e `EXIT_STOP_BP` são recalibrados para R:R coerente com a previsão e com o custo maker (break-even actual das barreiras 63,5–69,8%; alvo 35 bp contra previsão p50 8,6–12,9 bp), com os valores tirados do relatório do Card A e a evidência de expectancy líquida positiva. A **janela de espera de 15 min** (`HOLD_AFTER_FILL_S = 900 s`, que é o gatilho do escape) **fica fora** da recalibração: é valor de produto fixado na grelha de 23/09, para que uma janela devolvida pelo relatório não mude o «15 min» em silêncio; alterar este número é **alterar explicitamente aquela decisão**, nunca consequência implícita do relatório. Se o Card A não fechar a geometria, os valores actuais ficam e o motivo é registado — nunca se inventa um número «para parecer calibrado».
   Alternativa rejeitada — **fixar 12 bp / −12 bp no Design**: seria um número sem régua, exactamente o que A proíbe («nenhuma mudança de limiar sem este relatório»).
   Alternativa rejeitada — **deixar o Card A recalibrar também a janela de 15 min**: mudaria em silêncio uma constante fixada na grelha, e com ela o gatilho do escape (achado F3); a janela só muda por decisão explícita do dono.
   Alternativa rejeitada — **recalibrar alvo/stop por fórmula só com a evidência do #1015**: 17 min e um regime; insuficiente.

6. **O escape agressivo substitui o `stuck` inerte: no fim da janela de espera, sem tentativa passiva extra e alcançável com a saída passiva resting.** Nova função em `scalp_binance.py` para saída agressiva `MARKET`/IOC (hoje só existe `place_post_only`); `decide_exit_cycle` deixa de devolver `skip_reason="stuck"` **sem ordem**. O gatilho é o **primeiro ciclo em que o fim da janela de espera é atingido** (`seconds_since_fill >= HOLD_AFTER_FILL_S` = 900 s após o fill) com a posição ainda aberta — isto é, sem preenchimento passivo — e **não** a marca `stuck` dos 930 s (`STUCK_AFTER_FILL_S` deixa de ser o marcador do gatilho; `state.stuck` mantém o seu significado actual de «posição presa» no painel, intocado). **Reordenação dos gates do caminho de saída (contrato visível, não P3):** hoje o ramo `if resting is not None → skip_reason="exit_resting"` (l.445–452) devolve **antes** do `if stuck:` (l.453–460), pelo que o escape seria inalcançável no caso principal do card — a saída passiva postada aos 900 s e não preenchida fecha o ciclo em `exit_resting` e a posição fica sem escape. A condição de fim de janela/escape tem de ser avaliada **antes** do ramo `exit_resting` (e antes de `hold_position`/`would_cross`): ao disparar, **cancela** qualquer ordem de saída passiva do bot ainda não preenchida **e envia** a ordem agressiva, **sem teto de preço** (sai sempre, seja qual for o preço) e **sem tentativa passiva extra**. Consequência explícita: o post passivo temporal do fim da janela (`should_post_exit` pelo ramo `seconds_since_fill >= 900`) deixa de existir — seria a tentativa passiva extra proibida — pelo que os «4 de 49» fechos por tempo do #1015 passam a ser fechos pelo caminho agressivo; a saída passiva que resta é a de alvo/stop **dentro** da janela. A saída agressiva deixa **registo visível** no log de diagnóstico (nível WARNING, com motivo próprio — não o token `stuck`), nunca no painel. Invariante: **nenhuma posição passa a janela de espera sem tentativa de saída** (passiva dentro/na janela ou agressiva no seu fim).
   Alternativa rejeitada — **avaliar o escape depois do ramo `exit_resting`** (manter a ordem actual e só trocar o `stuck` pela agressiva): deixaria o caso principal do card — maker de saída postado e não preenchido — sem escape, que é exactamente o defeito que o card corrige (achado F1).
   Alternativa rejeitada — **esperar pela marca `stuck` dos 930 s**: adiaria o gatilho para lá do fim da janela fixado na grelha (15 min após o fill) — achado F2.
   Alternativa rejeitada — **IOC a preço limitado / com slippage guard**: a grelha fixa «sem teto de preço: sai sempre»; um tecto reintroduz a posição presa.
   Alternativa rejeitada — **tentar passivo outra vez no fim da janela e adiar o agressivo**: é a «tentativa passiva extra» proibida; o escape não espera por mais uma tentativa passiva.
   Alternativa rejeitada — **ter o escape no painel/API**: sem-tela; painel/Monitor fora (decisão do #1015).
   Alternativa rejeitada — **`place_post_only` que cruza (GTX a mercado)**: a Binance rejeita — não é escape.
   Alternativa rejeitada — **`MARKET` para a entrada**: o Entra quer a entrada maker; o escape é só de saída.

7. **Cadência: `JEV_TARGET_MS` por env com default 30 s, sem abrandar o loop do ciclo.** O valor configurado é injectado a partir de `scalp_service` (que tem I/O/env) para `decide_cycle`, no gate `jev_target` e no `last_jev_elapsed_ms` do caminho pós-chamada; o `scalp_engine` continua **puro**. O `interval` do loop (`max(JEV_FLOOR_MS/1000, 0.4)` = 0,4 s) **não** sobe: ele só paceia o gate e, com a cadência a 30 s, as requests/h caem ~30× (critério ≥ 15×) sem atrasar nada do que vive no mesmo ciclo.
   Alternativa rejeitada — **pôr o `interval` do loop a 30 s**: o mesmo ciclo trata o `_sync_resting_order`, o alvo/stop da saída e a marca `stuck`; uma saída passaria a esperar até 30 s — inaceitável, e é pior do que o problema que resolve.
   Alternativa rejeitada — **mudar só a env do unit DEV com a constante de 1000 ms no código**: o gate continuaria a 1 s (a constante manda) e o default de 30 s pedido pelo Entra não existiria no código.
   Alternativa rejeitada — **cadência adaptativa por regime**: mecanismo a mais, fora do Entra, e tornaria o critério «≥ 15× menos requests/h» não determinístico.
   Alternativa rejeitada — **tocar no `JEV_LATE_MS` (1,5 s)**: é o fail-closed; fica como está.

8. **Payload resumido até ~500 tokens sem tocar na ladder.** A janela transportada é resumida a **agregados do horizonte de 900 s + últimos N trades** (nunca o dump dos ticks) e o bloco fixo de `questions`/`criteria` é compactado, preservando os **10 níveis** `(0, 5, 10, 15, 20, 25, 30, 35, 50, 80)` e o significado de cada nível; o alvo é **input/call ≤ ~500 tokens** (hoje 1.158; 467 em 21/09). O instrumento exacto de contagem e a redação compacta do `criteria` são P3, mas o critério «≤ ~500 tokens» e a ladder inalterada são contrato.
   Alternativa rejeitada — **cortar a ladder para 5 níveis**: Não entra (a ladder só muda se o Card A mostrar que está capada).
   Alternativa rejeitada — **reduzir a cadência como única alavanca de custo**: resolve $/mês mas não o input por chamada, que é critério do card.
   Alternativa rejeitada — **pedir o resumo ao modelo (mais uma chamada)**: custo e latência a dobrar.

9. **`latency_ms` medido depois do registo de entrada.** Em `request_jev` o cronómetro passa a abrir **depois** de `log_call_entry` (hoje abre antes, l.263 vs l.283): a latência volta a medir a chamada e deixa de inflacionar o gate fail-closed `jev_late`. O registo de entrada continua a sair (é o #1015) — só sai da janela cronometrada.
   Alternativa rejeitada — **subtrair uma estimativa do registo**: não é mensurável e depende do disco.
   Alternativa rejeitada — **subir o `JEV_LATE_MS` para esconder a inflação**: mudaria o fail-closed (Não entra).
   Alternativa rejeitada — **desligar o registo de entrada**: destruiria a fonte de dados do Card A.

10. **Drivers do `book_toxic` no log, limiar intocado.** O registo de retorno do #1015 passa a incluir os drivers do flag: o `noul` devolvido pelo modelo, as features da janela usadas na decisão (`ret_bp`, `vol_bp`, `aggressor_flow`, `spread_bp_mean`, `trade_count`) e o booleano resultante — para distinguir **opinião do modelo** de **mapeamento errado**. Hoje 59% tóxico e correlacionado com fluxo agressor (p50 −0,4 BTC tóxico vs +4,9 BTC não tóxico). O limiar `noul ≥ 0,5` **não** se retuna neste card (é calibração, e só depois de os drivers mostrarem qual dos dois casos é).
   Alternativa rejeitada — **expor os drivers no `/monitor`**: sem-tela; painel fora.
   Alternativa rejeitada — **retunar já o limiar 0,5**: sem os drivers não se sabe se é opinião ou bug de mapeamento (é o ponto do G).

11. **Fronteira de ambiente e de superfície: DEV, log-only, sem tela.** Tudo nasce e é validado no **DEV** (`ops/systemd/criptofarol-dev-runtime-worker.service`, `RUN_SCALP_LOOP=1`, o mesmo flag que arma o log do #1015); PROD é T16, no lote. O motivo de recusa (incluindo `regime` e o escape agressivo) vive **só no log**; o `/api/scalp/status` continua a mostrar o hurdle em bp (agora com a fee real) e **não** ganha campos de diagnóstico; nada de HTML, rota, protótipo ou base de dados.
   Alternativa rejeitada — **levar já para PROD «porque é só backend»**: o Critério manda provar a evidência no DEV primeiro.
   Alternativa rejeitada — **avisar o operador no painel na saída agressiva**: é exactamente o que o #1015 fechou (card novo para isso); o registo visível é o log.

## Risks / Trade-offs

- [Risco] A régua (Card A) não produz amostra suficiente (log DEV multi-dia curto, janelas de 900 s sobrepostas) e as calibrações ficam sem base → Mitigação: decisão 1 (declarar insuficiência é resultado válido); default da confiança mantém-se 0,7 e a geometria fica como está, com o motivo registado na evidência — não se inventa número.
- [Risco] O gate de confiança cai e a entrada passa a depender só de previsão × custo × regime, com mais entradas do que o esperado → Mitigação: é decisão fechada na grelha e só acontece com o relatório da régua na mão (a confiança não separa); o gate de regime (maker + 50% de folga) passa a ser o travão da entrada, e o escape agressivo garante que nenhuma posição fica presa.
- [Risco] O `CONFIDENCE_MIN` calibrado fica acima do alcance observado (máx 0,39) e volta a matar 100% → Mitigação: decisão 3 (nunca acima do alcance observado) + teste do limiar.
- [Risco] A fee maker real é lida com `bnb_fee_active` a `false`/expirado e o hurdle fica em 20 bp outra vez → Mitigação: decisão 2 (duas fontes: `commissionRates.maker` + `spotBNBBurn`), teste com BNB ligado/desligado e o fallback sempre conservador.
- [Risco] Cache por utilizador com taxa velha (mudança de VIP) → Mitigação: TTL do cache é P3, explícito; o fallback conservador cobre a falha, e a taxa em uso fica visível no status.
- [Risco] O escape agressivo dispara num spread momentaneamente largo e a saída sai a um preço mau → Mitigação: é a decisão explícita do dono («sem teto de preço: sai sempre»); o registo do preço de saída fica no log; a alternativa (tecto) é o que prende a posição.
- [Risco] O escape cancelar uma saída passiva que estava a preencher → Mitigação: decisão 6 — o cancelamento só acontece no ciclo em que o fim da janela de espera é atingido com a posição ainda aberta, e o invariante exige o envio da agressiva no mesmo ciclo; teste com ordem parcialmente preenchida.
- [Risco] Pôr a cadência a 30 s atrasa a reacção a uma mudança de livro → Mitigação: decisão 7 — só o gate da **chamada ao Jev** passa a 30 s; o loop, o alvo/stop, o `_sync_resting_order` e a marca `stuck` continuam a 0,4 s; o efeito na reacção vs horizonte de 900 s é documentado.
- [Risco] Vazar valores exactos de conta no log cru novo (C) → Mitigação: o registo do #1015 já resume a conta (`has_position`/`has_balance`) e redige segredos; o registo cru é do **retorno** do modelo (confiança/score/noul), não do `account`; teste sem segredos.
- [Risco] Os drivers do `book_toxic` (G) virarem um segundo log pesado → Mitigação: mesmo ficheiro e mesmo tecto do #1015 (200 MB, truncagem de cauda), registo só no retorno da chamada.
- [Trade-off] Sete superfícies de contrato (A–G) num só card — aceite: foi assim que o dono fixou o Entra, e as calibrações C/D dependem de A; o Apply fatia por A–G.
- [Trade-off] Os números de alvo/stop e do `CONFIDENCE_MIN` **não** ficam fixados neste Design — aceite: fixá-los sem a régua seria o erro que o card existe para corrigir; a regra e a evidência ficam fixadas, a janela de espera fica fixada por decisão de produto (900 s), e o Apply bloqueia nos tasks do Card A.

## Apply contract

**Contrato visível (não P3):**

- `scripts/scalp_jev_eval.py` read-only sobre o log do #1015 + realizado a 900 s: janelas não sobrepostas, segmentação por regime, acerto +35/−28 bp, expectancy líquida por bucket de `score`/`confidence`, curva de calibração; amostra insuficiente declarada; **nenhuma** mudança de limiar (C/D) antes do relatório.
- `_fee_terms` com a taxa maker real (`GET /api/v3/account` + `GET /sapi/v1/bnbBurn`), cache por utilizador e fallback `(10 bp, False)`; hurdle `2 × fee_bp + spread` a reflectir 12–16 bp com maker, ~20 bp no fallback; taxa em uso visível no status.
- Registo opt-in (env) do payload cru do Jev sem segredos (`side_answer.confidence`, `probabilities[choice]`, `score` cru, `noul`).
- `CONFIDENCE_MIN` por env, valor do Card A (nunca acima do alcance observado); **queda do gate** quando a confiança não separa — decisão passa a previsão × custo × regime.
- Token `skip_reason="regime"` em `decide_cycle`, com `expected_move_bp >= entry_hurdle_bp × 1,5` (maker + 50% de folga), depois do `hurdle` e antes do `toxic_book`; sem switch por env; calmo → nenhuma entrada, activo → permitido.
- `EXIT_TARGET_BP`/`EXIT_STOP_BP` recalibrados **a partir do Card A**; a janela de espera (`HOLD_AFTER_FILL_S` = 900 s) é constante de produto da grelha de 23/09 e **não** entra na recalibração (só muda por alteração explícita dessa decisão); sem relatório, os valores actuais ficam.
- Saída agressiva `MARKET`/IOC **sem teto de preço** em `scalp_binance.py`; **gatilho = primeiro ciclo em que o fim da janela de espera (~900 s após o fill) é atingido com a posição aberta** (não a marca `stuck` dos 930 s); **gates do caminho de saída reordenados** para a condição de fim de janela/escape ser avaliada **antes** do ramo `exit_resting` (alcançável com a saída passiva resting não preenchida); cancelamento da passiva não preenchida + envio da agressiva no mesmo ciclo; sem tentativa passiva extra; **invariante**: nenhuma posição passa a janela sem tentativa de saída; registo visível (log, WARNING, motivo próprio) e nada no painel.
- `JEV_TARGET_MS` por env com default **30 s** (motor puro, valor injectado do serviço); requests/h ≥ 15× menores; payload com agregados do horizonte 900 s + últimos N trades e **input/call ≤ ~500 tokens**; ladder `(0, 5, 10, 15, 20, 25, 30, 35, 50, 80)` inalterada; `latency_ms` medido depois do registo de entrada.
- Drivers do `book_toxic` (`noul` + features da janela) registados com o flag resultante; limiar `noul ≥ 0,5` intocado.
- DEV-only (`RUN_SCALP_LOOP=1`); sem `frontend/**`, sem rota/HTML, sem base de dados nova, sem dashboard/exportação/Drive, sem backtest, sem PROD, sem segredos.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Onde vive o teste de folga de 50%: `entry_hurdle_bp`/`passes_entry_hurdle` em `scalp_window.py` (nova função, p.ex. `entry_hurdle_bp_with_slack`) ou dentro de `decide_cycle` — a fórmula (`entry_hurdle_bp × 1,5`) e o token `regime` estão fixados.
- Nomes das envs novas (cadência, limiar de confiança, registo cru do payload) e o TTL da cache de fee.
- Formato do registo do escape agressivo (função e campos: lado, quantidade, `MARKET`/IOC, motivo — **token próprio, não `stuck`**) e o nível (WARNING) no log do #1015.
- Instrumento de medição dos ~500 tokens (contagem de tokenizer vs heurística bytes/4) e a redação compacta do `criteria` do `expected_move_bp` — os 10 níveis e o seu significado ficam.
- Valor de `N` (últimos trades) na janela resumida e a forma exacta do resumo (quais agregados).
- Predicado/unidade de `fee_bp` (por perna) e como `bnb_fee_active` entra no número mostrado no status.
- Como os testes injectam fee/chamada assinada, forçam o fallback, armam o registo cru e simulam a saída passiva não preenchida.
- Se o σ (`vol_bp`) entra no gate de regime como condição secundária/fallback (decisão 4) — resolve-se com a segmentação por regime do Card A.

## Open Questions / pontos deixados ao crítico

Nenhuma pergunta ao operador — a fronteira veio grelhada e as decisões 1–11 fecham o *como*. O rework 1/1 fechou os três achados de contrato visível do crítico (F1/F2/F3) e o F4; o que continua aberto está no fim desta secção.

**Resolvido no rework 1/1 (achados F1/F2/F3 do crítico — contrato visível):**

(i) **Escape alcançável (F1):** os gates do caminho de saída são **reordenados** e a condição de fim de janela/escape é avaliada **antes** do ramo `exit_resting`, que hoje corta antes do `stuck`; com a saída passiva resting não preenchida, o escape passa a ser alcançado (cancela a passiva e envia a agressiva no mesmo ciclo). Fixado na decisão 6, no Apply contract, na spec `scalp-aggressive-exit` e nas tasks 5.2/5.4.
(ii) **Instante do gatilho (F2):** o gatilho é o **primeiro ciclo em que o fim da janela de espera é atingido** (~900 s após o fill), **não** a marca `stuck` dos 930 s; `STUCK_AFTER_FILL_S` deixa de ser o marcador do gatilho (o `state.stuck` mantém o significado de «posição presa» no painel/status). Fixado na decisão 6, no Apply contract, na spec e nas tasks.
(iii) **`HOLD_AFTER_FILL_S` × recalibração (F3):** desempatado — a recalibração do Card A aplica-se a `EXIT_TARGET_BP`/`EXIT_STOP_BP`; a janela de 15 min (`HOLD_AFTER_FILL_S = 900 s`) é constante de produto da grelha de 23/09, fica **fora** da recalibração e só muda por alteração explícita dessa decisão. Fixado na decisão 5, no Apply contract, na spec `scalp-regime-gate` e na task 4.2.

**Pontos que continuam abertos para a crítica:**

1. **Valor de `CONFIDENCE_MIN` e números de `EXIT_TARGET_BP`/`EXIT_STOP_BP`** — deliberadamente não fixados aqui: dependem do relatório do Card A (decisões 3 e 5). O Apply bloqueia nos tasks do Card A; se o relatório declarar amostra insuficiente, os valores actuais ficam e a evidência registra o motivo.
2. **σ (`vol_bp`) como condição secundária do gate de regime** — o Entra admite «previsão (ou σ do horizonte)»; o input primário é a **previsão** e o σ só entra se a régua (Card A) o justificar (decisão 4 e o requisito da spec `scalp-regime-gate`), nunca por leitura literal da cláusula.

## Design Critique

Publicada pelo pai após a onda de crítica (excepção prevista no runbook). Sem-tela: o crítico é **um**; sem onda A/B, sem protótipo, sem clone de página viva e sem Snapshot Impeccable.

**Onda (teto 1+1+1, sem-tela):** 1 autor → 1 crítico → **1 rework**. Sem segundo rework (não houve P0 novo de produto) — a coluna segue para `Aprovação de Design`.

**Crítico, ronda única:** `rework: sim`, `p0_p1_count: 3`. Achados e fecho (gravidade e classe copiadas do dump, sem reclassificação):

| id | gravidade | classe | achado | fecho |
| --- | --- | --- | --- | --- |
| F1 | **P0** | contrato-visivel | O escape agressivo era inalcançável no caso principal do card: o ramo `if resting is not None → skip_reason="exit_resting"` (`scalp_engine.py:445–452`) devolve **antes** do ramo do `stuck` (l.453–460), logo a saída passiva postada e não preenchida fechava o ciclo sem escape. | Reordenação dos gates do caminho de saída fixada como contrato visível (decisão 6, Apply contract, spec `scalp-aggressive-exit`, tasks 5.2/5.4/8.3): a condição de fim de janela é avaliada antes do `exit_resting`; ao disparar, cancela a passiva não preenchida e envia a agressiva no mesmo ciclo. |
| F2 | P1 | contrato-visivel | O gatilho do escape estava deslocado para o ponto onde hoje se devolve `stuck` (930 s), contra a decisão da grelha (fim da janela de espera, 15 min após o fill). | Gatilho passou a ser o **primeiro ciclo em que o fim da janela (~900 s) é atingido** com a posição aberta; `STUCK_AFTER_FILL_S` deixa de ser o marcador (o `state.stuck` mantém o significado de «posição presa» no painel). Consequência escrita: os 4/49 fechos por tempo do #1015 passam a fechos agressivos. |
| F3 | P1 | contrato-visivel | `HOLD_AFTER_FILL_S` era simultaneamente o gatilho do escape e um valor aberto à recalibração do Card A — o «15 min» podia mudar em silêncio. | Desempatado: a recalibração cobre só `EXIT_TARGET_BP`/`EXIT_STOP_BP`; a janela de 15 min é valor de produto da grelha de 23/09, **fora** da recalibração e só muda por alteração explícita dessa decisão (decisão 5, spec `scalp-regime-gate`, task 4.2). |

**P3 aceitos** (detalhe de Apply; registados como aceites e resolvidos no Apply, nunca reabertos como P0/P1):

- F4 — σ (`vol_bp`) como condição secundária do gate de regime: a spec fixa a **previsão** como input primário e o σ só entra se a régua o justificar (cenário próprio).
- Citações de linha envelhecidas em `design.md`: passou a citar o bloco `scalp_engine.py:11–26`; `_fee_terms` mantém `scalp_service.py:249–251`.
- `surface: new` lido como **nova capability de backend** (contrato de decisão novo), não como superfície de tela — nota de leitura no Context.

**Sem achados de produto/escopo:** nada do «Não entra» entrou (sem `frontend/**`, rota, HTML, painel, DB/dashboard/Drive/backtest, PROD; ladder `score→bp` intacta); briefing verbatim em `proposal.md`; 12 requisitos / 46 cenários dão cobertura aos critérios observáveis do issue.

**Rubrica do crítico:** itens 1 (tokens do gate), 2 (briefing verbatim), 4 (escopo), 6 (cobertura) e 7 (tasks) `ok` na ronda única; itens 3 e 5 falharam exactamente por F1/F2/F3 e ficaram fechados no rework 1/1.

**Proxies do handoff:** `design.md` 1.ª ronda → final (contagem em baixo); HTML generated vs copied = **N/A vs N/A** (sem protótipo); spawns = **3** (autor, crítico, rework 1/1). Cliente dsh: sem selecção de modelo por spawn (o mapa de modelo é contrato do cliente Cursor) e sem reivindicação de modo Auto.
