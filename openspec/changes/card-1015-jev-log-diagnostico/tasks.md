# Tasks — card-1015-jev-log-diagnostico

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Log da chamada Jev (entrada/retorno)

- [x] 1.1 — Entrada: em `request_jev`, registar o payload enviado (`state`/`questions`: touch, window, account, resting) no ponto onde o corpo SystemOne é montado. Conta só resumida (`has_position`, `has_balance`); nunca `inventory_btc`, `t`, `remaining_to_t` ou saldos em valores exactos. Nunca a chave TypeSafe nem o header `Authorization`.
- [x] 1.2 — Retorno: registar side, `expected_move_bp`/score, `book_toxic`, confiança, latência e status HTTP (`resp.status` no sucesso, `exc.code` no erro). Em erro, corpo do erro resumido (truncado) e passado pelo `_redact` antes de escrever.
- [x] 1.3 — Entrada e retorno legíveis numa chamada completa (sucesso), correlacionáveis por instante/id.

## 2. Recusa do ciclo (`skip_reason`)

- [x] 2.1 — Um único helper de registo de recusa chamado em todos os caminhos de `tick_user` que fecham o ciclo sem ordem, com o token `skip_reason` tal como nasce (`hold`, `low_confidence`, `hurdle`, `toxic_book`, `jev_late`, `jev_target`, `t_zero`, `ceiling_reduce_only`, `window_empty`, `switch_off`, `halted`, `no_book` «livro indisponível», etc.), pré- e pós-chamada.
- [x] 2.2 — O painel e `/api/scalp/status` não recebem o motivo da última recusa — só o log.

## 3. Nível e ficheiro único com tecto (truncagem de cauda)

- [x] 3.1 — Logger dedicado do diagnóstico com nível configurável por env (entrada/retorno em INFO, erros em WARNING); default INFO no DEV.
- [x] 3.2 — Ficheiro de log **único** com tecto de **200 MB (209 715 200 bytes)**: ao encher, o registo mais antigo cai no próprio ficheiro (truncagem de cauda em fronteira de linha, descartando a linha parcial do início); sem prazo fixo (nada de rotação por tempo, nada de `RotatingFileHandler`/`backupCount`/backups `.1`); o ficheiro não cresce sem tecto.

## 4. Segredos e conta

- [x] 4.1 — Nenhum segredo (chave, token) em logs, painel ou registo — incluindo corpos de erro ecoados; teste com a chave injectada no corpo de erro prova o `<redacted>`.
- [x] 4.2 — Conta no log sempre resumida; teste falha se o registo contiver saldo ou posição em valores exactos.

## 5. Inalterados (decisões de trading)

- [x] 5.1 — Payload SystemOne e código de decisão inalterados: mesmo hurdle (`expected_move_bp > 2 × fee_bp + spread_bp`), mesma cadência de pergunta (~1 s / `JEV_TARGET_MS`), mesmo fail-closed de 1,5 s (`JEV_LATE_MS`), mesmo fail-closed de 500 ms (`age_ms`), mesmos alvo 35 bp / stop −28 bp. Testes existentes do scalp verdes sem mudar expectativas.

## 6. DEV e evidência

- [x] 6.1 — Registo activo só no DEV (runtime-worker DEV com `RUN_SCALP_LOOP=1`); o unit PROD não ganha flag nem handler.
- [x] 6.2 — Evidência DEV — **resequenciada para pós-T14 pelo dono, mantendo a evidência** (o critério do card não muda; muda só a altura em que a evidência é recolhida). (i) O registo está armado no runtime-worker DEV (`RUN_SCALP_LOOP=1`). (ii) A evidência real — log do runtime-worker DEV com várias chamadas (sucesso + uma recusa com `skip_reason`) — é recolhida **após a integração em `develop` (T14: squash + restart DEV)** e anexada ao card para a homologação (T15). (iii) Prova interina já registada: reprodução local do mesmo caminho de código (2 chamadas completas + 1 recusa `switch_off`, sem segredos nem valores exactos).

## 7. Testes e verificação

- [x] 7.1 — Testes unitários: chamada completa (entrada + retorno) no log; erro HTTP com corpo resumido redigido; recusa com `skip_reason` em ciclo sem ordem (pré- e pós-chamada); nível configurável; tecto forçado num ficheiro temporário com tecto minúsculo prova que o registo mais antigo caiu, que o ficheiro ficou dentro do tecto e que a primeira linha do ficheiro truncado continua legível (fronteira de linha).
- [x] 7.2 — `openspec validate` desta change verde.
- [x] 7.3 — Diff sem `frontend/**`, sem mudar `build_jev_payload`/`_systemone_payload`/`decide_cycle`/constantes de trading, sem base de dados nova, sem rota/UI nova, sem exportação/Drive.
