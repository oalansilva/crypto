Título: Scalp Jev: destravar entradas (confiança, custo maker, regime, saída taker e cadência)
Relacionado com #1015 (log de diagnóstico do Jev — a evidência de 23/09 é deste card). #1001/#1006/#1008 não se reabrem; a régua #1007 fica como está (Cancelado) — o Card A substitui-a com dados do log do #1015.

Card criado a partir do diagnóstico do #1015 (log de diagnóstico do Jev). Agrupa **todas** as alterações necessárias para o scalp Jev poder voltar a entrar — e nunca ficar preso.

## Problema

Quem liga o Scalp BTCUSDT continua sem compras e o log do #1015 mostra porquê, com números (23/09, 13:26→13:44, **766 respostas**, **zero entradas**):

- **0 de 766** respostas passam o gate de confiança (`CONFIDENCE_MIN = 0.7`): o campo `confidence` do Jev vive em **[0; 0,39]** (p50 0,06) e **não acompanha o regime** — enquanto o `expected_move_bp` triplicou (p50 8,6 → 29,7 bp), a confiança ficou plana em 0,05–0,08. O gate é decorativo e mata 100% das decisões.
- **Havia candidatos reais**: 394 respostas com direção; **212** com `expected_move_bp` > 20 bp; **96** com previsão ≥ 20 bp e livro não tóxico; **114** com previsão ≥ 12 bp e não tóxico.
- **Custo mal modelado**: as duas pernas são `place_post_only` (maker), mas `_fee_terms` devolve sempre `(10 bp, sem BNB)` — stub taker — e o hurdle fica em ~20 bp quando o custo real é **12–16 bp** (inflação de 25–67%).
- **Sem filtro de regime**: no período calmo a previsão mediana foi 8,6 bp (abaixo do custo); no ativo, 24,5–29,7 bp. Operar sem olhar ao regime é perder no calmo.
- **Posição pode ficar presa**: aos 930 s o `decide_exit_cycle` devolve `skip_reason="stuck"` **sem postar saída** e **não existe nenhuma ordem a mercado/IOC** no cliente → uma posição cujo maker de saída não preenche fica inerte, sem escape taker (4 de 49 janelas fecharam por tempo).
- **Consulta sobre-amostrada e payload gordo**: o modelo responde a um horizonte de **900 s** mas é chamado a cada **1 s** (900× de sobre-amostragem) — $74,5/mês a 1 Hz vs $2,48/mês a 30 s; o input por chamada cresceu 467 → **1.158 tokens** (dump da janela); e a escrita do registo de entrada entra na latência medida que alimenta o gate fail-closed `jev_late` (P1 residual do review do #1015).

## História

Como operador do scalp Jev, quero que as entradas deixem de ser bloqueadas por um limiar fora do alcance do modelo, que a decisão use o custo **real** (maker), que o bot só opere quando a previsão cobre o custo no regime corrente, que nenhuma posição possa ficar presa sem saída, e que a consulta ao Jev seja proporcional ao horizonte do modelo — para o scalp entrar por decisão e não continuar a pagar chamadas para não decidir nada.

## Entra

**A. Régua de avaliação do Jev (primeiro — gate das calibrações)**
- `scripts/scalp_jev_eval.py` (read-only) sobre `backend/scalp_jev_diagnostic.log` multi-dia: previsão vs realizado aos **900 s** com janelas **não sobrepostas** e segmentação por regime; acerto das barreiras +35/−28; expectancy líquida por bucket de `score`/`confidence`; curva de calibração (`confidence` → |realizado|).
- Nenhuma mudança de limiar sem este relatório; amostra insuficiente tem de ser declarada, não concluída.

**B. Custo maker real e hurdle**
- `_fee_terms` real via `signed_request`: `GET /api/v3/account` (`commissionRates.maker`) + `GET /sapi/v1/bnbBurn` (`spotBNBBurn`), cache por utilizador, **fallback `(10 bp, False)`** em falha.
- `entry_hurdle_bp = 2 × fee_maker + spread` → de ~20 bp para **12–16 bp**.

**C. Diagnóstico e recalibração do gate de confiança**
- Registar o **payload cru** das respostas do Jev (opt-in por env, sem segredos) para saber o que é `confidence` (`side_answer.confidence` vs `probabilities[choice]`) e se há erro de escala/parsing — antes de mexer no número.
- `CONFIDENCE_MIN` configurável por env, valor escolhido pelo **Card A** (bucket com expectancy líquida positiva), nunca acima do alcance observado.
- **Decidido (grelha 23/09):** se o Card A mostrar que a confiança **não separa** trades bons de maus, o gate **cai** — a decisão passa a ser previsão × custo × regime, sem limiar de confiança.

**D. Filtro de regime e geometria alvo/stop**
- Gate de regime explícito (`skip_reason="regime"`): não operar quando a previsão (ou σ do horizonte) não cobre o custo **com 50% de folga sobre o custo maker** (hurdle × 1,5) — no regime calmo nenhuma entrada, no activo entradas permitidas.
- Recalibrar `EXIT_TARGET_BP` / `EXIT_STOP_BP` / `HOLD_AFTER_FILL_S` para R:R coerente com a previsão e com o custo maker (break-even actual das barreiras: **63,5–69,8%**; alvo 35 bp vs previsão p50 8,6–12,9 bp).

**E. Saída com escape taker**
- Nova função de saída agressiva (`MARKET`/IOC) em `scalp_binance.py` (hoje não existe).
- **Decidido (grelha 23/09):** o gatilho é o **fim da janela de espera (15 min após o fill)** sem preenchimento passivo — sem tentativa passiva extra — e a saída agressiva é **sem teto de preço** (sai sempre, seja qual for o preço). Registo/alerta visível na saída agressiva.
- Invariante: nenhuma posição passa a janela de espera sem tentativa de saída (passiva ou agressiva).

**F. Cadência, payload e latência do registo**
- `JEV_TARGET_MS` por env, default **30 s** (hoje 1 s; **decidido na grelha 23/09**, ~$2,5/mês vs $74,5/mês a 1 Hz), documentando o efeito na reação vs horizonte de 900 s.
- Janela do payload resumida (agregados do horizonte 900 s + últimos N trades), input/call ≤ ~500 tokens.
- Medir `latency_ms` a partir de **depois** do registo de entrada (fecha o P1 residual do review do #1015).

**G. Observabilidade do `book_toxic`**
- Registar os drivers do flag (`noul` + features da janela) para distinguir opinião do modelo de mapeamento errado — hoje 59% tóxico e correlaciona com fluxo agressor (p50 −0,4 BTC tóxico vs +4,9 BTC não tóxico).

## Não entra

- Reabrir #1006 (lookback), #1008 (stream) ou #1001 (interruptor/T/clip/kill); a régua #1007 fica como está (Cancelado) — o Card A substitui-a com dados do log do #1015.
- Painel/Monitor: a recusa e o motivo continuam **só no log** (decisão do #1015); expor no painel é card novo.
- Base de dados nova, dashboard, exportação/Drive, backtest.
- Produção: tudo nasce e é validado no **DEV** (PROD é T16, no lote).
- Mudar a ladder `score → bp` `(0, 5, 10, 15, 20, 25, 30, 35, 50, 80)` — só se o Card A mostrar que está capada.

## Critérios observáveis

- Com o limiar de confiança calibrado, o replay multi-dia mostra **≥ 1 trade com expectancy líquida positiva** e nenhum bucket negativo a passar o gate.
- O hurdle reflecte a fee **maker** (12–16 bp) e cai no fallback conservador quando a API de fee falha.
- No regime calmo, **nenhuma** entrada (skip visível `regime`); no regime ativo, entradas permitidas.
- Uma posição cuja saída passiva não preenche é fechada pelo caminho agressivo; nenhuma fica aberta sem tentativa de saída.
- Requests/h reduzidas **≥ 15×** vs 1 Hz; `latency_ms` sem o custo do registo de entrada; `black` + pytest focado verdes; `qa-gate` verde.
- Evidência DEV anexada em cada etapa (log real no runtime-worker DEV).

## Evidência (log do #1015, 23/09 — 766 respostas / 17 min)

| Medição | Valor |
|---|---|
| `confidence` do Jev | máx **0,39** · p50 0,06 · ≥ 0,2: 2/766 |
| gate actual | `CONFIDENCE_MIN = 0.7` → **0/766** passam |
| `expected_move_bp` | p50 8,6 (calmo) → 29,7 (ativo) |
| direcionais | 394 · `em` > 20 bp: 212 · `em` ≥ 20 e não tóxico: 96 · `em` ≥ 12 e não tóxico: 114 |
| custo | maker 12–16 bp (2 pernas `place_post_only`) vs stub taker 20 bp |
| barreiras (49 janelas completas de 900 s) | 32 alvo · 13 stop · 4 tempo |
| cadência/custo | 1 Hz = $74,5/mês · 30 s = $2,48/mês |
| input/chamada | 467 tokens (21/09) → 1.158 tokens (22-23/09) |

Este card é **SEM-TELA** (backend/harness: régua, custo, gates e saída do scalp Jev). Sem HTML, sem protótipo, sem painel/Monitor (a recusa e o motivo continuam só no log — decisão do #1015).

## Como (resumo técnico da solução)

**A — Régua primeiro, e é ela que manda nos números.** `scripts/scalp_jev_eval.py` (read-only, sem escrever em produto nem em base de dados) lê o log de diagnóstico do #1015 (`backend/scalp_jev_diagnostic.log`, via `SCALP_JEV_LOG_FILE`) e junta-o aos preços realizados a 900 s (OHLCV já existente no repositório). Reporta previsão vs realizado com janelas **não sobrepostas**, segmentação por regime, acerto das barreiras +35/−28 bp, expectancy líquida por bucket de `score`/`confidence` e a curva de calibração (`confidence` → |realizado|). **Amostra insuficiente é declarada, nunca concluída**; nenhuma mudança de limiar em C/D acontece antes deste relatório existir.

**B — Custo maker real no hurdle.** `_fee_terms` (`backend/app/services/scalp_service.py`) deixa de ser stub e passa a ler a taxa **maker** real por `signed_request` (`GET /api/v3/account` → `commissionRates.maker`; `GET /sapi/v1/bnbBurn` → `spotBNBBurn`, o mesmo cliente que já serve `/sapi/v1/...` em `binance_spot.py`), com **cache por utilizador** e **fallback conservador `(10 bp, False)`** em falha. A shape do retorno `(fee_bp, bnb_fee_active)` mantém-se e a fórmula do hurdle não muda (`entry_hurdle_bp = 2 × fee_bp + spread`, em `scalp_window.py`), pelo que o hurdle cai de ~20 bp para **12–16 bp** e o `/api/scalp/status` mostra a taxa em uso.

**C — Confiança: medir antes de mexer no número.** Registo **opt-in por env** do payload cru das respostas do Jev (sem segredos) — `side_answer.confidence` vs `probabilities[choice]`, o `score` cru e o `noul` — para saber o que é `confidence` e se há erro de escala/parsing. `CONFIDENCE_MIN` passa a ser **configurável por env**, com o valor escolhido pelo Card A (bucket com expectancy líquida positiva, nunca acima do alcance observado). **Decidido (grelha 23/09):** se o Card A mostrar que a confiança **não separa** trades bons de maus, o gate **cai** e a decisão passa a ser previsão × custo × regime.

**D — Regime explícito e geometria coerente.** Novo gate de regime em `decide_cycle` com o token `skip_reason="regime"`: não entra quando a previsão não cobre o custo **com 50% de folga sobre o custo maker** (`entry_hurdle_bp × 1,5`), avaliado com a fee maker real — no regime calmo nenhuma entrada, no activo entradas permitidas. `EXIT_TARGET_BP` / `EXIT_STOP_BP` / `HOLD_AFTER_FILL_S` são recalibrados a partir do relatório do Card A para R:R coerente com a previsão e com o custo maker (break-even actual das barreiras 63,5–69,8%; alvo 35 bp contra previsão p50 8,6–12,9 bp); **os números não se inventam no Design** — saem do relatório.

**E — Escape taker, sem preço de conforto.** Nova função de saída agressiva (MARKET/IOC) em `backend/app/services/scalp_binance.py`, que hoje só tem `place_post_only`. **Decidido (grelha 23/09):** o gatilho é o **fim da janela de espera (15 min após o fill)** sem preenchimento passivo — **sem tentativa passiva extra** — e a saída é **sem teto de preço** (sai sempre, seja qual for o preço). O caminho deixa de ser inerte: hoje aos 930 s `decide_exit_cycle` devolve `skip_reason="stuck"` **sem ordem**; passa a cancelar a saída passiva não preenchida e a enviar a ordem agressiva, com **registo visível** no log de diagnóstico. Invariante: **nenhuma posição passa a janela de espera sem tentativa de saída** (passiva ou agressiva).

**F — Cadência, payload e latência.** `JEV_TARGET_MS` passa a ser lido de env com default **30 s** (hoje 1 s), injectado a partir de `scalp_service` para o motor puro (o `scalp_engine` não lê env) — requests/h caem ~30× e o `jev_late`/1,5 s fica como está. A janela transportada ao modelo é resumida (agregados do horizonte 900 s + últimos N trades) e o input por chamada fica **≤ ~500 tokens** (hoje 1.158), sem tocar na ladder `score → bp` `(0, 5, 10, 15, 20, 25, 30, 35, 50, 80)`. E o `latency_ms` passa a ser medido **depois** do registo de entrada — hoje o `log_call_entry` do #1015 corre dentro da janela cronometrada e inflaciona o gate fail-closed `jev_late` (P1 residual do review do #1015).

**G — Observabilidade do `book_toxic`.** Os drivers do flag (`noul` + features da janela usadas na decisão) são registados com o flag resultante, para distinguir opinião do modelo de mapeamento errado — hoje 59% tóxico, correlacionado com fluxo agressor (p50 −0,4 BTC tóxico vs +4,9 BTC não tóxico). Só log; o limiar `noul ≥ 0,5` não se retuna neste card.

**Fronteira e ambiente.** Este card é **SEM-TELA** (backend/harness): sem HTML, sem protótipo, sem painel — a recusa e o motivo continuam **só no log** (decisão do #1015). Tudo nasce e é validado no **DEV** (runtime-worker DEV, `RUN_SCALP_LOOP=1`); PROD é T16, no lote.

## Capabilities

### New Capabilities

- `scalp-jev-eval-ruler`: régua read-only multi-dia sobre o log do #1015 (previsão vs realizado a 900 s com janelas não sobrepostas, segmentação por regime, acerto das barreiras +35/−28 bp, expectancy líquida por bucket de `score`/`confidence`, curva de calibração), declaração explícita de amostra insuficiente e gate de todas as calibrações.
- `scalp-maker-fee-hurdle`: taxa maker real (`commissionRates.maker` + `spotBNBBurn`) por `signed_request` com cache por utilizador e fallback `(10 bp, False)`; hurdle `2 × fee_bp + spread` a reflectir 12–16 bp; taxa em uso visível no status.
- `scalp-confidence-gate`: registo opt-in (env) do payload cru do Jev sem segredos; `CONFIDENCE_MIN` configurável por env com o valor do Card A; queda do gate quando a confiança não separa trades bons de maus.
- `scalp-regime-gate`: gate de regime explícito (`skip_reason="regime"`) exigindo previsão ≥ custo maker + 50% de folga; recalibração de alvo/stop/hold a partir da régua.
- `scalp-aggressive-exit`: saída agressiva MARKET/IOC sem teto de preço, disparada no fim da janela de espera sem preenchimento passivo, com tentativa de saída garantida e registo visível.
- `scalp-jev-consult-cadence`: `JEV_TARGET_MS` por env com default 30 s; janela do payload resumida (agregados 900 s + últimos N trades) com input/call ≤ ~500 tokens e ladder inalterada; `latency_ms` medido sem o registo de entrada.
- `scalp-book-toxic-observability`: registo dos drivers do `book_toxic` (`noul` + features da janela) com o flag resultante, só no log.

### Modified Capabilities

- (nenhuma) — o painel/Monitor, o payload SystemOne (contrato do modelo para além do resumo de F), a ladder `score → bp`, o stream (#1008) e o interruptor/T/clip/kill (#1001) não mudam de requisito.

## Impact

- `scripts/scalp_jev_eval.py` (novo, read-only): régua do Card A sobre o log de diagnóstico + OHLCV realizado.
- `backend/app/services/scalp_service.py`: `_fee_terms` real (com cache e fallback) e injecção da cadência `JEV_TARGET_MS` configurada para o motor; status com a taxa em uso.
- `backend/app/services/scalp_window.py`: `entry_hurdle_bp`/`passes_entry_hurdle` mantêm a fórmula e ganham o teste de folga de 50% do regime (ou o gate vive em `scalp_engine`, com a mesma fórmula — P3).
- `backend/app/services/scalp_engine.py`: gate de regime `regime`, `CONFIDENCE_MIN` configurável (ou queda do gate), geometria alvo/stop/hold recalibrada, ramo de escape agressivo em `decide_exit_cycle`; módulo continua puro (sem I/O, sem env).
- `backend/app/services/scalp_binance.py`: nova função de saída agressiva (MARKET/IOC) a par do `place_post_only`.
- `backend/app/services/scalp_jev.py`: `latency_ms` medido depois do registo de entrada; payload do `questions`/`criteria` compactado sem tocar na ladder.
- `backend/app/services/scalp_jev_payload.py`: janela resumida (agregados + últimos N trades).
- `backend/app/services/scalp_jev_log.py`: registo opt-in do payload cru (C) e registo dos drivers do `book_toxic` (G) e da saída agressiva (E) no log do #1015.
- `backend/tests/`: testes de fee/fallback/cache, gate de regime, calibração da confiança, escape agressivo, cadência/payload/latência.
- Sem `frontend/**`, sem rota nova, sem HTML, sem base de dados nova, sem dashboard/exportação/Drive, sem backtest, sem PROD. Sem segredos em nenhum artefacto.
