Título: Régua Jev: falha de leitura do OHLCV fora do root vira amostra insuficiente em silêncio

Achado da verificação de homologação do #1030 (25/09).

## Problema

A régua do scalp Jev (`scripts/scalp_jev_eval.py`) só consegue ler o lado realizado quando corre com o utilizador dos serviços DEV (`root`, ligação por socket com peer auth). Corrida como outro utilizador, a leitura do OHLCV falha e a régua degrada em silêncio para **"0 com preço"** — um número que se lê como *amostra insuficiente* quando é **falha de medição**. Quem opera o instrumento conclui o contrário do que os dados dizem.

## História

Como operador do scalp Jev, quero que a régua distinga "não consegui medir" de "não há amostra suficiente", para não decidir sobre um relatório cuja medição falhou — e para que a evidência de um card nunca seja colhida de uma medição falhada.

## Entra

- A régua passa a declarar a **falha de leitura** do OHLCV como falha, distinta da insuficiência de amostra, com o motivo (ex.: peer auth, import, sem candles que cubram a janela).
- O relatório não apresenta como "amostra insuficiente" o caso em que o lado realizado não foi medido.
- A causa (utilizador/ligação) fica visível no relatório, não só no texto da linha de OHLCV.
- O caminho de execução passa a ser declarado (qual utilizador/DSN a régua pressupõe), ou a régua aceita o DSN por argumento.

Critérios observáveis:

- Corrida fora do utilizador dos serviços, o relatório diz explicitamente que **não mediu** o realizado, e não o apresenta como insuficiência de amostra.
- Corrida com acesso válido, o relatório mostra a contagem de janelas com preço (hoje: 57 de 74).
- Nenhum caminho do relatório confunde as duas situações.

### Decisões fechadas (grelha 25/09)

- Quando a corrida não conseguiu medir o realizado, a régua **termina em erro** (corrida falhada) e, ainda assim, emite o relatório rotulado «realizado não medido». Uma corrida que não mediu nunca termina como sucesso.
- A régua continua a obter o acesso ao lado realizado pelo **ambiente** (a invocação não muda) e passa a **declarar no relatório qual ligação/utilizador usou**, tanto quando mede como quando não mede.
- O relatório passa a distinguir **«medição parcial»** de **«amostra insuficiente»**: quando a lacuna é de cobertura, diz quantas janelas ficaram sem preço e porquê, em vez de as apresentar como falta de amostra.

Critérios observáveis das decisões:

- Corrida sem medição do realizado: termina em erro, visível a quem a invoca à mão ou por automação, e o relatório emitido diz explicitamente que não mediu.
- Relatório de corrida com acesso válido: identifica a ligação/utilizador usada; havendo lacuna de cobertura, rotula-a como medição parcial com a contagem de janelas sem preço.

## Não entra

- Mudar o limiar de confiança, a política por regime, a geometria alvo/stop ou o horizonte de espera.
- Reabrir o #1030 (o mecanismo está entregue) ou o #1025.
- Expor no painel/Monitor. Produção.

## Evidência (25/09, DEV)

- Como `ubuntu`: `OHLCV indisponível (import: ModuleNotFoundError)` com o python do sistema; `OperationalError` no socket com o venv — `FATAL: Peer authentication failed for user "root"`. Relatório: `74 janelas / 0 com preço`.
- Como `root` (utilizador dos serviços): `OHLCV BTC/USDT 15m: 194 candles`. Relatório: `74 janelas / 57 com preço`.
- A evidência de Apply do #1030 registou "30 janelas, 0 com preço → amostra insuficiente", colhida no caminho degradado.

## Why

