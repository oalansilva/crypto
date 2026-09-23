## Context

Card **#1028**, Status=Design. Briefing = issue grelhado (Problema, História, Entra/Critérios, Não entra, Factos e Decisões fechadas), copiado verbatim em `proposal.md`. Sem reentrevista. **Pré-requisito de #1029 e #1030** (calibração): sem veredicto de todos os gates e sem origem/versão, não existe dado para calibrar. Relacionado com **#1025** (Done técnico, homologado). **SEM-TELA** (backend/log; o destino é o ficheiro de diagnóstico do #1015). #1001/#1006/#1007/#1008 não se reabrem.

Factos do código actual (lidos no worktree, sem alterar nada):

- As regras de entrada decidem **em ordem e param na primeira recusa**: `backend/app/services/scalp_engine.py::decide_cycle` devolve o primeiro `CycleIntent` que fecha o ciclo — `halted`/`switch_off:204`, `no_spot_key:212`, `kill:220`, `position_open:235`, `jev_in_flight:245`, `jev_unavailable:253`, `jev_target:265`, `need_jev:273`, `jev_late:282`, `hold:292`, `low_confidence:300`, `hurdle:308`, `regime:319`, `toxic_book:327`, `t_zero:335`, `ceiling_reduce_only:347`, `zero_inventory:355`, `would_cross:365`, `dust:392` (verde em `:403`). A recusa por confiança (`:300`) fica **antes** de custo (`:308`), custo com folga (`:319`) e toxicidade (`:327`).
- O `skip_reason` é o único dado do ciclo registrado hoje: `backend/app/services/scalp_service.py::tick_user` escreve o registro quando `result.skipped` é não nulo (`:830-831`) e `backend/app/services/scalp_jev_log.py::log_cycle_refusal` (l.357-361) grava só `scalp cycle refused user=%s skip_reason=%s`. Nenhum veredicto dos outros gates é calculado ou escrito.
- O **tempo limite** da chamada e o corte de recusa por atraso são o **mesmo número**: `backend/app/services/scalp_jev.py::request_jev` usa `timeout = JEV_LATE_MS / 1000.0` (l.303-305), com `JEV_LATE_MS = 1500` em `scalp_engine.py:16`, e `decide_cycle` recusa com `jev_late` quando `jev.latency_ms > JEV_LATE_MS` (`scalp_engine.py:277`). No caminho de erro de transporte o `latency_ms` é forçado para `>= JEV_LATE_MS + 1` (`scalp_jev.py:346,367`).
- A **origem da confiança** está fundida no valor: `scalp_jev.py::_side_confidence` (l.207-218) devolve `side_answer.confidence` quando existe e, só quando não existe, cai em `probabilities[choice]`/`probabilities[choice.upper()]`; devolve um `Decimal` só, sem dizer qual ramo respondeu.
- A **toxicidade é corte único**: `scalp_jev.py::_noul_yes` (l.203-204) devolve `_decimal(answers["book_toxic"]["noul"]) >= Decimal("0.5")`, consumido por `_map_systemone` (l.248) como o booleano `book_toxic` do `JevSignal`.
- O modelo pedido é o **apelido** `_JEV_MODEL = "jev-latest"` (`scalp_jev.py:33`), enviado em `_systemone_payload` como `"model": _JEV_MODEL` (l.156). A resposta traz um identificador de versão (fixture real do repo: `"model": "jev-1.13.0"` em `backend/tests/unit/test_scalp_direcional_jev.py:376`).
- A versão que respondeu **não é gravada por omissão**: o campo `model` da resposta só aparece no registro cru opt-in `log_call_raw` (`scalp_jev_log.py:410-441`), armado por `raw_payload_enabled()` = `SCALP_JEV_RAW_PAYLOAD` (`scalp_jev_log.py:102-108`), desligado por defeito.
- O registro de retorno do #1015 vive em `scalp_jev.py:378-390` (`log_call_return` com `noul=` e `window=`) e em `scalp_jev_log.py:305-346`; o de entrada em `scalp_jev.py:320`.
- Testes que **codificam o contrato de hoje a mudar**: `backend/tests/unit/test_scalp_direcional_jev.py:466` (`captured["timeout"] == JEV_LATE_MS / 1000.0`) e `:468` (`body["model"] == "jev-latest"`). A decisão de compra/venda não é tocada; o que muda é o tempo limite e o identificador pedido.
- A **régua read-only** do #1025 lê o ficheiro do #1015 com três regexes (`scripts/scalp_jev_eval.py:90-94`): entrada, retorno e `RefusalRe = \sscalp cycle refused user=(\S+) skip_reason=(\S+)`; os campos são lidos por `KVRe` sobre `k=v` (l.93), que **tolera campos adicionais** na mesma linha.
- O **loop é sequencial por utilizador** (`backend/app/services/scalp_loop.py:87-98`: `await asyncio.to_thread(_tick_user_blocking, ...)` por `user_id`), pelo que o tempo limite da chamada bloqueia o avanço do loop até ele expirar.
- **DEV-only**: o handler do diagnóstico só é instalado quando `diagnostic_enabled()` (`scalp_jev_log.py:93-99`, `SCALP_JEV_LOG_ENABLED` ou `RUN_SCALP_LOOP`); o unit DEV corre com `RUN_SCALP_LOOP=1` (`ops/systemd/criptofarol-dev-runtime-worker.service`) e o unit PROD não tem a flag.

