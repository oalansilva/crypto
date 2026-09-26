# Tasks — card-1028-jev-veredictos-origem

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.
> Usar as skills do projeto disponíveis no Cursor quando aplicável (`.cursor/skills/`, `.agents/skills/`), com o runbook `covenant-flow`.
> `UI impact: none` nesta entrega: nada de painel/Monitor, rota, HTML ou base de dados. Os tokens do gate estão no `design.md`.

## 1. Veredicto de todos os gates de entrada no mesmo registro

- [x] 1.1 — Em `backend/app/services/scalp_engine.py::decide_cycle`, sem alterar a decisão nem a ordem dos gates, calcular o veredicto `pass`/`fail`/`not_applicable` de cada gate alimentado pela resposta (`jev_late`, `hold`, `low_confidence`, `hurdle`, `regime`, `toxic_book`) e devolvê-lo no `CycleIntent`; o intent devolvido (primeiro `skip_reason`, `send`, `cancel_resting`, etc.) fica **idêntico** ao de hoje.
- [x] 1.2 — Em `backend/app/services/scalp_service.py::tick_user`, no fecho único do ciclo, escrever **um** registro por ciclo com resposta do modelo: `scalp cycle refused user=... skip_reason=<primeiro token>` (recusado) ou `scalp cycle sent user=... skip_reason=none` (enviado), com o veredicto de cada gate no **mesmo** registro, mesmo quando um gate anterior já recusou.
- [x] 1.3 — Manter o prefixo `scalp cycle refused` e a chave `skip_reason` do #1015 (a régua read-only `scripts/scalp_jev_eval.py` lê-os e o `KVRe` tolera campos adicionais); não alterar `scripts/scalp_jev_eval.py`.

## 2. Origem da confiança

- [x] 2.1 — Em `backend/app/services/scalp_jev.py`, `_side_confidence` devolve `(valor, origem)` com origem em `reply_field` / `choice_probability` / `none`; o valor devolvido é o mesmo que a decisão consome (o campo de confiança da resposta quando existe; só quando não existe, a probabilidade da opção escolhida).
- [x] 2.2 — A origem da confiança entra no registro do ciclo e no registro de retorno da chamada, junto do valor.

## 3. Versão do modelo

- [x] 3.1 — A chamada passa a pedir um identificador de **versão fixa** em vez do apelido `_JEV_MODEL = "jev-latest"`; o pedido nunca envia o apelido e não cai no apelido quando a versão pinada não está configurada.
- [x] 3.2 — Gravar a **versão que respondeu** (campo `model` da resposta) em todo registro, independentemente do opt-in `SCALP_JEV_RAW_PAYLOAD`; sem identificador na resposta → `unknown`.
- [x] 3.3 — Levar a versão que respondeu (e a origem da confiança) do cliente até ao registro do ciclo, sem a decisão passar a ler campos novos.
- [x] 3.4 — Valor concreto da versão pinada = facto de ambiente DEV capturado no Apply a partir do `model` que a resposta reportar (P3); testes usam o valor configurado/constante.

## 4. Toxicidade com dois cortes e faixa de incerteza

- [x] 4.1 — Em `backend/app/services/scalp_jev.py`, a leitura de toxicidade ganha o rótulo de três estados: `not_toxic` (noul < 0,4), `indeterminate` (0,4 ≤ noul ≤ 0,6), `toxic` (noul > 0,6) e `unknown` sem valor.
- [x] 4.2 — A decisão **não muda**: o booleano consumido por `decide_cycle` continua `noul >= 0,5`; o registro mostra o rótulo **e** o booleano da decisão, para a leitura indeterminada não ser confundida com mudança de comportamento.

## 5. Tempo limite da chamada (3 s) com a recusa em 1,5 s

- [x] 5.1 — Novo valor de contrato **3 s** (constante pura ao lado de `JEV_LATE_MS`, nome = P3) usado como tempo limite por omissão de `request_jev`; `JEV_LATE_MS = 1500` continua a alimentar o gate `jev_late`.
- [x] 5.2 — Uma resposta entre 1,5 s e 3 s passa a ser recebida, mapeada e registrada, e o ciclo continua recusado por `jev_late`; nenhuma decisão muda.

## 6. Não-regressão (decisão inalterada)

- [x] 6.1 — Teste de não-regressão por cenário: mesmo input → mesma decisão (`send`/primeiro `skip_reason`) cobrindo recusa por confiança, hurdle, regime, tóxico, atraso e o ciclo verde; os campos novos do registro são efeito lateral.
- [x] 6.2 — Actualizar as duas asserções de contrato de configuração que fixam o comportamento antigo (`backend/tests/unit/test_scalp_direcional_jev.py:466` timeout `== JEV_LATE_MS/1000` e `:468` `model == "jev-latest"`) para o contrato novo (3 s e versão fixa) — é configuração, não decisão.
- [x] 6.3 — Teste que prova que um `noul` dentro da faixa (ex.: 0,45) continua a decidir pelo corte de 0,5 (não tóxico no gate) e que o registro marca `indeterminate`.

## 7. Só DEV, só log

- [x] 7.1 — Sem `frontend/**`, sem rota, sem HTML, sem painel/Monitor, sem `/api/scalp/status`, sem base de dados nova, sem exportação/Drive; destino é o ficheiro único de diagnóstico do #1015 (tecto e truncagem de cauda inalterados), DEV-only (`RUN_SCALP_LOOP=1`; o unit PROD não ganha nada).
- [x] 7.2 — `openspec validate card-1028-jev-veredictos-origem --strict` verde.
- [x] 7.3 — Payload SystemOne e demais decisões inalterados: mesma cadência (`JEV_TARGET_MS`), mesmo hurdle, mesmo regime, mesmo alvo/stop, mesmo fail-closed de frescura; testes existentes verdes (excepto as asserções de configuração de 6.2).
