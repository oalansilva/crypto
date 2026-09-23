# Relatório do autor — Design do card #1028

**Change:** `openspec/changes/card-1028-jev-veredictos-origem/`
**Branch/worktree:** `card-1028-jev-veredictos-origem` @ `/srv/apps/dev/criptofarol/crypto-worktrees/card-1028-jev-veredictos-origem`
**Status:** Design. Sem-tela (`UI impact: none`). Prototype N/A. Impeccable N/A.
**Nota:** este relatório é do autor; não declara veredito de crítica.

## 1. Resumo do design

O card #1028 é backend/log e é o **pré-requisito de #1029 e #1030** (calibração). O design entrega, no ficheiro de diagnóstico do #1015 (mesmo logger, ficheiro único e truncagem de cauda), quatro coisas sem tocar na decisão de compra/venda:

1. **Veredicto de todos os gates de entrada no mesmo registro.** Hoje `decide_cycle` decide em ordem e para na primeira recusa; só o primeiro `skip_reason` é escrito. Passa a devolver (sem mudar a decisão) o veredicto `pass`/`fail`/`not_applicable` de cada gate alimentado pela resposta — `hurdle` (custo), `regime` (custo com folga), `toxic_book` (toxicidade), `low_confidence` (confiança), mais `jev_late` e `hold` — e o serviço escreve **um** registro por ciclo (recusado ou enviado) com esse mapa.
2. **Origem da confiança.** Uma função devolve `(valor, origem)`, com origem em `reply_field` / `choice_probability` / `none`; a origem registrada é a do valor exacto que a decisão consumiu.
3. **Versão do modelo.** A chamada pede um identificador de versão **fixa** (nunca o apelido `jev-latest`) e a versão que **respondeu** (`model` da resposta) é gravada em todo registro, independentemente do opt-in `SCALP_JEV_RAW_PAYLOAD`.
4. **Toxicidade com dois cortes e faixa.** `not_toxic` (< 0,4) / `indeterminate` (0,4–0,6, inclusive) / `toxic` (> 0,6) / `unknown` (sem valor); **só etiqueta** — a decisão continua `noul >= 0,5`.
5. **Tempo limite 3 s** com a recusa de atraso **1,5 s** inalterada: as respostas entre 1,5 s e 3 s deixam de se perder e são registradas.