UI impact: none
live_route: N/A registro de veredictos em ficheiro de log; sem tela de produto
surface: new

Sem rota autenticada, sem landing, sem HTML. Nunca emprestar `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, `landing`. Prototype **N/A**. Impeccable **N/A**.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Vocabulário

- **Gate de entrada:** uma regra de `decide_cycle` que, ao falhar, fecha o ciclo sem ordem com um `skip_reason` (token cru). Neste card, os gates **alimentados pela resposta do modelo**.
- **Veredicto:** `pass` (a regra aceitaria), `fail` (a regra recusaria) ou `not_applicable` (a regra está desligada/configurada fora — p.ex. limiar de confiança removido), calculado **independentemente** do primeiro gate que fechou o ciclo.
- **Registro do ciclo:** a linha do ficheiro de diagnóstico do #1015 que fecha um ciclo (`scalp cycle refused` ou, novo, `scalp cycle sent`), com o `skip_reason` e os veredictos no **mesmo** registro.
- **Origem da confiança:** qual ramo produziu o número usado — `reply_field` (campo de confiança da resposta) ou `choice_probability` (probabilidade da opção escolhida); `none` quando não há nenhum dos dois.
- **Faixa de incerteza da toxicidade:** o intervalo `[0,4, 0,6]` de `noul` onde o registro marca a leitura como `indeterminate` (nem tóxico nem não tóxico). **Só etiqueta**: não altera o booleano de decisão.
- **Versão do modelo:** identificador de versão fixa pedido na chamada (`model` do corpo), distinto do apelido móvel `jev-latest`; e a versão que **respondeu** (`model` da resposta), gravada no registro.
- **Não-regressão:** com a mesma entrada, o `CycleIntent` (e portanto `send`/`skip_reason`) antes e depois é o mesmo; os campos novos do registro são efeito lateral.

## Goals / Non-Goals

**Goals:**

- Todo ciclo com resposta do modelo deixa **um** registro com o veredicto de cada gate de entrada alimentado pela resposta — custo (`hurdle`), custo com folga (`regime`), toxicidade (`toxic_book`), confiança (`low_confidence`) — mais `jev_late` e `hold`, mesmo quando um gate anterior já recusou o ciclo.
- O registro diz a **origem da confiança** usada e a **versão do modelo** que respondeu.
- A toxicidade ganha **dois cortes (0,4 / 0,6)** e uma **faixa de incerteza** visíveis no registro; a decisão de compra/venda fica pelo corte de hoje (≥ 0,5).
- O **tempo limite da chamada passa a 3 s**, com a recusa de resposta acima de **1,5 s** inalterada; as respostas entre 1,5 s e 3 s deixam de se perder.
- A chamada pede uma **versão fixa** em vez do apelido `jev-latest`.
- **Não-regressão**: com a mesma entrada, o resultado da decisão é o mesmo.

**Non-Goals:**

- Mudar o valor do limiar de confiança (`CONFIDENCE_MIN`) ou a pergunta feita ao modelo (faixas/níveis/tipos).
- Mudar a ordem das regras ou o primeiro gate que decide (o primeiro `skip_reason` continua o mesmo).
- Expor no painel/Monitor/`/api/scalp/status` (a recusa e os veredictos ficam só no log — decisão do #1015).
- Base de dados nova, dashboard, exportação/Drive, backtest, régua nova.
- Mudar hurdle/regime/alvo/stop/cadência/fail-closed de frescura/payload SystemOne.
- PROD nesta entrega (T16, no lote).

## Decisions

1. **O veredicto de todos os gates nasce no motor puro, sem parar na primeira recusa para efeito de registro.** `decide_cycle` continua a devolver o **mesmo** `CycleIntent` de hoje (a decisão não muda) e passa a devolver, no mesmo intent, um mapa imutável de veredictos dos gates alimentados pela resposta — `jev_late`, `hold`, `low_confidence`, `hurdle`, `regime`, `toxic_book` — cada um `pass`/`fail`/`not_applicable`, avaliado independentemente do que fechou o ciclo. O serviço escreve o registro do ciclo com esse mapa. O motor continua **puro** (sem I/O, sem env): devolve dados, não escreve log.
   Alternativa rejeitada — **recalcular os veredictos no `scalp_service`** a partir dos helpers (`passes_entry_hurdle`, `passes_regime_gate`, comparação de confiança): duplicaria os limiares e divergiria assim que um gate muda (o próprio #1025 introduziu/alterou gates).
   Alternativa rejeitada — **registrar só o primeiro motivo, como hoje**: é exactamente o problema do card (0 registros com veredicto de custo/regime/toxicidade).
   **Fronteira declarada:** os gates que **não** leem a resposta do modelo — `t_zero`, `ceiling_reduce_only`, `zero_inventory`, `would_cross`, `dust` — ficam **fora** do conjunto desta entrega (dependem de inventário/quote, não do modelo); se entrarem, é aditivo (P3).

2. **Um só registro por ciclo, com o prefixo e a chave do #1015 preservados.** O ciclo **recusado** continua a escrever `scalp cycle refused user=... skip_reason=<token>` e ganha, na **mesma** linha, os campos aditivos; o ciclo **enviado** (que hoje não deixa registro de ciclo) passa a escrever `scalp cycle sent user=...` com os mesmos campos e `skip_reason=none`. `skip_reason` continua a ser o **primeiro** gate que fechou o ciclo, com o token cru.
   Alternativa rejeitada — **prefixo novo para os dois casos**: quebraria a régua read-only do #1025 (`RefusalRe` em `scripts/scalp_jev_eval.py:92`), que é o instrumento já em uso.
   Alternativa rejeitada — **um segundo registro só para os veredictos**: violaria o "no mesmo registro" do Entra.
   Alternativa rejeitada — **não registrar o ciclo enviado**: o critério «dado um ciclo com resposta do modelo, existe registro com a origem e a versão» cobre também o ciclo que passou em todos os gates.
   **Compatibilidade:** a régua lê `skip_reason=(\S+)` e campos `k=v` por `KVRe`; campos extra na mesma linha não a quebram (não se altera a régua — Não entra).

3. **A origem da confiança é produzida junto com o valor — uma função, dois retornos.** `_side_confidence` passa a devolver `(valor, origem)`, com origem em `reply_field` / `choice_probability` / `none`; o valor devolvido é exactamente o que a decisão consome e é esse par que segue para o registro.
   Alternativa rejeitada — **derivar a origem no caminho do log a partir da resposta crua**: seriam duas leituras do mesmo campo, e a origem registrada poderia divergir do valor usado na decisão.

4. **Toxicidade com dois cortes e faixa, só etiqueta; a decisão fica no corte de hoje.** `noul < 0,4` → `not_toxic`; `0,4 <= noul <= 0,6` → `indeterminate`; `noul > 0,6` → `toxic`; resposta sem `noul` → `unknown`. O booleano de decisão `book_toxic` continua `noul >= 0,5` (inalterado) e é ele que entra em `decide_cycle`. O registro mostra o rótulo **e** o booleano, para a leitura indeterminada não ser confundida com uma mudança de decisão.
   Alternativa rejeitada — **decidir pela faixa** (tratar a faixa como bloqueio ou como tóxico): mudaria a decisão de compra/venda — Não entra.
   Alternativa rejeitada — **faixa aberta** (`< 0,4` tóxico-baixo etc. com `0,6` fora): a grelha fixa **0,4 a 0,6** como indeterminado, inclusive nos extremos.

5. **Versão do modelo: pedir fixa e gravar a que respondeu.** O `model` do corpo deixa de ser o apelido `jev-latest` e passa a ser um identificador de **versão fixa** (configurado/pinado); a versão que **respondeu** (`model` da resposta) é gravada em todo registro, **independentemente** do opt-in `SCALP_JEV_RAW_PAYLOAD` (que hoje é o único sítio onde ela aparece). O `model` que respondeu viaja do cliente para o serviço com o sinal, para entrar no registro do ciclo.
   Alternativa rejeitada — **manter o apelido e só gravar a versão que respondeu**: mantém a mudança silenciosa do fornecedor, que é metade do problema do card.
   Alternativa rejeitada — **cair no apelido quando a versão pinada não estiver configurada**: reintroduziria o apelido no caminho da chamada; o default é uma versão fixa.
   O **valor concreto** da versão pinada é um facto de ambiente lido da resposta do DEV no Apply (P3): a resposta actual traz `model` (fixture `jev-1.13.0`) e esse é o valor a fixar.

6. **Tempo limite da chamada = 3 s, recusa de atraso > 1,5 s inalterada.** Entra um valor de contrato novo (3 s, constante pura ao lado de `JEV_LATE_MS`) usado como **tempo limite por omissão** de `request_jev`; `JEV_LATE_MS = 1500` continua a alimentar o gate `jev_late`. Assim, uma resposta entre 1,5 s e 3 s chega, é mapeada e **registrada**, e o ciclo continua a ser recusado por `jev_late` — o mesmo resultado de hoje, agora com dado.
   Alternativa rejeitada — **subir o `JEV_LATE_MS` para 3 s**: mudaria o fail-closed e a decisão (a grelha manda manter a recusa em 1,5 s).
   Alternativa rejeitada — **manter o tempo limite em 1,5 s**: as respostas entre 1,5 s e 3 s continuam a fechar como erro (sem veredicto), que é o que o card vem corrigir.

7. **Não-regressão provada por teste de decisão, não por inspecção.** Um teste compara o `CycleIntent` (e o resultado `skipped`/`sent`) para a mesma entrada antes/depois, cobrindo os cenários de recusa por confiança, hurdle, regime, tóxico, atraso e o verde; os campos novos do registro são **efeito lateral** que nunca entra na decisão. Os dois testes que fixam o contrato de configuração a mudar (`timeout == JEV_LATE_MS/1000` e `model == "jev-latest"`) passam a afirmar o contrato novo (3 s e versão fixa) — é configuração, não decisão.
   Alternativa rejeitada — **confiar na revisão visual do diff**: o critério é observável e o teste tem de o provar.

8. **Só log; sem superfície nova.** Reutiliza-se o logger, o ficheiro único e a truncagem de cauda do #1015 (`scalp_jev_log.py`); nada de painel, rota, `/api/scalp/status`, base de dados, exportação/Drive, PROD.
   Alternativa rejeitada — **expor os veredictos no Monitor**: Não entra (decisão do #1015).

## Risks / Trade-offs

- [Risco] O `decide_cycle` deixar de ser "primeira recusa e sai" também na **decisão** (não só no registro) — regressão grave de comportamento. Mitigação: decisão 1 e 7; o intent devolvido tem de ser idêntico; teste de não-regressão por cenário.
- [Risco] Recalcular a confiança/toxicidade no caminho do log e divergir do valor decidido. Mitigação: decisão 3 e 4; valor e origem/rótulo saem da mesma função.
- [Risco] A faixa de toxicidade ser lida (ou implementada) como mudança de decisão. Mitigação: decisão 4 + cenário de spec que prova `book_toxic` inalterado com o mesmo `noul` (p.ex. `noul = 0,45` continua verde no gate).
- [Risco] O tempo limite de 3 s bloquear o loop (sequencial por utilizador, `scalp_loop.py:87-98`) até 3 s em vez de 1,5 s. Mitigação: a cadência pós-#1025 é 30 s (`SCALP_JEV_TARGET_MS`, default 30000) e o bloqueio é limitado ao tempo limite; declarado — a decisão não muda.
- [Risco] `last_jev_elapsed_ms = max(_jev_target_ms(), int(signal.latency_ms))` (`scalp_service.py:1117`) passa a receber a latência real (até 3 s) em vez do corte (~1,5 s) numa resposta lenta; com `SCALP_JEV_TARGET_MS` abaixo de 3 s isso poderia subir o intervalo mínimo pós-chamada. Mitigação: com o default de 30 s o `max` é dominado pela cadência (efeito nulo); declarado no Apply contract; teste com o default.
- [Risco] Mudar o prefixo ou a chave do registro do #1015 quebrar a régua read-only do #1025. Mitigação: decisão 2; prefixo `scalp cycle refused` e `skip_reason` preservados; campos aditivos; a régua não é alterada.
- [Risco] Pinar uma versão errada e a chamada passar a falhar no fornecedor. Mitigação: o valor vem da versão que o DEV responde e fica gravado em cada registro (decisão 5); rollback = repor o valor por configuração.
- [Trade-off] Registros do ciclo mais gordos (mais bytes) no ficheiro com tecto de 200 MB e truncagem de cauda. Aceite: o tecto e a truncagem do #1015 já limitam o ficheiro; o dado é o que o card pede.
- [Trade-off] Passar a registrar o ciclo **enviado** aumenta o volume (~1 registro por ciclo com resposta). Aceite: é metade do critério observável (origem + versão em todo ciclo com resposta).

## Apply contract

**Contrato visível (não P3):**

- **Veredicto de todos os gates no mesmo registro:** todo ciclo com resposta do modelo deixa um registro (recusado: `scalp cycle refused`, com o primeiro `skip_reason`; enviado: `scalp cycle sent`, `skip_reason=none`) com o veredicto `pass`/`fail`/`not_applicable` de **cada** gate alimentado pela resposta — `hurdle` (custo), `regime` (custo com folga), `toxic_book` (toxicidade), `low_confidence` (confiança), mais `jev_late` e `hold` — mesmo quando um gate anterior já recusou. Os gates de dimensionamento (`t_zero`, `ceiling_reduce_only`, `zero_inventory`, `would_cross`, `dust`) ficam fora (não leem a resposta).
- **Origem da confiança:** todo registro diz a origem do número usado — `reply_field`, `choice_probability` ou `none` — e o valor.
- **Versão do modelo:** todo registro traz a versão que **respondeu** (campo `model` da resposta; `unknown` se ausente) e a chamada pede um identificador de versão **fixo** (nunca `jev-latest`).
- **Toxicidade:** três rótulos visíveis no registro — `not_toxic` (`noul < 0,4`), `indeterminate` (`0,4 <= noul <= 0,6`), `toxic` (`noul > 0,6`) — mais `unknown` sem valor; a **decisão continua** `book_toxic = (noul >= 0,5)`, inalterada.
- **Tempo limite:** a chamada ao modelo usa **3 s**; a recusa de resposta acima de **1,5 s** (`jev_late`) fica inalterada; uma resposta entre 1,5 s e 3 s é registrada e o ciclo continua recusado por atraso.
- **Não-regressão:** com a mesma entrada, o resultado da decisão (`send`/`skip_reason`) antes e depois é o mesmo.
- **Só log:** destino é o ficheiro de diagnóstico do #1015 (logger, ficheiro único, tecto de 200 MB e truncagem de cauda inalterados); nada de painel/Monitor/`/api/scalp/status`, rota, HTML, base de dados, exportação/Drive; DEV-only.

**P3 — detalhe de Apply (aceito aqui, resolvido no Apply — não reabrir como P0/P1):**

- Nomes exactos das chaves dos veredictos na linha (`hurdle=`, `regime=`, `toxic_book=`, `low_confidence=`, `jev_late=`, `hold=`) ou um mapa único `gates={...}`; ordem dos campos; separador.
- Nome e valor concreto da configuração/constante da **versão fixa** do modelo (valor = a versão que o DEV responder no Apply, lida do campo `model`) e se se mantém override por env.
- Nome da constante/env do **tempo limite** (3 s) e se o override por argumento de `request_jev` continua a existir.
- Conjunto exacto dos gates de dimensionamento; se `t_zero`/`ceiling_reduce_only`/`zero_inventory`/`would_cross`/`dust` entrarem no mapa, é aditivo.
- Rótulo do `noul` ausente (`unknown`) e como aparece no registro; valor de `not_applicable` quando o limiar de confiança está removido (`SCALP_CONFIDENCE_MIN=none`).
- Como o cliente transporta `model` e a origem da confiança até ao serviço (ampliar o `JevSignal` com campos de diagnóstico vs outro transporte) — desde que a decisão continue a ler só os campos de hoje.
- Como os testes injectam resposta/`urlopen` falsos e verificam os campos novos no ficheiro; actualização das duas asserções de contrato de configuração (`test_scalp_direcional_jev.py:466,468`).

## Open Questions

Nenhuma. A fronteira veio grelhada; os *como* fecham nas decisões 1–8. Os factos que faltam (valor concreto da versão pinada) são de ambiente DEV e resolvem-se no Apply, não com o dono.

## Design Critique

Sem-tela. Teto 1+1+1 na 1.ª entrada: **1 autor + 1 crítico, sem rework** — nenhum P0/P1 de produto/escopo/contrato visível. Relatórios: `.impeccable/critique/1028-card-1028-jev-veredictos-origem.md` (autor) · `.impeccable/critique/1028-card-1028-jev-veredictos-origem-design-critic.md` (crítico). Snapshot T7 = o relatório do crítico.

**Veredito do crítico: PASS** — rúbrica 1–7: PASS · PASS · PASS · PASS · PASS · PASS · PASS (item 7 = sem tela: Prototype **N/A** / Impeccable **N/A** declarados; sem protótipo, sem acessibilidade visual, sem clone de página viva). Tokens do gate do autor em linha própria parseável e verificados: `UI impact: none` · `live_route: N/A registro de veredictos em ficheiro de log; sem tela de produto` · `surface: new`; sem rota de catálogo emprestada. `proposal.md` copia `## Problema`, `## História` e `## Entra` **verbatim** do issue grelhado.

