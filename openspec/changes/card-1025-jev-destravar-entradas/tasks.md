# Tasks — card-1025-jev-destravar-entradas

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.
> Gate de Design antes de implementar: Design → Aprovação de Design → Pronto para Dev.
> Usar as skills do projecto (`.cursor/skills/`) quando aplicáveis no Apply.
> Ordem obrigatória: **A (régua) antes de C e D** — nenhuma mudança de limiar ou de geometria sem o relatório do Card A.

## 1. A — Régua de avaliação do Jev (`scripts/scalp_jev_eval.py`, read-only)

- [x] 1.1 — Criar `scripts/scalp_jev_eval.py` **read-only**: lê o log de diagnóstico do #1015 (`backend/scalp_jev_diagnostic.log` / `SCALP_JEV_LOG_FILE`) e junta o realizado a 900 s do OHLCV já existente (`ohlcv_storage`/`canonical_candle_service`); sem escrita em produto, estado do scalp ou base de dados nova.
- [x] 1.2 — Janelas **não sobrepostas** de 900 s e segmentação por regime (calmo vs activo) no relatório.
- [x] 1.3 — Reportar acerto das barreiras +35/−28 bp, expectancy líquida por bucket de `score` e de `confidence`, e a curva de calibração (`confidence` → |realizado|).
- [x] 1.4 — Declarar **amostra insuficiente** por bucket/regime em vez de concluir; guardar o relatório multi-dia como evidência DEV da etapa.
- [x] 1.5 — Gate: só depois de 1.4 existir é que 3.3 (limiar/queda do gate) e 4.2 (geometria) podem ser aplicados; sem relatório, os valores actuais ficam e o motivo entra na evidência.

## 2. B — Custo maker real e hurdle

- [x] 2.1 — `_fee_terms` (`backend/app/services/scalp_service.py`) real via `signed_request`: `GET /api/v3/account` (`commissionRates.maker`) + `GET /sapi/v1/bnbBurn` (`spotBNBBurn`), mantendo a shape `(fee_bp, bnb_fee_active)`; taxas por perna.
- [x] 2.2 — Cache por utilizador do resultado (sem chamada assinada por ciclo) com TTL definido; falha/timeout → fallback conservador `(Decimal("10"), False)`.
- [x] 2.3 — Hurdle continua `entry_hurdle_bp = 2 × fee_bp + spread` (`scalp_window.py`) e passa a reflectir **12–16 bp** com maker real; `/api/scalp/status` mostra a taxa em uso (hoje mostra «7,5 if bnb_fee_active else 10 bp»).
- [x] 2.4 — Testes: maker real aplicado; BNB ligado/desligado; falha da API → fallback `(10, False)` e hurdle ~20 bp; cache (número de chamadas assinadas não cresce com os ciclos).

## 3. C — Diagnóstico e recalibração do gate de confiança

