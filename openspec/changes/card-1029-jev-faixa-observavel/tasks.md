# Tasks — card-1029-jev-faixa-observavel

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.
> Usar as skills do projeto disponíveis no Cursor quando aplicável (`.cursor/skills/`), com o runbook `covenant-flow`.
> `UI impact: none` nesta entrega: nada de painel/Monitor, rota, HTML ou base de dados. Os tokens do gate estão no `design.md`.
> Depende de #1028 (já em `develop`): o registo de veredictos/versão/origem **não** se reabre.

## 1. Faixa relativa ao custo do ciclo (sem limiar novo)

- [x] 1.1 — Em `backend/app/services/scalp_jev.py`, implementar a leitura do **nível já alcançado**: recortar o `score` ao intervalo da escada (dez níveis, `_EXPECTED_MOVE_BP_LEVELS_BP`) e arredondar **para baixo** (`floor`), devolvendo o **bp exacto** desse nível — nunca um valor interpolado.
- [x] 1.2 — Materializar as **três faixas** (`below_cost`, `covers_cost`, `covers_with_slack`) do nível creditado contra o custo real do ciclo, **reusando** `passes_entry_hurdle` (estrito `>`) e `passes_regime_gate` (`>=`) de `backend/app/services/scalp_window.py`, com o `fee_bp`/`spread_bp` do ciclo; **nenhuma** fronteira fixa na escala e **nenhuma** constante/limiar novo.
- [x] 1.3 — Em `backend/app/services/scalp_engine.py`, `reply_gate_verdicts` (l.218-242) e os gates de custo (l.390-410) passam a decidir pela faixa do nível creditado; `below_cost` fecha em `skip_reason="hurdle"`, `covers_cost` em `skip_reason="regime"`, `covers_with_slack` passa a regra de custo — **um motivo só**, sem token próprio para a faixa mais baixa e sem alterar `GATE_ORDER`.
- [x] 1.4 — Não tocar no valor do limiar de confiança nem na ordem dos gates: com o gate removido (`confidence_min=None`), uma posição abaixo do custo fecha **por custo**, nunca por confiança; com o gate ligado e a falhar, o ciclo fecha em `low_confidence` como hoje.

## 2. Fim do artefacto de interpolação

- [x] 2.1 — Retirar a interpolação linear (`_bp_from_score`, `scalp_jev.py:65-81`) do caminho de decisão; `_expected_move_bp` (`scalp_jev.py:284-299`) passa a devolver o bp do **nível já alcançado**.
- [x] 2.2 — Levar a **posição na escala** e o **nível creditado** no `JevSignal` (`scalp_engine.py:161-174`); o campo `expected_move_bp` passa a carregar o bp exacto do nível creditado — **mudança de significado declarada** no `design.md` (decisão 3) — e alimenta os predicados de custo como única entrada.
- [x] 2.3 — Actualizar as asserções de contrato que fixam a interpolação em `backend/tests/unit/test_scalp_direcional_jev.py:490-492` para o nível já alcançado (ex.: `score 4.5` credita o nível 4 = 20 bp, nunca 22,5 bp).

## 3. Rótulo em faixas na pergunta ao modelo

- [x] 3.1 — Em `scalp_jev.py`, tornar `_expected_move_bp_criteria()` (l.55-62) **cost-aware**: as **dez opções ordenadas** continuam a existir e cada rótulo passa a ser a **faixa** daquele nível face ao custo do ciclo, em vez de um número nu; a faixa de cada nível usa os mesmos predicados da decisão (rótulo e leitura coincidem).
- [x] 3.2 — Passar o custo do ciclo (`fee_bp`/`spread_bp`, ou o `hurdle`/slack) até `_systemone_payload`/`_expected_move_bp_criteria` (`scalp_jev.py:182-211`); manter o `type: score` e as dez opções (a resposta continua a ser uma posição) — nomes/forma de passagem são P3.
- [x] 3.3 — Reverificar o orçamento de entrada do #1025 (≤ ~500 tokens por chamada) com o rótulo em faixas.
- [x] 3.4 — Actualizar as asserções de contrato de `backend/tests/unit/test_scalp_jev_consult_cadence.py:243-244` (lista de critérios nus) para o contrato de rótulo em faixas, mantendo `_EXPECTED_MOVE_BP_LEVELS_BP == (0, 5, 10, 15, 20, 25, 30, 35, 50, 80)`.

## 4. Registo com faixa e posição, nunca bp interpolado

- [x] 4.1 — Em `backend/app/services/scalp_jev_log.py::log_call_return` (l.327-378), acrescentar de forma **aditiva** a **faixa** (`move_band`) e a **posição** (`move_position`), mantendo `score=` (score cru) e `expected_move_bp=` com o bp **exacto** do nível creditado; nenhum campo carrega bp interpolado.
- [x] 4.2 — Levar a faixa e a posição ao **registo do ciclo** (`_cycle_suffix` l.390-421, `log_cycle_refusal`/`log_cycle_sent` l.424-482 e `scalp_service.py:_gate_verdict_fields`/`_write_cycle_record` l.806-841), preservando o prefixo `scalp cycle refused` e a adjacência `user= … skip_reason=` (régua read-only).
- [x] 4.3 — Provar que o artefacto quantizado (15,0 / 15,35 / 14,30 / 9,60) deixa de ser produzido e que todo bp registado é um nível da escada (teste com score fraccionário entre níveis).