**P0:** nenhum
**P1:** nenhum
**P2:** nenhum

**P3 (aceitos, detalhe de Apply — não reabrir como P0/P1):** 3 do crítico, somados aos já aceitos no Apply contract
- Alcance do requisito «todo ciclo com resposta do modelo deixa um registro»: `tick_user` fecha com `skipped=None` (logo sem registro) em rejeição do broker, stand-in sem `live_send` e `rest_open` a bloquear o envio (`scalp_service.py:813-818,1361`) — declarar no Apply contract como esses fechos são registados (ou que ficam fora), sem inventar chave.
- Adjacência `user= … skip_reason=` na linha `scalp cycle refused`: a régua read-only do #1025 (`scripts/scalp_jev_eval.py:92`, `RefusalRe`) exige a ordem actual; campos aditivos só **depois** de `skip_reason`.
- Requisito de versão do modelo no registro de **entrada** (`log_call_entry`), escrito antes da resposta: circunscrever ao registro de retorno/do ciclo ou declarar que a entrada leva a versão **pedida**.
- (Já no Apply contract) nomes/forma das chaves dos veredictos, nome/valor concreto da versão pinada (facto de DEV, lido no Apply), nome da constante/env do tempo limite de 3 s, conjunto exacto dos gates de dimensionamento, rótulos `unknown`/`not_applicable`, transporte de `model`/origem da confiança, e a forma como os testes injectam resposta/`urlopen`.

**Disposition:** nenhum P0/P1/P2 — sem rework; o crítico correu **uma** vez (teto sem-tela). P3 → Apply. Escopo do `## Não entra` intacto: sem mudar limiar de confiança nem a pergunta ao modelo, sem painel/Monitor/`/api/scalp/status`, sem base de dados/dashboard/exportação/Drive/backtest, PROD fora (T16). Contrato visível do dono preservado com os valores exactos: faixa de toxicidade **só etiqueta** com a decisão continua ≥ 0,5 · cortes **0,4/0,6** · tempo limite **3 s** com recusa **1,5 s inalterada** · versão fixa **nesta entrega** + versão que respondeu gravada · veredicto de todos os gates no **mesmo** registro · **não-regressão** da compra/venda. `openspec validate --strict` verde.

Spawns: 2
proxy modelo: design-autor → deepseek-flash (deepseek-flash)
proxy modelo: design-critic → deepseek-flash (deepseek-flash)
