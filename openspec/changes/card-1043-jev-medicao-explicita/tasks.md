# Tasks — card-1043-jev-medicao-explicita

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.
> Gate antes de implementar: **Design → Aprovação de Design → Pronto para Dev** — só o `Status=Pronto para Dev` (aprovação humana do Alan) libera `/opsx:apply`; o agente não cruza `Aprovação de Design → Pronto para Dev`.
> Usar as skills do projeto disponíveis no Cursor quando aplicável (`.cursor/skills/`, `.agents/skills/`), com o runbook `covenant-flow`; a crítica de Design é a skill `design-critic`.
> `UI impact: none` nesta entrega: nada de painel/Monitor, rota, HTML, base de dados nova ou PROD. Os tokens do gate estão no `design.md`.

## 1. Estado da medição como resultado estruturado

- [x] 1.1 — Em `scripts/scalp_jev_eval.py`, fazer `load_candles` (`:442-520`) devolver um **resultado de leitura estruturado** com `status` (`medido` | `medição parcial` | `não medido` | `não aplicável`), o **motivo** (causa real) e a **identidade da ligação** usada, em vez de `tuple[CandleSeries, str]` (decisão 1 do `design.md`).
- [x] 1.2 — Derivar o `status` do resultado da leitura, nunca de `if not series` (`:1165`) nem do texto da nota; `não aplicável` só quando não há decisões a juntar (log ausente/vazio).
- [x] 1.3 — Transportar o resultado estruturado de `load_candles` (`:1556-1559`) até `build_report` (`:1037+`) e ao sumário JSON.

## 2. Relatório: medição explícita, sem confundir com amostra

- [x] 2.1 — Acrescentar ao relatório a secção `## Medição do realizado` com o `status`, o `n` de janelas, o `n_priced` e, quando houver lacuna, **quantas janelas ficaram sem preço por cobertura e porquê**.
- [x] 2.2 — Escolher o rótulo do veredicto **primeiro** pelo estado da medição: `não medido` → `**Realizado não medido**`; `medição parcial` → `**Medição parcial**` (com a contagem) e, se aplicável, `**Amostra insuficiente**` em separado; `medido` + amostra curta → `**Amostra insuficiente**`; `não aplicável` → log ausente/vazio. Nenhum caminho imprime `**Amostra insuficiente**` quando `status = não medido` (`:1386-1389`).
- [x] 2.3 — Fecho por regime (`:831-835`): acrescentar o rótulo «medição parcial — X janela(s) sem cobertura» quando a lacuna for de cobertura, **sem** mudar o predicado de fecho (`n_priced < MIN_NON_OVERLAPPING_WINDOWS`, `:88`).
- [x] 2.4 — Contar «janela sem preço por cobertura» (candles não cobrem a janela, `price_at` → `None`, `:419-426`) de forma distinta de «janela sem preço por ausência de entrada» (`realized_for:562-563`); a segunda não entra no contrato de erro.
- [x] 2.5 — `summary["insufficient"]` (`:1112`, `:1254`) mantém o significado de **amostra**; a medição vai em `summary["measurement"]` e não sobrecarrega o campo de amostra.

## 3. Causa real da falha de leitura, sanitizada

- [x] 3.1 — Nas notas de falha (`:456,460,470,506`) incluir a **mensagem real** do erro subjacente (primeira linha, limitada) além de `type(exc).__name__`; na falha de import manter o nome do módulo em falta (decisão 5).
- [x] 3.2 — Sanitizar a mensagem: nunca emitir password nem o DSN completo (o `str(exc)` de `OperationalError` pode conter o DSN).
- [x] 3.3 — Manter `OHLCV desativado (sem DATABASE_URL)` (`:462`) identificável como causa de `não medido`.

## 4. Ligação/utilizador declarado, invocação inalterada