A régua do scalp Jev (`scripts/scalp_jev_eval.py`) trata hoje a **falha de leitura** do OHLCV como se fosse **falta de amostra**: com o lado realizado indisponível, `load_candles` devolve uma `CandleSeries` vazia e um texto solto (`scripts/scalp_jev_eval.py:456,460,462,470,494-497,506,508`), e qualquer `reason` faz o bloco de veredicto imprimir `**Amostra insuficiente**` (`scripts/scalp_jev_eval.py:1165-1166,1386`). O resultado observado é `74 janelas / 0 com preço`, lido por quem opera como insuficiência de amostra quando é medição falhada — e a evidência de um card pode ser colhida nesse caminho degradado. Este card torna o resultado da medição um estado explícito e verificável do relatório, declara a ligação/utilizador usado e faz a corrida que não mediu terminar em erro.

## What Changes

- `load_candles` (`scripts/scalp_jev_eval.py:442-520`) passa a devolver um **resultado de leitura estruturado** com o estado da medição (`medido` | `não medido` | `medição parcial`), o motivo real (não só `type(exc).__name__`) e a identidade da ligação/utilizador usada, em vez de um `tuple[CandleSeries, str]` cujo estado tem de ser inferido do texto.
- O relatório passa a ter uma secção de **medição do realizado** que declara o estado, a contagem de janelas sem preço e o motivo; o veredicto deixa de imprimir `**Amostra insuficiente**` quando o realizado **não foi medido** — passa a imprimir `**Realizado não medido**` (ou `**Medição parcial**`), e a insuficiência de amostra é declarada em separado.
- A corrida que **não mediu** o realizado termina com **código de saída não-zero**, continuando a emitir o relatório (stdout, `--out` e `--json`) antes de sair; a causa deixa de ser apenas o nome da classe da exceção e passa a incluir a mensagem real, sanitizada (sem segredos).
- O acesso ao lado realizado continua a vir **do ambiente** (`DATABASE_URL`/settings via `app.database`, `scripts/scalp_jev_eval.py:50`), sem alterar a invocação; o relatório passa a **declarar a ligação/utilizador** usado, tanto no sucesso como na falha.
- A lacuna de **cobertura** passa a ser rotulada como **medição parcial** (quantas janelas ficaram sem preço e porquê), incluindo no fecho por regime, em vez de ser apresentada como falta de amostra.
- Sem tocar no limiar de confiança, na política por regime, na geometria alvo/stop ou no horizonte de espera; sem reabrir #1030/#1025; sem painel/Monitor; sem PROD.

## Capabilities

### New Capabilities

- `scalp-jev-realized-measurement`: a régua declara o resultado da medição do lado realizado (`medido` | `não medido` | `medição parcial`) com o motivo real, distingue-o da insuficiência de amostra em todos os caminhos do relatório e faz a corrida que não mediu terminar em erro, emitindo ainda assim o relatório.
- `scalp-jev-ohlcv-access`: o acesso ao OHLCV continua a vir do ambiente (a invocação não muda) e a régua declara no relatório a ligação/utilizador usada, no sucesso e na falha, com a causa real visível e sem expor segredos.

### Modified Capabilities

<!-- Nenhuma capability de `openspec/specs/` tem requisitos alterados: a régua do #1030 ainda é um change em voo (`card-1030-jev-limiar-retorno-liquido`, não arquivado), pelo que esta entrega introduz requisitos novos e não reescreve requisitos existentes. -->

## Impact

- `scripts/scalp_jev_eval.py` — instrumento read-only: `load_candles`, `build_report`, o bloco de veredicto, o sumário `--json` e o contrato de saída de `main()`.
- `backend/tests/unit/test_scalp_jev_eval_ruler.py` — testes existentes da régua e do gate de read-only (novos casos para medição não medida, medição parcial, causa real, declaração da ligação e código de saída).
- Consumidores do código de saída: corrida manual do operador e a recolha de evidência por automação (Apply/QA) — uma medição falhada deixa de ser aceite como sucesso.
- Sem `backend/app/**`, sem `frontend/**`, sem rota, sem HTML, sem painel/Monitor, sem base de dados nova, sem PROD (T16).
