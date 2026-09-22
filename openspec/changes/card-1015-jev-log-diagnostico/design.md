## Context

Card **#1015**, Status=Design. Briefing = issue grelhado (Problema, História, Entra/Critérios, Não entra), copiado verbatim em `proposal.md`. Sem reentrevista. Relacionado com **#1006** (Done técnico, em homologação). #1001/#1007/#1008 não se reabrem. **SEM-TELA** (log de diagnóstico em ficheiro).

Factos do código actual (lidos no repo, sem alterar nada):

- A chamada ao Jev vive em `backend/app/services/scalp_jev.py::request_jev`: um POST (`urllib`) para `{JEV_BASE_URL|https://api.typesafe.ai}/v1/systemone`, corpo de `_systemone_payload` (`state` + `model: jev-latest` + `questions` `side`/`expected_move_bp`/`book_toxic`), timeout = `JEV_LATE_MS` = 1,5 s. A chave TypeSafe vem só de env (`JEV_API_KEY`/`TYPESAFE_API_KEY`) em `Authorization: Bearer`; `_redact` já substitui a chave por `<redacted>` nas mensagens de erro.
- Hoje só existem dois logs neste módulo, ambos `logger.warning` e só em erro (status HTTP + `latency_ms`; exceção redigida). A chamada de sucesso é invisível: não há registo de entrada, de retorno, nem do status HTTP do sucesso (o `resp.status` nunca segue para log) e o corpo do erro nunca é lido para registo.
- O retorno é um `JevSignal` (`side`, `confidence`, `expected_move_bp`, `book_toxic`, `latency_ms`, `cost_quote`) mapeado por `_map_systemone`; erro ou resposta vazia → `_hold_signal` (side `None`, confiança 0), indistinguível no log de hoje.
- O payload é montado por `backend/app/services/scalp_jev_payload.py::build_jev_payload` a partir da memória do stream (#1008): `state.touch`, `state.window` (900 s de `aggTrade`), `state.account` (`inventory_btc`, `t`, `remaining_to_t`, `fee_bp`, `bnb_fee_active` — valores exactos de saldo/posição) e `state.resting` (`{side, price, age_ms, role}` ou `null`). Sem toque → devolve `(None, "no_book")`; janela sem `aggTrade` → `(None, "window_empty")` — recusa antes da chamada.
- O ciclo é `backend/app/services/scalp_service.py::tick_user`, invocado por `backend/app/services/scalp_loop.py` (tick `max(JEV_FLOOR_MS/1000, 0.4)` s; o relógio de **pergunta** ao Jev é `JEV_TARGET_MS = 1000` — gate `jev_target` — e `jev_in_flight` mantém uma chamada em voo por utilizador).
- O `skip_reason` nasce nas decisões puras `decide_cycle`/`decide_exit_cycle` de `backend/app/services/scalp_engine.py` (módulo sem I/O) como token de `CycleIntent.skip_reason` — `halted`, `switch_off`, `no_spot_key`, `kill`, `position_open`, `jev_in_flight`, `jev_unavailable`, `jev_target`, `need_jev`, `jev_late`, `hold`, `low_confidence`, `hurdle`, `toxic_book`, `t_zero`, `ceiling_reduce_only`, `zero_inventory`, `would_cross`, `dust`; saídas `exit_resting`, `stuck`, `hold_position` — mais `no_book` (fechado em `tick_user`) e `window_empty` (fechado em `build_jev_payload`). O token chega a `CycleResult.skipped` (`None if sent else intent.skip_reason`) em ~10 pontos de fecho de ciclo e **hoje ninguém o escreve em log**: o destino visível é apenas o painel (`calibration_signals`/`calibration_hits` e `/api/scalp/status`).
- Logging hoje: `backend/app/main.py` liga um `logging.FileHandler` **sem rotação** a `backend/full_execution_log.txt`; `backend/app/workers/runtime_worker.py` usa `logging.basicConfig` com `WORKER_LOG_LEVEL` (default INFO) para stderr. O scalp loop corre no runtime-worker com `RUN_SCALP_LOOP=1` — presente em `ops/systemd/criptofarol-dev-runtime-worker.service` e **ausente** do unit PROD.

UI impact: none
live_route: N/A registo de diagnóstico em ficheiro de log; sem tela de produto
surface: new

Sem rota autenticada, sem landing, sem HTML. Nunca emprestar /monitor /favorites /combo/discovery /combo/select landing. Prototype N/A. Impeccable N/A.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Vocabulário

- **Chamada Jev (SystemOne):** um `request_jev` — POST `/v1/systemone` com o corpo `_systemone_payload` — e o respectivo retorno mapeado em `JevSignal`.
- **Entrada:** o corpo enviado (`state`: touch, window, account, resting + `questions`), registado sem segredos e com conta resumida.
- **Retorno:** `side`, `expected_move_bp` (score interpolado em bp), `book_toxic`, confiança, latência e status HTTP; em erro, o corpo do erro resumido.
- **Recusa do ciclo (`skip_reason`):** token do gate que fechou o ciclo sem ordem, tal como nascido em `scalp_engine`/`scalp_service`.
- **Conta resumida:** só boleanos «há posição? há saldo?» (`has_position`, `has_balance`); nunca valores exactos de saldo ou posição.
- **Ficheiro único com tecto de 200 MB (truncagem de cauda):** um só ficheiro de log, tecto de **200 MB (209 715 200 bytes)**; ao encher, o registo mais antigo cai dentro do mesmo ficheiro (truncagem de cauda em fronteira de linha); sem prazo fixo (nada de rotação por tempo, nada de backups `.1`/`.2`).
- **DEV / runtime-worker:** entrega e evidência no unit DEV (`criptofarol-dev-runtime-worker.service`, `RUN_SCALP_LOOP=1`); produção fica para depois da evidência.

## Goals / Non-Goals

**Goals:**

- Cada chamada Jev fica registada em log com entrada (payload enviado, sem segredos, conta só resumida) e retorno (side, expected_move_bp/score, book_toxic, confiança, latência, status HTTP; em erro, corpo resumido) legíveis.
- Cada ciclo sem ordem regista o `skip_reason` do gate que recusou (hold, low_confidence, hurdle, toxic_book, jev_late, jev_target, t_zero, ceiling_reduce_only, floor, window_empty, switch_off, halted, livro indisponível, etc.).
- Nível de log configurável (INFO para envio/retorno, WARNING para erros) sem inundar; cadência (~1 s), hurdle, alvo/stop e qualquer decisão de trading inalterados.
- Zero segredos (chave, token) em logs, painel ou registo; conta nunca em valores exactos de saldo ou posição.
- Ficheiro de log **único** com tecto de **200 MB (209 715 200 bytes)**: ao encher, o registo mais antigo cai no próprio ficheiro (truncagem de cauda em fronteira de linha); sem prazo fixo.
- Só DEV nesta entrega; evidência = log real de várias chamadas (sucesso + uma recusa) observável no runtime-worker.

**Non-Goals:**

- Reabrir #1006 (lookback), #1001 (cadência), #1007 (saída/régua, Cancelado) ou #1008 (stream).
- Consola TypeSafe, backtest, régua/calibração de acerto por horizonte.
- Base de dados nova, dashboard/UI novo no Monitor, exportação/Drive.
- Histórico de trades/ciclos navegável — só log de diagnóstico.
- Mudar regras de entrada/saída, taxa, hurdle, teto ou piso.
- Produção nesta entrega — o registo nasce no DEV.
- Tocar no painel de hoje: o motivo da última recusa fica só no log, não no Monitor.
- Saldos e posições em valores exactos no registo.

## Decisions

1. **Registar nas costuras que já existem — entrada/retorno em `request_jev`, recusa no fecho do ciclo — sem camada nova de telemetria.** O registo de entrada sai onde o corpo SystemOne é montado (o que se loga é o que se enviou); o de retorno sai após o mapeamento, com status HTTP (`resp.status` / `exc.code`) e `latency_ms`; em erro, o corpo é lido, truncado e redigido antes de escrever. A recusa sai de um único helper chamado em todos os caminhos que fecham `tick_user` sem ordem, com o token `skip_reason` tal como está.
   Alternativa rejeitada — **logar só no ciclo**: o corpo enviado e o status HTTP morrem dentro de `request_jev`; o operador continuaria sem ver a entrada.
   Alternativa rejeitada — **decorator/proxy à volta de `request_jev` no `scalp_loop`**: não vê o `skip_reason` (nascido depois, em `tick_user`) e duplica o ponto de verdade do payload.
   Alternativa rejeitada — **base de dados nova / tabela de ciclos**: Não entra (é régua #1007, Cancelado).

2. **Conta resumida e zero segredos por ocasião da formatação do registo — nunca no payload.** O registo de entrada substitui `state.account` pelos boleanos `has_position` / `has_balance`; `inventory_btc`, `t`, `remaining_to_t` e saldos livres não entram no ficheiro. A chave TypeSafe e o header `Authorization` nunca são registados; corpos de erro passam pelo `_redact` existente. O corpo enviado ao Jev continua byte-a-byte como hoje.
   Alternativa rejeitada — **logar o body completo e limpar com regex depois do facto**: frágil (um campo novo vaza) e escreve o segredo por instantes no formatter.
   Alternativa rejeitada — **mascarar só dígitos de saldo/posição**: continua a ser valor exacto disfarçado, contra o critério «nunca valores exactos».

3. **Nível configurável por env num logger dedicado: INFO para envio/retorno, WARNING para erros.** Um logger do diagnóstico (nome exacto = P3) com nível lido de env, default INFO em DEV, para o operador silenciar o ruído sem tocar no código. A chamada de sucesso fica em INFO — é exactamente o que falta hoje.
   Alternativa rejeitada — **nível fixo**: o loop bate ~1/s por utilizador ligado; sem knob o DEV inunda o ficheiro.
   Alternativa rejeitada — **só WARNING**: eliminaria a chamada de sucesso, que é o problema do card.

4. **Ficheiro de log único com tecto de 200 MB (209 715 200 bytes) e truncagem de cauda — cai o mais antigo, sem prazo.** O registo do diagnóstico vai para o seu próprio ficheiro, **um só**, com tecto fixado pelo dono em **200 MB = `200 * 1024 * 1024` = 209 715 200 bytes** (convenção do repo: `backend/app/routes/logs.py::MAX_INCREMENTAL_BYTES = 256 * 1024`, produto de 1024). Ao encher, o registo mais antigo cai **dentro do mesmo ficheiro** (truncagem de cauda), nunca por tempo. O corte é pela cabeça e tem de ser feito em **fronteira de linha**: a linha parcial do início é descartada, senão o primeiro registo do ficheiro fica corrompido/ilegível. Não crescer sem tecto é critério observável.
   Alternativa rejeitada — **`RotatingFileHandler` com backups (`.1`, `.2`, `backupCount`)**: o tecto seria um par `maxBytes` × `backupCount` (o ficheiro activo não fica capado sozinho) e em Python `backupCount=0` **não roda nada** — o ficheiro fica sem tecto; o dono fixou ficheiro único com truncagem de cauda.
   Alternativa rejeitada — **`TimedRotatingFileHandler` / prazo fixo**: o Entra proíbe prazo.
   Alternativa rejeitada — **crescer sem teto em `full_execution_log.txt`**: já é o problema actual (o `logs.py` fala em ficheiros 300 MB+); violaria o critério.
   Alternativa rejeitada — **só stderr/journald**: não satisfaz «ficheiro de log não cresce sem teto; ao encher, o mais antigo desaparece».

5. **`skip_reason` como token cru, em todos os caminhos sem ordem — antes e depois da chamada.** Pré-chamada (`no_book` «livro indisponível», `window_empty`, `switch_off`, `halted`, `no_spot_key`, `kill`, `position_open`, `jev_in_flight`, `jev_unavailable`, `jev_target`, …) e pós-retorno (`hold`, `low_confidence`, `hurdle`, `toxic_book`, `jev_late`, `t_zero`, `ceiling_reduce_only`, `zero_inventory`, `would_cross`, `dust`, …) saem iguais aos tokens de `scalp_engine`/`scalp_service`. Sem tradução para frases (o token é o contrato estável e parseável). O painel e `/api/scalp/status` não recebem o motivo da última recusa — só o log.
   **Fronteira do log de recusa:** o registo cobre só os ciclos fechados por um gate, isto é, com `skip_reason` não nulo. Os fechos sem ordem e sem token — ordem decidida rejeitada pelo broker (`BinanceOrderError` → `result None`), `intent.send=True` sem `live_send` no stand-in sem chave, e `rest_open` que impede o envio — não deixam registo de diagnóstico neste ficheiro (não há aviso nenhum nesses três caminhos: `rest_open` e o stand-in sem `live_send` não passam pelo `scalp post failed …`).
   Alternativa rejeitada — **só gates pós-Jev**: o operador também precisa de ver `window_empty`/`no_book`, que hoje são invisíveis e bloqueiam a chamada inteira.
   Alternativa rejeitada — **copiar o motivo para o painel**: Não entra («Tocar no painel de hoje»).

6. **Só DEV nesta entrega; produção fica para depois da evidência.** O registo liga-se no runtime-worker DEV (`RUN_SCALP_LOOP=1` já está no unit DEV); o unit PROD não ganha flag nem handler. Evidência = ficheiro real com várias chamadas (sucesso + uma recusa) observável no runtime-worker DEV.
   Alternativa rejeitada — **ligar já em PROD «porque é só log»**: o Entra manda provar a evidência no DEV primeiro.
   Alternativa rejeitada — **expor no visualizador de logs / `/api/logs/tail` nesta entrega**: superfície de UI/API nova — o card é sem-tela; fica para depois.

7. **Inalterados garantidos por contrato e teste — o logging é efeito lateral à volta do caminho crítico.** Não toca em `build_jev_payload`, `_systemone_payload`, `_map_systemone`, `decide_cycle`, `decide_exit_cycle` nem em constantes: cadência de pergunta `JEV_TARGET_MS = 1000` (~1 s), hurdle `expected_move_bp > 2 × fee_bp + spread_bp`, alvo `EXIT_TARGET_BP = 35` / stop `EXIT_STOP_BP = -28`, fail-closed de 1,5 s (`JEV_LATE_MS`, timeout do Jev) e fail-closed de frescura 500 ms (`age_ms` ≤ 500). Nada de campos novos no payload «para facilitar o log».
   Alternativa rejeitada — **enriquecer o payload com o resumo da conta**: mudaria o corpo enviado (critério «payload inalterado»).
   Alternativa rejeitada — **registar dentro de `scalp_engine`**: módulo puro sem I/O; quebraria a fronteira da decisão.

## Risks / Trade-offs

- [Risco] Apply escreve o registo dentro de `scalp_engine` (puro) ou dentro de `decide_cycle` → Mitigação: decisão 1 e 7; registo só nas costuras com I/O (`request_jev`, fecho de `tick_user`).
- [Risco] O registo de entrada vaza `account` exacto porque o payload já o transporta → Mitigação: decisão 2; teste que falha se `inventory_btc`/`t`/`remaining_to_t`/saldos aparecerem no ficheiro.
- [Risco] Apply loga headers ou o corpo de erro completo e a chave aparece ecoada → Mitigação: decisão 2; `_redact` + truncagem; teste com chave no corpo de erro.
- [Risco] Flood a ~1/s por utilizador ligado em DEV durante dias → Mitigação: nível configurável (decisão 3) + tecto de 200 MB com truncagem de cauda (decisão 4); default INFO é intencional para a evidência desta entrega.
- [Risco] A truncagem corta a meio de uma linha e o primeiro registo do ficheiro fica corrompido/ilegível → Mitigação: cortar sempre em fronteira de linha (descartar a linha parcial do início); teste prova que a primeira linha do ficheiro truncado continua legível.
- [Risco] Apply liga o registo em PROD «porque é só log» → Mitigação: decisão 6; task de diff/ambiente; o unit PROD não ganha flag.
- [Risco] Alguém reabre o painel para mostrar a última recusa → Mitigação: Non-Goal + cenário de spec; o contrato visível é ficheiro-only.
- [Trade-off] O registo por ciclo sem ordem é ruidoso mesmo com token estável (p.ex. `jev_target` quase sempre entre perguntas) — aceite: é o diagnóstico pedido; o knob do nível é o filtro.

## Apply contract

**Contrato visível (não P3):**

- Log por chamada Jev com entrada legível (payload `state`/`questions`: touch, window, account, resting; conta só resumida `has_position`/`has_balance`; nunca a chave TypeSafe nem qualquer segredo) e retorno legível (side, expected_move_bp/score, book_toxic, confiança, latência, status HTTP; em erro, corpo resumido e redigido).
- Registo de recusa em todo ciclo recusado por um gate (com `skip_reason` não nulo), com o token tal como nasce; o painel não o recebe. Rejeição do broker / stand-in sem chave / `rest_open` não deixam registo neste ficheiro de diagnóstico.
- Nível configurável (INFO envio/retorno, WARNING erros); ficheiro de log **único** com tecto de **200 MB (209 715 200 bytes)**, truncagem de cauda (cai o mais antigo no mesmo ficheiro, em fronteira de linha), sem prazo fixo.
- Só DEV nesta entrega; evidência = log real de várias chamadas (sucesso + uma recusa) no runtime-worker.
- Inalterados: payload SystemOne, cadência ~1 s, hurdle, alvo/stop, fail-closed de 1,5 s, fail-closed de 500 ms, interruptor/T/clip/kill, painel de hoje.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Formato exacto das linhas (chave=valor vs texto corrido) e id de correlação entre entrada e retorno.
- Nome do logger, nomes das envs de nível/on-off e caminho default do ficheiro.
- Implementação fina da truncagem de cauda (onde/como corta: seek/trim no próprio ficheiro, bytes por escrita) — o tecto de **200 MB (209 715 200 bytes)** e o mecanismo (ficheiro único, truncagem de cauda em fronteira de linha) já estão fixados no contrato visível.
- Limite de caracteres do corpo de erro «resumido».
- Campos exactos de `touch`/`window`/`resting` que entram na entrada, desde que a conta fique só resumida e nada de segredos seja escrito.
- Se o caminho stand-in / sem chave regista entrada sintética (com a mesma forma redigida) ou não regista chamada.
- Como os testes injectam o handler de ficheiro temporário e forçam o tecto/truncagem (ficheiro temporário com tecto minúsculo).

## P3 (detalhe de Apply — aceitos, resolvidos no Apply)

- `floor` do Entra não é token real: só se emitem tokens reais (não inventar `floor`); piso/teto lêem-se `zero_inventory` / `ceiling_reduce_only`.
- A recusa cobre também os ciclos de saída: `exit_resting` / `stuck` / `hold_position` entram no mesmo registo (o mesmo `tick_user` fecha os dois tipos de ciclo).
- `has_position` / `has_balance` ficam sem predicado fixado aqui: o predicado exacto (`inventory_btc > 0`, `t > 0`) fixa-se no Apply.
- `_redact` cobre hoje só `JEV_API_KEY`/`TYPESAFE_API_KEY`: no Apply redige-se por lista de envs sensíveis e nunca se logam headers.
- Restantes detalhes já aceites na lista P3 do Apply contract acima (formato de linha e id de correlação, logger e envs, implementação fina da truncagem, limite do corpo de erro, campos de `touch`/`window`/`resting`, caminho stand-in, injecção de handler nos testes).

## Open Questions

Nenhuma. A fronteira veio grelhada; os *como* fecham nas decisões 1–7. A secção de crítica fica para o pai depois do crítico — este autor não submete Design, Gist nem T5.

## Design Critique

Sem-tela. Teto 1+1+1 na 1.ª entrada: 1 autor + 1 crítico + 1 rework (usado). **2.ª entrada** após `devolver_design` (T6, Alan): +1 rework do autor, justificado no prompt pela decisão de produto do dono (tecto do log), sem nova rodada de crítica. Relatórios: `.impeccable/critique/1015-card-1015-jev-log-diagnostico.md` (autor) · `1015-card-1015-jev-log-diagnostico-design-critic.md` (crítico) · `1015-card-1015-jev-log-diagnostico-rework.md` (rework) · `1015-card-1015-jev-log-diagnostico-rework2.md` (rework da 2.ª entrada). Snapshot T7 = relatório do crítico.

**Veredito do crítico: PASS** — rúbrica 1–7: PASS · PASS · PASS · PASS · PASS · N/A (sem tela) · PASS. Tokens do gate em linha própria parseável: `UI impact: none` · `live_route: N/A registo de diagnóstico em ficheiro de log; sem tela de produto` · `surface: new`; sem rota de catálogo emprestada; Prototype N/A / Impeccable N/A.

**P0:** nenhum  
**P1:** nenhum

**P2:** 1 — **corrigido no 1.º rework** · `bloqueia_merge: nao`
- `[P2][contrato-visivel]` O requisito «todo o ciclo sem ordem deixa o gate» era universal, mas há fechos de ciclo sem ordem sem token (`BinanceOrderError` → `result None`; `intent.send=True` sem `live_send` no stand-in sem chave; `rest_open` que impede o envio). — Correção aplicada: requisito/cenário estreitados a «ciclo recusado por um gate (`skip_reason` não nulo)» + fronteira declarada na decisão 5 e no Apply contract (esses fechos não deixam registo de diagnóstico neste ficheiro).

**P3 (aceitos, detalhe de Apply — não reabrir como P0/P1):** 5
- `floor` do Entra não é token real; só se emitem tokens reais (piso/teto = `zero_inventory` / `ceiling_reduce_only`).
- A recusa cobre também os ciclos de saída (`exit_resting` / `stuck` / `hold_position`).
- `has_position` / `has_balance` ficam sem predicado fixado aqui; o predicado exacto fixa-se no Apply.
- `_redact` cobre hoje só `JEV_API_KEY`/`TYPESAFE_API_KEY`: no Apply redige-se por lista de envs sensíveis e nunca se logam headers.
- Restantes detalhes já aceites no Apply contract (formato de linha e id de correlação, logger e envs, limite do corpo de erro, campos de `touch`/`window`/`resting`, caminho stand-in, injecção de handler nos testes; a truncagem fina — seek/trim, bytes por escrita — resolve-se no Apply).

**Disposition:** P2 fechado no 1.º rework. **2.ª entrada (T6 — `devolver_design` por Alan):** o dono fixou o tecto que faltava — **um só ficheiro, 200 MB (209 715 200 bytes), truncagem de cauda** (cai o mais antigo no mesmo ficheiro, em fronteira de linha; sem `RotatingFileHandler`, sem `backupCount`, sem backups, sem prazo). Aplicado no 2.º rework do autor, justificado no prompt pela decisão de produto do dono; `openspec validate --strict` verde. Sem nova rodada de crítica: é valor de contrato fixado pelo dono, não achado novo. P3 → Apply. Escopo do «Não entra» intacto: sem UI/painel, sem base de dados, sem dashboard/exportação/Drive, sem histórico navegável, sem produção, sem mudar regras de trading/hurdle/cadência/teto/piso, sem valores exactos de conta, sem segredos. `openspec validate --strict` verde após o rework. Processo: a 1.ª tentativa do crítico foi cancelada pelo host (sem payload de retorno, sem relatório) → restage com spawn **novo** (não resume); contabilizada em Spawns. Cliente dsh: spawns isolados sem parâmetro `model`; faixas `juizo` registadas pelo mapa vigente em `.cursor/model-map.yaml` (sem parser de usage, sem dashboard).

Spawns: 5
proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: design-critic → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: design-critic (restage) → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: design-autor (rework) → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: design-autor (rework T6) → Grok 4.6 (cursor-grok-4.6-high)