- [x] 4.1 — Declarar no relatório a identidade derivada do ambiente — `user`, `host`, `port`, `dbname` e a **origem** (`settings.database_url` vs `DATABASE_URL`, `backend/app/database.py:61`) — **sem password**, tanto no sucesso como na falha (decisão 4).
- [x] 4.2 — No sucesso, confirmar a identidade da sessão com um `SELECT current_user, inet_server_addr(), inet_server_port(), current_database()` **read-only**, best-effort: a falha da confirmação não muda o `status` nem falha a corrida.
- [x] 4.3 — Não introduzir `--dsn`/`--db-url` nem env de acesso novo; o acesso continua a vir de `app.database` (`DB_URL`), como hoje (`scripts/scalp_jev_eval.py:449-462`; `backend/app/services/ohlcv_storage.py:15,285`).
- [x] 4.4 — (Correção C1 do Code Review) Garantir o bootstrap de `sys.path` (`backend` e raiz) **antes** de qualquer chamada a `_connection_identity()`, via helper idempotente `_ensure_backend_on_path()` chamado em `load_candles` e no início de `main`; sem ele, correr a régua como script degradava a identidade declarada para `unknown` quando o URL vinha só de `settings.database_url` (a decisão 4/Q2 exige a ligação visível no sucesso e na falha).

## 5. Saída em erro da corrida que não mediu

- [x] 5.1 — `main()` devolve **`3`** quando `status = não medido` e há decisões; `0` para `medido`, `medição parcial` e `não aplicável`; `2` continua reservado ao `argparse` (decisão 3).
- [x] 5.2 — Garantir que o relatório (stdout), o `--json` e o `--out` (`:1561-1568`) são emitidos **antes** do retorno, e que `raise SystemExit(main())` (`:1574`) propaga o código não-zero.
- [x] 5.3 — Expor no sumário JSON `measurement` (`status`, `reason`, `connection`, `windows_without_price`, `exit_code`) para o consumidor automático (operador à mão e recolha de evidência por automação).

## 6. Testes, read-only, DEV-only e validação

- [x] 6.1 — Testes do estado de medição: leitura completa → `medido`; leitura falhada/sem cobertura com decisões → `não medido`; lacuna de cobertura → `medição parcial` com contagem; log ausente/vazio → `não aplicável`.
- [x] 6.2 — Testes do contrato de saída: `não medido` → exit não-zero com relatório emitido; `medido`/`medição parcial`/`não aplicável` → exit `0`.
- [x] 6.3 — Testes do veredicto: `não medido` nunca imprime `**Amostra insuficiente**`; `medido` + amostra curta continua a imprimir; `medição parcial` + amostra curta declara os dois em separado.
- [x] 6.4 — Testes da causa real e da declaração da ligação: nota com mensagem real (não só a classe) sanitizada; `user`/`host`/`port`/`dbname` + origem declarados no sucesso e na falha, **sem** password/DSN.
- [x] 6.5 — Testes da invocação inalterada e da não-regressão: sem argumento novo de acesso; limiar de confiança, política por regime, geometria alvo/stop, horizonte, `MIN_NON_OVERLAPPING_WINDOWS`/`MIN_BUCKET_TRADES` e `sample_sufficient` inalterados; teste de read-only existente (`test_the_instrument_is_read_only`) continua a cobrir o ficheiro.
- [x] 6.6 — Só log/relatório e DEV-only: sem `backend/app/**` de produto, sem `frontend/**`, sem rota, sem HTML, sem painel/Monitor, sem base de dados nova, sem exportação/Drive, sem backtest; PROD é T16. Sem segredos em artefactos, registos ou evidência.
- [x] 6.7 — `openspec validate card-1043-jev-medicao-explicita --strict` verde no worktree.
- [x] 6.8 — (Correção C2 do Code Review) Testes de regressão do bootstrap da ligação: a derivação **real** (`settings.database_url` apenas, sem `DATABASE_URL` exportado e sem `PYTHONPATH`) declara `source`/`user`/`host`/`port`/`dbname` no relatório na falha de leitura e no caminho de `main` com log ausente, sem password/DSN; e a identidade derivada chega ao relatório no sucesso e na falha (`test_main_with_a_missing_log_declares_the_derived_connection`, `test_load_candles_carries_the_derived_connection_when_the_read_fails`, `test_the_real_derivation_is_declared_in_the_report_on_success_and_failure`).

## 7. Gate de Design (não implementar aqui)

- [x] 7.1 — Confirmar `Status=Design` → crítica do `design-critic` → `Aprovação de Design`; **não** avançar para `Pronto para Dev` (T7 é do Alan) nem editar código de produto neste filho.
- [x] 7.2 — Depois de `Pronto para Dev`: `/opsx:apply` com o contrato do `design.md` (secção de medição, veredicto sem confusão, código de saída não-zero, causa real sanitizada, ligação/utilizador declarado).
- [x] 7.3 — Declarar na evidência do Apply que a corrida usada para evidência **mediu** o realizado (código de saída `0` e `status` da medição), nunca uma corrida degradada.