- [x] 3.1 — Registo **opt-in por env** (no log do #1015) do payload cru das respostas: `side_answer.confidence`, `probabilities[choice]`, `score` cru e `noul`; sem segredos e sem valores exactos de conta; desligado, os registos do #1015 ficam como estão.
- [x] 3.2 — `CONFIDENCE_MIN` configurável por env (o motor puro recebe o valor; `scalp_engine` não lê env).
- [x] 3.3 — Aplicar o resultado do Card A: valor = menor bucket com expectancy líquida positiva, **nunca acima do alcance observado**; **se a confiança não separar trades bons de maus, remover o gate** — a decisão passa a previsão × custo × regime e `low_confidence` desaparece do caminho.
- [x] 3.4 — Testes: limiar calibrado; gate removido (sem `low_confidence`); relatório ausente/insuficiente → mantém o default e a evidência registra o motivo; nenhum bucket negativo passa o gate.

## 4. D — Gate de regime e geometria alvo/stop

- [x] 4.1 — Novo `skip_reason="regime"` em `decide_cycle`: entrada só com `expected_move_bp >= entry_hurdle_bp × 1,5` (custo maker + 50% de folga); avaliado **depois** do `hurdle` e **antes** do `toxic_book` (`hurdle` = abaixo do custo; `regime` = paga o custo sem a folga).
- [x] 4.2 — Recalibrar `EXIT_TARGET_BP` / `EXIT_STOP_BP` **a partir do relatório do Card A** (R:R coerente com a previsão e o custo maker; break-even actual 63,5–69,8%; alvo 35 bp vs previsão p50 8,6–12,9 bp); sem relatório, os valores actuais ficam. A **janela de espera de 15 min** (`HOLD_AFTER_FILL_S = 900 s`, gatilho do escape) **não** entra nesta recalibração: é valor de produto da grelha de 23/09 e só muda por alteração explícita dessa decisão (achado F3).
- [x] 4.3 — Cardinalidade do σ (`vol_bp`) no gate: decidir com a segmentação por regime do Card A se entra como condição secundária/fallback; se não entrar, o gate fica só com a previsão.
- [x] 4.4 — Testes: calmo → `regime` e nenhuma ordem; activo → permitido; hurdle passa mas 1,5× não → `regime` (não `hurdle`); nenhum switch por env desliga o gate.

## 5. E — Saída com escape taker

- [x] 5.1 — Nova função de saída agressiva (`MARKET`/IOC) em `backend/app/services/scalp_binance.py` (hoje só `place_post_only`, «Post-only LIMIT/GTX only»), **sem teto de preço**.
- [x] 5.2 — `decide_exit_cycle`: **gatilho = primeiro ciclo em que o fim da janela de espera é atingido** (`seconds_since_fill >= HOLD_AFTER_FILL_S` ≈ 900 s após o fill) com a posição aberta — **não** a marca `stuck` dos 930 s (`STUCK_AFTER_FILL_S` deixa de ser o marcador do gatilho; `state.stuck` mantém o significado de «posição presa» no painel/status). **Reordenar os gates do caminho de saída (contrato visível, achado F1):** a condição de fim de janela/escape tem de ser avaliada **antes** do ramo `if resting is not None → skip_reason="exit_resting"` (hoje devolve antes do `if stuck:` e torna o escape inalcançável quando a saída passiva está resting e não preenche), cancelando a saída passiva do bot não preenchida **e** enviando a agressiva no mesmo ciclo, **sem tentativa passiva extra** e sem o post passivo temporal do fim da janela.
- [x] 5.3 — Registo/alerta **visível** da saída agressiva no log de diagnóstico (WARNING, com motivo próprio e dados da saída — não o token `stuck`); painel e status intocados; invariante: nenhuma posição passa a janela de espera sem tentativa de saída (passiva dentro/na janela ou agressiva no seu fim).
- [x] 5.4 — Testes: saída passiva **postada e não preenchida** ao fim da janela → o escape é **alcançado** (a passiva é cancelada e a agressiva é enviada no mesmo ciclo — o ciclo NÃO fecha em `exit_resting`); posição aberta sem resting após a janela → não inerte (ordem enviada); ordem agressiva sem price cap; o gatilho dispara no fim da janela e **não** espera pelos 930 s; nenhum post passivo novo no fim da janela; painel sem campos novos.

## 6. F — Cadência, payload e latência

- [x] 6.1 — `JEV_TARGET_MS` por env com default **30 s** (30000 ms): valor injectado de `scalp_service` para o gate `jev_target` e para o `last_jev_elapsed_ms` pós-chamada; `scalp_engine` continua puro; `interval` do loop (`0,4 s`) inalterado, `JEV_LATE_MS` (1,5 s) inalterado.
- [x] 6.2 — Janela do payload resumida: agregados do horizonte 900 s + últimos N trades (sem dump de ticks) e bloco de `questions`/`criteria` compactado até **input/call ≤ ~500 tokens** (hoje 1.158), preservando os 10 níveis da ladder `(0, 5, 10, 15, 20, 25, 30, 35, 50, 80)`.
- [x] 6.3 — `latency_ms` medido **depois** do registo de entrada em `request_jev` (hoje `started` abre antes de `log_call_entry`): fecha o P1 residual do review do #1015 sem desligar o registo.
- [x] 6.4 — Testes: requests/h ≥ 15× menores vs 1 Hz; input medido ≤ ~500 tokens com a ladder intacta; `latency_ms` exclui o registo (resposta dentro de `JEV_LATE_MS` não é recusada por `jev_late`).

## 7. G — Observabilidade do `book_toxic`

- [x] 7.1 — Registar no log do #1015 os drivers do flag: `noul` devolvido pelo modelo + features da janela usadas na decisão (`ret_bp`, `vol_bp`, `aggressor_flow`, `spread_bp_mean`, `trade_count`) + o booleano resultante.
- [x] 7.2 — Evidência multi-dia que distinga **opinião do modelo** de **mapeamento errado**; limiar `noul ≥ 0,5` intocado (sem retune neste card); nada no painel/status. **Resequenciada para pós-T14 pelo dono (ok 23/09, como no #1015):** os drivers passam a ser gravados nesta entrega (provado por teste) e a leitura multi-dia é recolhida depois da integração em `develop` (T14) e anexada ao card para a homologação (T15); limiar e painel/status intocados.

## 8. Testes, DEV e evidência

- [x] 8.1 — `black` + pytest focado verdes (scalp: fee/hurdle, regime, confiança, escape agressivo, cadência/payload/latência, drivers do `book_toxic`); `openspec validate card-1025-jev-destravar-entradas --strict --no-interactive` verde.
- [x] 8.2 — Diff sem `frontend/**`, sem rota/HTML, sem base de dados nova, sem dashboard/exportação/Drive, sem backtest, sem PROD, sem segredos.
- [x] 8.3 — Evidência DEV em cada etapa no runtime-worker DEV (`RUN_SCALP_LOOP=1`, o mesmo flag que arma o log do #1015): relatório da régua, hurdle com a fee real, skip `regime`, fecho pelo caminho agressivo **alcançado com uma saída passiva resting não preenchida**, requests/h e tamanho do input. **Resequenciada para pós-T14 pelo dono (ok 23/09, como no #1015):** o runtime-worker DEV corre `develop`; a evidência (régua sobre o log real, fee real lida no DEV, skip `regime`, fecho agressivo com passiva resting não preenchida, requests/h e input) é recolhida **depois da integração em `develop` (T14: squash + `./restart` DEV)** e anexada ao card para a homologação (T15). Prova interina desta entrega: régua sobre o log real + leitura real da fee no DEV + 156 testes focados verdes.
- [x] 8.4 — Fecho da coluna: `/opsx:verify` (quando aplicável), `qa-gate` verde e PR `q_git`; PROD fica no lote (T16). **Executado pelo pai nesta entrada** (o filho Apply não faz `process_event`/commit/PR): `/opsx:verify` + `openspec validate --strict`, `qa-gate` e PR `card-1025-jev-destravar-entradas` → `develop` a seguir ao Code Review (T9/T11) e T14; PROD no lote (T16).