## 5. A/B da janela de estado

- [x] 5.1 — Registar de forma aditiva, no registo de diagnóstico, o **braço** do A/B (janela actual / janela maior) e a confiança usada, sem alterar a decisão nem o payload de decisão.
- [x] 5.2 — Análise **read-only** sobre os registos que produza a **confiança média** da janela actual e da janela maior, com a **mesma versão fixa de modelo** (pin do #1028) e o **tamanho da amostra** declarado (janelas e observações por braço).
- [x] 5.3 — Concluir **apenas** com **≥30 janelas de 900 s não sobrepostas** (observações na mesma janela contam uma vez); abaixo disso **não concluir** e escrever **`amostra insuficiente`**.
- [x] 5.4 — Garantir que o A/B **não** altera gate, limiar, pergunta ou superfície de produto (read-only).

## 6. Fronteira, higiene e validação

- [x] 6.1 — Sem `frontend/**`, sem rota/HTML, sem painel/Monitor, sem `/api/scalp/status`, sem base de dados, sem dashboard/exportação/Drive/backtest; destino é o ficheiro único de diagnóstico do #1015 (tecto e truncagem de cauda inalterados), **DEV-only**; PROD fora (T16).
- [x] 6.2 — **Não** alterar a régua read-only `scripts/scalp_jev_eval.py` (prefixo e chave do #1015 preservados; campos aditivos na mesma linha).
- [x] 6.3 — Testes: cenários das três capabilities verdes (faixa vs custo, nível já alcançado, rótulo em faixas, registo sem interpolado, A/B com amostra declarada e `amostra insuficiente` abaixo de 30 janelas).
- [x] 6.4 — `openspec validate card-1029-jev-faixa-observavel --strict` verde.

## 7. Tratamento do A/B (rework pós-T18) — janela maior como contrato visível

> Novas tasks do rework. As 22 anteriores ficam concluídas; estas ficam por fazer e são resolvidas no Apply seguinte (após novo T7).

- [x] 7.1 — Criar a configuração efectiva da janela de estado (env do produto; nome final P3) e fazê-la mandar no **conteúdo** da janela: retenção do buffer do stream (`LOOKBACK_SECONDS`/`TRADE_WINDOW_SECONDS`, `scalp_btcusdt_stream.py:24-25`) e horizonte dos agregados enviados ao modelo (`scalp_jev_payload.py:69,115`); a janela maior (referência 3600 s) tem de reter de facto mais trades/spreads e declarar o `horizon_s` efectivo. Não é rótulo.
- [x] 7.2 — Derivar o braço do A/B da **janela efectiva** (`larger` sse janela > 900 s) e remover/inertar `SCALP_JEV_AB_ARM` como autoridade do rótulo (`scalp_jev.py:158-166,587`); garantir a invariante «nunca `ab_arm=larger` com a janela de 900 s enviada» e levar a janela efectiva ao registo.
- [x] 7.3 — Declarar a separação `state window` (contexto: retenção + agregados + `horizon_s`) vs `prediction horizon` (não muda neste card); confirmar que decisão, gates, limiar, geometria alvo/stop e cadência não leem o horizonte e ficam intactos.
- [x] 7.4 — Provar que o orçamento de payload do #1025 (≤ ~500 tokens) se mantém com a janela maior: bloco `window` de forma fixa (sete escalares + `recent_trades` ≤ `RECENT_TRADES_N = 5`); manter/estender o teste `systemone_input_tokens(body) <= 500` (`test_scalp_jev_consult_cadence.py:239`) com a janela maior.
- [x] 7.5 — Recolha dos dois braços por **alternância da configuração entre execuções** do loop DEV (900 s = `current`; 3600 s = `larger`), com o registo a declarar a janela efectiva e o braço derivado; piso de **≥30 janelas de 900 s não sobrepostas por braço**; abaixo disso **`amostra insuficiente`** (mantém a régua read-only `scripts/scalp_jev_window_ab.py`).
- [x] 7.6 — Fixar que **gates, limiar de confiança e a pergunta** (dez opções, `type: score`) são **idênticos** nos dois braços; só o contexto difere, por desenho; a análise read-only não altera nada.
- [x] 7.7 — Testes do contrato novo: janela maior produzida (conteúdo/valores diferentes de 900 s), rótulo derivado (900 s nunca é `larger`; janela maior é `larger`), `horizon_s` declarado = janela efectiva, orçamento ≤ ~500 tokens com a janela maior, `amostra insuficiente` abaixo de 30 janelas.
- [x] 7.8 — `openspec validate card-1029-jev-faixa-observavel --strict` verde.