Capabilities novas: `scalp-jev-entry-verdicts`, `scalp-jev-model-version`, `scalp-jev-toxicity-band`, `scalp-jev-call-timeout`. Modified: nenhuma (os registos do #1015 são estendidos de forma aditiva, preservando prefixo e chave lidos pela régua read-only do #1025).

## 2. Decisões e alternativas rejeitadas

1. **Veredicto no motor puro, sem parar na primeira recusa para efeito de registro.** Motor continua puro (devolve dados, não escreve log); a decisão devolvida fica idêntica.
   - Rejeitado: recalcular os veredictos no `scalp_service` (duplicaria limiares; divergiria quando um gate muda).
   - Rejeitado: continuar a registrar só o primeiro motivo (é o problema do card).
   - Fronteira: gates de dimensionamento (`t_zero`, `ceiling_reduce_only`, `zero_inventory`, `would_cross`, `dust`) não leem a resposta → fora do conjunto desta entrega.
2. **Um só registro por ciclo, com prefixo e chave do #1015 preservados.** `scalp cycle refused … skip_reason=<token>` ganha campos aditivos; o ciclo enviado ganha `scalp cycle sent …` com `skip_reason=none`.
   - Rejeitado: prefixo novo (quebraria a régua read-only `scripts/scalp_jev_eval.py`, `RefusalRe`).
   - Rejeitado: um segundo registro só para os veredictos (viola "no mesmo registro").
   - Rejeitado: não registrar o ciclo enviado (o critério cobre o ciclo que passa em todos os gates).
3. **Origem da confiança produzida junto com o valor (um par, dois retornos).**
   - Rejeitado: derivar a origem no caminho do log a partir do cru (duas leituras; poderia divergir do valor usado).
4. **Toxicidade: faixa só etiqueta; decisão no corte de hoje (≥ 0,5).**
   - Rejeitado: decidir pela faixa (mudaria compra/venda — Não entra).
   - Rejeitado: faixa aberta nos extremos (a grelha fixa 0,4–0,6 como indeterminado, inclusive).
5. **Versão: pedir fixa e gravar a que respondeu.**
   - Rejeitado: manter o apelido e só gravar a versão (mantém a mudança silenciosa do fornecedor).
   - Rejeitado: cair no apelido quando a versão pinada não está configurada (reintroduz o apelido).
   - Valor concreto da versão pinada = facto de ambiente DEV capturado no Apply (P3).
6. **Tempo limite 3 s, recusa de atraso 1,5 s inalterada.**
   - Rejeitado: subir o `JEV_LATE_MS` para 3 s (mudaria o fail-closed e a decisão).
   - Rejeitado: manter o tempo limite em 1,5 s (as respostas 1,5–3 s continuam a perder-se).
7. **Não-regressão provada por teste de decisão, não por inspecção.** Mesma entrada → mesmo `CycleIntent`/`skip_reason`/`send`; as duas asserções de configuração que fixam o comportamento antigo são actualizadas (config, não decisão).
   - Rejeitado: confiar na revisão visual.
8. **Só log; sem superfície nova.**
   - Rejeitado: expor no Monitor (Não entra, decisão do #1015).

## 3. Factos com ficheiro:linha (verificados no worktree)

- `backend/app/services/scalp_engine.py:204,212,220,235,245,253,265,273,282,292,300,308,319,327,335,347,355,365,392,403` — `decide_cycle` decide em ordem e para na primeira recusa; a confiança (`:300`) fica antes de custo (`:308`), custo com folga/regime (`:319`) e toxicidade (`:327`).
- `backend/app/services/scalp_engine.py:16` — `JEV_LATE_MS = 1500`; `:277` — gate `jev_late` (`jev.latency_ms > JEV_LATE_MS`); `:19` — `JEV_TARGET_MS = 30000` (cadência pós-#1025, injectada).
- `backend/app/services/scalp_jev.py:303-305` — `timeout = JEV_LATE_MS / 1000.0` (tempo limite = corte de recusa).
- `backend/app/services/scalp_jev.py:203-204` — `_noul_yes`: toxicidade é corte único `noul >= 0.5`; consumido em `:248`.
- `backend/app/services/scalp_jev.py:207-218` — `_side_confidence`: campo de confiança da resposta quando existe; fallback `probabilities[choice]`/`[choice.upper()]`; devolve só um `Decimal` (origem fundida).
- `backend/app/services/scalp_jev.py:33` — `_JEV_MODEL = "jev-latest"`; `:156` — `"model": _JEV_MODEL` no corpo.
- `backend/app/services/scalp_jev.py:378-390` — `log_call_return` (com `noul=` e `window=`); `:320` — `log_call_entry`.
- `backend/app/services/scalp_service.py:830-831` — `tick_user` registra só quando `result.skipped` é não nulo.
- `backend/app/services/scalp_jev_log.py:357-361` — `log_cycle_refusal` grava só `scalp cycle refused user=… skip_reason=…`.
- `backend/app/services/scalp_jev_log.py:102-108` — `raw_payload_enabled()` = `SCALP_JEV_RAW_PAYLOAD` (opt-in, desligado por defeito); `:410-441` — `log_call_raw`, único sítio com `model=`.
- `backend/app/services/scalp_jev_log.py:93-99` — DEV-only (`SCALP_JEV_LOG_ENABLED`/`RUN_SCALP_LOOP`); `:41-50` — tecto `MAX_LOG_BYTES = 200*1024*1024` e truncagem de cauda.
- `backend/tests/unit/test_scalp_direcional_jev.py:376` — a resposta traz `"model": "jev-1.13.0"`; `:466` — `timeout == JEV_LATE_MS/1000.0`; `:468` — `body["model"] == "jev-latest"` (asserções de contrato antigo a actualizar).
- `scripts/scalp_jev_eval.py:90-94` — regexes da régua read-only: `RefusalRe` lê `scalp cycle refused … skip_reason=`, `KVRe` lê `k=v` (tolera campos extra).
- `backend/app/services/scalp_loop.py:87-98` — loop sequencial por utilizador (`await asyncio.to_thread`), logo o tempo limite bloqueia o avanço.
- `backend/app/services/scalp_service.py:1117` — `last_jev_elapsed_ms = max(_jev_target_ms(), int(signal.latency_ms))`.
- `backend/app/services/scalp_engine.py:192` — `jev_target_ms` injectado; `backend/app/services/scalp_service.py:122-135` — `_jev_target_ms()` por `SCALP_JEV_TARGET_MS`.
- `ops/systemd/criptofarol-dev-runtime-worker.service` — `RUN_SCALP_LOOP=1` (DEV); `ops/systemd/criptofarol-prod-runtime-worker.service` — sem a flag (PROD intocado).

## 4. Riscos

- Alterar a **decisão** em vez de só o registro (regressão grave) → decisão 1 + teste de não-regressão por cenário.
- Divergir valor/origem da confiança e rótulo da toxicidade → uma só função para cada par (decisões 3 e 4).
- A faixa de toxicidade ser lida como mudança de decisão → cenário que prova `noul = 0,45` ainda verde no gate, rótulo `indeterminate`.
- Tempo limite 3 s bloquear o loop sequencial até 3 s (vs 1,5 s) → cadência 30 s; bloqueio limitado ao tempo limite; decisão inalterada.
- `last_jev_elapsed_ms = max(cadência, latência)` receber a latência real (até 3 s) numa resposta lenta → com o default de 30 s o `max` é dominado pela cadência (efeito nulo); declarado; teste com o default.
- Mudar prefixo/chave do #1015 quebrar a régua read-only do #1025 → prefixo e `skip_reason` preservados, campos aditivos, régua não alterada.
- Pinar uma versão errada e a chamada falhar no fornecedor → valor capturado da resposta do DEV no Apply, gravado em cada registro; rollback por configuração.
- Trade-off: registros mais gordos e o ciclo enviado passar a registrar → aceite (tecto de 200 MB/truncagem do #1015 limitam; é o dado pedido).

## 5. O que fica em P3 (detalhe de Apply)

- Nomes/forma exacta das chaves dos veredictos na linha (campos `hurdle=`… vs mapa `gates={…}`) e ordem.
- Nome/valor concreto da versão pinada (facto de DEV capturado no Apply) e se mantém override por env.
- Nome da constante/env do tempo limite (3 s) e se o override por argumento de `request_jev` continua.
- Conjunto exacto dos gates de dimensionamento (aditivo se entrarem).
- Rótulo `unknown` sem `noul`; `not_applicable` com o limiar de confiança removido (`SCALP_CONFIDENCE_MIN=none`).
- Como o cliente transporta `model`/origem da confiança até ao serviço (ampliar `JevSignal` vs outro transporte), sem a decisão ler campos novos.
- Como os testes injectam resposta/`urlopen` falsos e verificam os campos novos; actualização das asserções `test_scalp_direcional_jev.py:466,468`.

## 6. Open Questions

Nenhuma. A fronteira veio grelhada; os *como* fecham nas decisões 1–8. O valor concreto da versão pinada é facto de ambiente DEV, resolvido no Apply (P3). A seção de crítica é do pai, depois do crítico.
