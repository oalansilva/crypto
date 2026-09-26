# Design — card-1043-jev-medicao-explicita

## Context

Card **#1043**, `Status=Design`, cliente Cursor Agent, **SEM-TELA**. Briefing = issue grelhado (`## Problema`, `## História`, `## Entra` com critérios observáveis e `### Decisões fechadas (grelha 25/09)`, `## Não entra`, `## Evidência (25/09, DEV)`), copiado **verbatim** em `proposal.md`; sem reentrevista. Instrumento: a régua read-only do scalp Jev. Sem rota, sem protótipo, sem painel/Monitor, sem base de dados nova, sem PROD.

**Estado do instrumento no worktree (lido, sem alterar nada):** a régua do #1025/#1030 já existe e é read-only; este card muda o **resultado da medição do realizado** no seu relatório.

Factos confirmados no worktree (path:linha):

- **Não existe caminho de erro não-zero.** `scripts/scalp_jev_eval.py:1570` — `main()` termina **sempre** com `return 0`; `:1574` — `raise SystemExit(main())`. Qualquer medição falhada sai hoje com código `0` (o cerne de Q1).
- **A falha de leitura só produz texto solto, e o veredicto colapsa tudo em "Amostra insuficiente".** `scripts/scalp_jev_eval.py:442-520` — `load_candles` devolve `tuple[CandleSeries, str]`; as notas carregam apenas `type(exc).__name__`: `:456` (`OHLCV indisponível (import: ...)`), `:460` (`(repo: ...)`), `:470` e `:506` (`OHLCV falhou na leitura (...)`); `:462` (`OHLCV desativado (sem DATABASE_URL)`); `:494-497` (`sem candles que cubram a janela ...`); `:508` (`OHLCV sem candles ...`); `:513-519` acrescenta a nota de **cobertura parcial** (o último candle não chega ao fim).
- **`if not series` vira um `reason` genérico.** `scripts/scalp_jev_eval.py:1165-1166` — `if not series: reasons.append(f"realizado indisponível: {ohlcv_note}")`; a lista `reasons` (`:1160`, `:1167-1181`) alimenta o bloco de veredicto em `:1386-1389`, que imprime `**Amostra insuficiente**` para **qualquer** `reason`. O texto distingue a causa; o **veredicto** não.
- **A insuficiência de amostra é outro eixo.** `scripts/scalp_jev_eval.py:1170-1172` (`len(windows) < 30`), `:1178-1181` (`n_priced < 30`), `:1233-1236` (`sample_sufficient = len(windows) >= 30 and stats_all["n_priced"] >= 30`); mínimos em `:88-89` (`MIN_NON_OVERLAPPING_WINDOWS = 30`, `MIN_BUCKET_TRADES = 20`). O fecho por regime usa o mesmo mínimo: `:831-835` (`elif stats["n_priced"] < MIN_NON_OVERLAPPING_WINDOWS`).
- **A contagem de janelas com preço já é visível.** `scripts/scalp_jev_eval.py:895-898` mostra `**{stats['n_priced']} com preço**` na linha de amostra (o «57 de 74» já aparece); a decisão do card é o **rótulo do veredicto**, não a contagem.
- **O acesso ao OHLCV que a régua usa vem do ambiente, por import de módulo.** `scripts/scalp_jev_eval.py:50` (docstring: `DATABASE_URL` do ambiente), `:449-462` (`load_candles` faz `sys.path` e importa `app.services.ohlcv_storage.MarketOhlcvRepository`). `backend/app/database.py:54-72` — `resolve_db_url()` lê `settings.database_url` ou `DATABASE_URL` (`:61`) e levanta se ausente/inválido (`:64`, `:69`); `:72` — `DB_URL = resolve_db_url()` corre **no import**. `backend/app/services/ohlcv_storage.py:15` importa `DB_URL, engine`; `:283-289` (`MarketOhlcvRepository`, `self._enabled = bool(DB_URL)`); `:413-420` (`read_recent_candles`, `with engine.begin() as conn`). A régua **não** tem parâmetro de acesso: a ligação é sempre a do módulo `app.database`.
- **O sumário JSON mistura os dois eixos.** `scripts/scalp_jev_eval.py:1112` (`summary["insufficient"] = True` inicial), `:1254` (`summary["insufficient"] = bool(reasons)`), `:1108-1110` (`summary["ohlcv"]`, `summary["ohlcv_candles"]`). Um consumidor do `--json` não consegue hoje distinguir medição falhada de amostra pequena.
- **A escrita do relatório precede o retorno.** `scripts/scalp_jev_eval.py:1561-1568` — `print(report)`, `print` do JSON quando `args.json`, e `out_path.write_text(...)` quando `args.out`; só depois `:1570 return 0`.

UI impact: none
live_route: N/A régua read-only de avaliação no backend/harness do scalp Jev; não há tela de produto
surface: new

Sem rota autenticada, sem landing, sem HTML. Nunca emprestar `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, `landing`. Prototype **N/A** — não há superfície visual neste card (instrumento read-only de backend/harness); não há página viva a clonar nem HTML de protótipo. Impeccable **N/A** — não há UI nem copy visível a polir; os gates de Design e de Aprovação de Design continuam a valer (esta entrega é OpenSpec + relatório, e o pai publica a crítica). Nota de leitura do gate: `surface: new` refere-se à **nova capability de medição explícita** (estado da medição do realizado no relatório + contrato de saída), **não** a uma superfície de tela nova.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Vocabulário

- **Medição do realizado:** o acto de juntar a cada janela não sobreposta o preço de fecho a 900 s lido do OHLCV já existente (`realized_for`, `scripts/scalp_jev_eval.py:561-577`; `CandleSeries.price_at`, `:414-426`).
- **Estado da medição (eixo próprio deste card):**
  - **`medido`** — todas as janelas a medir obtiveram preço.
  - **`medição parcial`** — algumas janelas obtiveram preço e outras ficaram sem ele por **lacuna de cobertura** do OHLCV (o último candle não chega ao fim da janela, `:513-519`; `price_at` devolve `None`, `:419-426`).
  - **`não medido`** — o lado realizado era **necessário** (há decisões a juntar) e **nenhuma** janela obteve preço: falha de import/repo/leitura (`:456,460,470,506`), OHLCV desativado (`:462`) ou ausência total de candles que cubram a janela (`:494-497,508`).
  - **`não aplicável`** — não há decisões (log ausente/vazio): não há lado realizado a medir. Distinto de `não medido` de propósito (decisão 3).
- **Insuficiência de amostra (eixo pré-existente, do #1030):** `len(windows) < MIN_NON_OVERLAPPING_WINDOWS` (30) ou `n_priced < 30` (`:1170-1181`, `:1233-1236`). Continua a significar «a amostra não chega para propor valores»; **não** significa «não consegui medir».
- **Ligação/utilizador (identidade de acesso):** o par utilizador+servidor+porta+base que a régua usa para ler o OHLCV, derivado do ambiente (`app.database.DB_URL`), **sem password**. Nunca confundir com a password/DSN completo.
- **Causa real:** a mensagem do erro subjacente (ex.: `FATAL: Peer authentication failed for user "root"`, `No module named 'app'`), distinta de `type(exc).__name__`.
- **Corrida que não mediu:** corrida com `status = não medido`. É a única que termina em erro (decisão 3); `não aplicável` e `medição parcial` não.

## Goals / Non-Goals

**Goals:**

- Tornar o **estado da medição** do realizado um resultado explícito e verificável do relatório (`medido` | `medição parcial` | `não medido` | `não aplicável`), com o motivo real.
- Garantir que **nenhum caminho do relatório** apresenta «não consegui medir» como «amostra insuficiente», incluindo o veredicto e o fecho por regime.
- Fazer a corrida que **não mediu** terminar com **código de saída não-zero**, continuando a emitir o relatório rotulado «realizado não medido».
- Declarar no relatório **qual ligação/utilizador** a régua usou, no sucesso e na falha, sem mudar a invocação (acesso pelo ambiente).
- Distinguir **«medição parcial»** de **«amostra insuficiente»**, com a contagem de janelas sem preço e o motivo.
- Manter o instrumento **read-only**, sem novas arestas de escrita, e sem tocar nos valores do #1030 (limiar, política por regime, geometria, horizonte).

**Non-Goals:**

- Mudar o limiar de confiança, a política por regime, a geometria alvo/stop ou o horizonte de espera (decisões fechadas do #1030).
- Reabrir #1030 ou #1025; mudar a regra de amostra suficiente (`sample_sufficient`).
- Acrescentar `--dsn`/`--db-url` à invocação (Q2 fechada: o acesso continua pelo ambiente e a invocação não muda).
- Expor no painel/Monitor, criar rota/HTML, base de dados nova, dashboard, exportação/Drive ou backtest.
- Escrever estado de medição em produto/DB; segredos (password/DSN completo) em qualquer artefacto ou registo.
- PROD (T16).

## Decisions

1. **O estado da medição é um resultado estruturado, não um texto a inferir.** `load_candles` (`:442-520`) passa a devolver o par `(CandleSeries, OhlcvRead)`, onde `OhlcvRead` carrega `status` (`medido`/`parcial`/`não medido`/`não aplicável`), o **motivo** (causa real), a **identidade da ligação** usada e a contagem de janelas sem cobertura; o `main` (`:1546-1559`) e o `build_report` (`:1037+`) passam a consumir esse estado em vez de `if not series` (`:1165`).
   *Alternativa rejeitada* — **manter `tuple[CandleSeries, str]` e inferir o estado do texto da nota**: é a fonte actual da confusão (as notas são frases livres, `:456-519`; o veredicto decide por `bool(reasons)`), e qualquer mudança de wording quebraria a classificação em silêncio.
   *Alternativa rejeitada* — **um único booleano `measured`**: não exprime `medição parcial` (Q3) nem distingue `não aplicável` de `não medido`.

2. **Dois eixos independentes, nunca colapsados: medição e amostra.** O relatório declara a **medição** (secção própria, `## Medição do realizado`) e, em separado, a **amostra** (`## Declaração / gate`). O rótulo do veredicto é escolhido **primeiro** pelo estado da medição: `não medido` → `**Realizado não medido**`; `parcial` → `**Medição parcial**` (com «X de N janelas sem preço» e o porquê) e, quando aplicável, também `**Amostra insuficiente**`; `medido` com `reasons` → `**Amostra insuficiente**`; `não aplicável` → `**Log ausente/vazio**`/insuficiência de amostra sem chamadas.
   *Alternativa rejeitada* — **deixar `if reasons:` imprimir `**Amostra insuficiente**` para qualquer motivo** (`:1386`): é literalmente o defeito do card («o texto distingue, o veredicto não»).
   *Alternativa rejeitada* — **gravar no `reason` a palavra «medição» e deixar o rótulo como está**: mantém a conclusão errada («amostra insuficiente») e não é verificável por um consumidor automático.

3. **Q1 — a corrida que não mediu termina em erro, e ainda assim emite o relatório.** Quando `status = não medido` e há decisões (o lado realizado era necessário), `main()` devolve **`3`** (código não-zero, distinto do `2` do `argparse`) e `raise SystemExit(main())` (`:1574`) propaga-o. O relatório é integralmente emitido **antes** de retornar: `print(report)` (`:1561`), `--json` do sumário (`:1562-1565`) e `--out` (`:1566-1568`) já executaram. Consumidores: o operador que invoca à mão e a automação de evidência (Apply/QA) que lê o código de saída do processo.
   *Alternativa rejeitada* — **`sys.exit()`/`raise` dentro de `build_report` ou antes de escrever o relatório**: suprimiria o relatório rotulado «realizado não medido» que a decisão fechada exige («a régua termina em erro **e** emite o relatório»).
   *Alternativa rejeitada* — **manter `return 0` com um aviso** (`:1570`): é o estado que produz evidência colhida de medição falhada.
   *Alternativa rejeitada* — **`não medido` sempre que falte qualquer medição, incluindo log ausente/vazio**: falharia uma corrida cujo log está simplesmente vazio — não houve lado realizado a medir; por isso `não aplicável` fica fora do contrato de erro (vocabulário).

4. **Q2 — acesso pelo ambiente, invocação inalterada, ligação declarada no sucesso e na falha.** A régua continua a obter a ligação pelo módulo `app.database` (`DB_URL`, `backend/app/database.py:72`; consumido por `ohlcv_storage.py:15,285`), **sem** novo argumento. O relatório passa a declarar a **identidade** derivada do ambiente — `user`, `host`, `port`, `dbname` e a **origem** (`settings.database_url` vs `DATABASE_URL`) — **sem password**; na falha declara a identidade pretendida **e** a causa real. No sucesso pode confirmar a identidade da sessão com um `SELECT current_user, inet_server_addr(), inet_server_port(), current_database()` **read-only** (best-effort).
   *Alternativa rejeitada* — **acrescentar `--dsn`/`--db-url`**: o próprio Entra admite «ou a régua aceita o DSN por argumento», mas a decisão fechada de Q2 escolheu o ambiente e «a invocação não muda»; um argumento novo muda o contrato de chamada e cria dois caminhos de acesso.
   *Alternativa rejeitada* — **exigir/pressupor o utilizador `root`**: perpetua a fragilidade descrita no Problema e não é declarado ao operador.
   *Alternativa rejeitada* — **imprimir o DSN cru**: exporia a password em relatório/stdout/`--out` (o `str(exc)` de `OperationalError` também pode conter o DSN) — proibido.

5. **A causa real fica visível, sanitizada.** As notas de falha passam a incluir a mensagem do erro subjacente (primeira linha, limitada, com DSN/password sanitizados) **além** de `type(exc).__name__`; na falha de import mantém-se o nome do módulo em falta. Isto substitui as notas `:456,460,470,506` que expõem só a classe.
   *Alternativa rejeitada* — **manter só `type(exc).__name__`**: o `OperationalError` não diz ao operador que a causa é `Peer authentication failed for user "root"`; foi exactamente o que obrigou a investigação manual na evidência do #1030.
   *Alternativa rejeitada* — **colar o traceback inteiro**: ruído e risco de segredos no relatório.

6. **Q3 — «medição parcial» distinta de «amostra insuficiente», inclusive no fecho por regime.** A secção de medição mostra `n` janelas, `n_priced`, **janelas sem preço por cobertura** e o motivo; o fecho por regime (`:831-835`) passa a declarar, quando for o caso, «medição parcial — X janela(s) sem cobertura», em vez de deixar ler-se apenas «população elegível com preço < mínimo». A insuficiência de amostra continua a ser declarada quando `n_priced < MIN_NON_OVERLAPPING_WINDOWS` (regra do #1030, **intacta**).
   *Alternativa rejeitada* — **substituir o fecho por `n_priced < 30` pelo estado da medição**: mudaria a regra de amostra do #1030 (fora do `## Não entra`).
   *Alternativa rejeitada* — **manter tudo como `reason` textual** (a nota de cobertura parcial já existe em `:513-519`): o rótulo continua a ser «Amostra insuficiente», logo a decisão Q3 não fica cumprida.

7. **O sumário `--json` expõe a medição como campo próprio e não sobrecarrega `insufficient`.** Entra `summary["measurement"] = {status, reason, connection:{user,host,port,dbname,source}, windows_without_price, exit_code}`; `summary["insufficient"]` (`:1112`, `:1254`) mantém o significado de **amostra** (não de medição), para que um consumidor automático não leia uma falha de medição como falta de amostra.
   *Alternativa rejeitada* — **continuar a derivar `insufficient` de `bool(reasons)`**: mistura os dois eixos e é a raiz do consumo errado descrito no Problema.

8. **Read-only preservado e sem novas arestas de escrita.** Nenhuma escrita em produto, estado do scalp ou base de dados; a confirmação de identidade é um `SELECT`; sem novo argumento/env de acesso; o teste existente de read-only mantém-se e cobre o ficheiro.
   *Alternativa rejeitada* — **persistir o estado de medição** (tabela/ficheiro de estado): daria à régua uma aresta de escrita que hoje não tem e não é pedida pelo card.
   *Alternativa rejeitada* — **configurar o acesso por env novo (`SCALP_*`)**: abre um segundo caminho de acesso e desvia do Problema (o acesso válido já existe; o que falta é declará-lo e não o mascarar).

## Risks / Trade-offs

- [Risco] A mudança de tipo de retorno de `load_candles` quebrar chamadores. → Mitigação: o único chamador é `main` (`:1556-1559`); `scalp_jev_window_ab.py` usa `build_report`, não `load_candles`; os testes atualizam-se no Apply; a forma exacta do resultado é P3.
- [Risco] «Medição parcial» disparada por janelas sem preço que não são lacuna de cobertura (ex.: ciclo sem `entry_mid`, `realized_for:562-563`). → Mitigação: conta-se como «sem preço por cobertura» apenas a janela cuja lacuna vem dos candles armazenados (`price_at` devolve `None` com `series` não vazia); ausência de entrada é motivo distinto (P3 declará-lo no relatório, sem entrar no contrato de erro).
- [Risco] Tratar «medição parcial» como falha e fazer falhar toda a corrida com qualquer lacuna. → Mitigação: decisão 3 — erro **só** para `não medido` (zero janelas com preço); parcial é declarada e sai `0`.
- [Risco] Vazar password/DSN no relatório (nomeadamente via `str(exc)` de `OperationalError`). → Mitigação: decisão 4/5 — declarar só `user`/`host`/`port`/`dbname` + origem; sanitizar a mensagem; nunca imprimir o DSN cru.
- [Risco] O `SELECT` de confirmação falhar/demorar e transformar um sucesso em falha. → Mitigação: confirmação **best-effort**; a identidade derivada do ambiente é sempre declarada; a falha da confirmação não muda o `status`.
- [Risco] O código de saída `3` colidir com convenções de automação. → Mitigação: contrato explícito e documentado (decisão 3): `0` = não houve `não medido`; `3` = `não medido`; `2` reservado ao `argparse`. O sumário `--json` repete o código em `measurement.exit_code`.
- [Risco] `str(exc)` variar por driver/locale. → Mitigação: `type(exc).__name__` permanece sempre na nota; a mensagem real é best-effort e limitada.
- [Risco] Reabrir #1030 por arrasto (limiar/amostra). → Mitigação: `sample_sufficient`, política por regime, geometria e horizonte **intocados**; o fecho por regime só **acrescenta** o rótulo de medição parcial, sem mudar o predicado.
- [Risco] A corrida legítima sem log (log ausente/vazio) passar a falhar. → Mitigação: `não aplicável` fora do contrato de erro (decisão 3).
- [Trade-off] Quatro estados de medição (medido/parcial/não medido/não aplicável) em vez dos três nomeados no issue — aceite: `não aplicável` existe só para não transformar «log vazio» num erro de medição de OHLCV; os três estados do issue ficam intactos.

## Apply contract

**Contrato visível (não P3):**

- **Relatório — secção de medição:** o relatório tem uma secção `## Medição do realizado` que declara o `status` (`medido` | `medição parcial` | `não medido` | `não aplicável`), o `n` de janelas, o `n_priced` e, quando houver lacuna, **quantas janelas ficaram sem preço por cobertura e porquê**.
- **Relatório — veredicto sem confusão:** nenhum caminho do relatório imprime `**Amostra insuficiente**` quando `status = não medido`; nesse caso o veredicto é `**Realizado não medido**` com o motivo. `medição parcial` é rotulada como tal (com a contagem) e a insuficiência de amostra, quando existir, é declarada em separado. `medido` + amostra curta mantém `**Amostra insuficiente**` (comportamento actual).
- **Relatório — causa real:** as notas de falha de leitura incluem a mensagem do erro subjacente (limitada e sanitizada) além de `type(exc).__name__`; a falha de import mantém o módulo em falta; `OHLCV desativado` identifica a ausência de `DATABASE_URL`.
- **Relatório — ligação/utilizador declarado:** o relatório declara `user`, `host`, `port`, `dbname` e a origem da ligação, **sem password**, tanto no sucesso como na falha; no sucesso pode confirmar a identidade da sessão por `SELECT` read-only.
- **Saída — corrida que não mediu termina em erro:** `status = não medido` com decisões presentes ⇒ `main()` devolve `3` e o processo sai não-zero; o relatório (stdout) e, quando pedidos, `--json` e `--out` são emitidos **antes** de sair. `medição parcial`, `medido` e `não aplicável` saem `0`.
- **`--json`:** o sumário expõe `measurement` (`status`, `reason`, `connection`, `windows_without_price`, `exit_code`); `insufficient` mantém o significado de **amostra** e não é usado como sinal de medição.
- **Fecho por regime:** um regime fechado por lacuna de cobertura declara «medição parcial — X janela(s) sem cobertura» ao lado do motivo de amostra; a regra de fecho do #1030 (`n_priced < 30`) permanece intacta.
- **Invocação inalterada:** sem `--dsn`/`--db-url` nem env de acesso novo; o acesso continua a vir do ambiente (`app.database`), como hoje.
- **Read-only:** sem escrita em produto, estado do scalp ou base de dados; sem o loop do scalp; teste de read-only existente mantido e a cobrir o ficheiro.
- **Não-regressão:** limiar de confiança, política por regime, geometria alvo/stop, horizonte de espera, mínimos `MIN_NON_OVERLAPPING_WINDOWS`/`MIN_BUCKET_TRADES` e a regra `sample_sufficient` **não mudam**.

**P3 — detalhe de Apply (aceito aqui, resolvido no Apply — não reabrir como P0/P1):**

- Nome e forma exacta do resultado estruturado de `load_candles` (dataclass/campos) e como o `main` o transporta até `build_report`.
- Valor exacto do código de saída (`3` proposto) e a chave exacta do sumário (`measurement.exit_code`).
- Regras exactas de sanitização da mensagem de erro (limite de caracteres, padrões de DSN/password removidos).
- Wording exacto dos rótulos (`**Realizado não medido**`, `**Medição parcial**`) e do texto da secção de medição.
- Se a identidade é confirmada por `SELECT` à sessão e com que query; como se comporta quando o repo está desativado (`_enabled = False`, `:285`) ou o import falha.
- Como se conta «janela sem preço por cobertura» vs «janela sem preço por ausência de entrada» (`realized_for:562-563`) e como o relatório rotula a segunda.
- Como os testes injectam leitura falhada/parcial/sem cobertura sem base de dados real e como provam o código de saída não-zero.

## Open Questions / pontos deixados ao crítico

Nenhuma pergunta ao operador — Q1/Q2/Q3 vieram fechadas na grelha de 25/09 e as decisões 1–8 fecham o *como*. O que fica aberto para a crítica, sem reabrir decisões do card:

1. **Fronteira `não aplicável`.** Log ausente/vazio fica fora do contrato de erro (decisão 3), por não haver lado realizado a medir; se o crítico considerar que o issue exige erro nesse caso, o P0 é de produto e reabre a decisão 3 — mas a evidência do card é sobre OHLCV com decisões presentes (74 janelas), não sobre log vazio.
2. **Código de saída `3`.** Valor fixado como proposta no contrato visível; a alternativa (reutilizar `2`) colidiria com o `argparse`. P3 se se preferir outro valor, desde que não-zero e distinto de `2`.
3. **Acesso por ambiente vs `--dsn`.** O issue admite as duas vias; a decisão fechada de Q2 escolheu o ambiente e fixou «a invocação não muda» — o design não reabre.

## Design Critique

**Teto:** sem-tela = 1 autor + 1 crítico + 1 rework. Rodadas usadas: **1 autor + 1 crítico**; rework **não** foi necessário (0 P0/P1).

**Veredito:** **PASS** — `rework: nao`, `p0_p1_count: 0`. Nenhum achado de produto/escopo.

**Rubrica do crítico (8 itens):** todos `ok`.

1. Tokens do gate em linha própria parseável (`UI impact: none` · `live_route: N/A ...` · `surface: new`), sem rota de catálogo emprestada; Prototype N/A e Impeccable N/A justificados; bloco D4 verbatim.
2. Briefing verbatim — `proposal.md` copia `## Problema`, `## História`, `## Entra` (incl. `### Decisões fechadas (grelha 25/09)`) e `## Não entra` por secção: **5/5 IDENTICAL**.
3. Escopo — nada do `## Não entra` entrou; limiar de confiança, política por regime, geometria alvo/stop e horizonte intactos; #1030/#1025 não reabertos; sem painel/Monitor; sem PROD.
4. Decisões fechadas da grelha preservadas com contrato observável:
   - **Q1** — corrida que não conseguiu medir o realizado termina em **erro não-zero** (exit `3`, distinto do `2` do `argparse`) e o relatório «realizado não medido» é emitido **antes** de sair.
   - **Q2** — acesso pelo **ambiente** (invocação inalterada) e `user`/`host`/`port`/`dbname` + origem **declarados no relatório no sucesso e na falha**, sem password, com a **causa real** visível (mensagem + classe, sanitizada).
   - **Q3** — **«medição parcial»** distinta de **«amostra insuficiente»**, com contagem e motivo, **inclusive no fecho por regime** (predicado `n_priced < 30` do #1030 intacto).
5. Falha ≠ insuficiência em **todos** os caminhos (veredicto, `--json`, fecho por regime e secção de medição); nenhum caminho colapsa as duas.
6. Coerência interna — requisitos × cenários × tasks × decisões × riscos; `tasks.md` com 27 caixas, todas `- [ ]`.
7. Riscos e alternativas — 8 decisões, cada uma com alternativa rejeitada real; riscos com mitigação.
8. N/A (sem tela) — sem protótipo/HTML/rota de catálogo; `design.md` sem `## Design Critique` até esta secção.

**P3 aceitos (detalhe de Apply — resolvidos no Apply, nunca reabertos como P0/P1):**

- A1 — citações de linha ligeiramente deslocadas (`"insufficient"` é `:1113`; `ohlcv`/`ohlcv_candles` são `:1110-1111`; `def build_report` é `:1039`). Sentido factual preservado; acertar no Apply.
- A2 — `OHLCV desativado (sem DATABASE_URL)` (`scalp_jev_eval.py:462`) é aparentemente inalcançável (o import de `app.database:72` levanta primeiro). No Apply, tratar o import falhado como causa de «não medido» e manter `:462` como defesa.
- A3 — em «não medido», emitir primeiro o motivo de **medição** e separar visualmente o motivo de **amostra** (ordem dos bullets de `reasons`).
- A4 — garantir precedência de `não aplicável` quando o log está presente mas vazio (sem decisões a medir).
- Forma/nome do resultado estruturado de `load_candles`; valor exacto do código de saída (`3` proposto) e chave `measurement.exit_code`; regras de sanitização; wording dos rótulos; confirmação por `SELECT` e comportamento com repo desativado; separação «sem preço por cobertura» vs «por ausência de entrada»; como os testes injectam leitura falhada/parcial sem DB real.

**Factos conferidos pelo crítico (path:linha):** `scalp_jev_eval.py:1570` (`return 0`) e `:1574` (`raise SystemExit(main())`); `:1165-1166` e veredicto `:1385-1389`; `:1233-1236`; `:88-89`; `:831-835`; `:895-898`; `:1561-1568`; `:50`; `:442-520`; `backend/app/database.py:54,61,72`; `backend/app/services/ohlcv_storage.py:15,283-289,413-420`.

**Proxies:** `openspec validate --strict` → `Change 'card-1043-jev-medicao-explicita' is valid` (exit 0); `git status --porcelain` sem `backend/**`/`frontend/**`; `design.md` = 3257 palavras (antes desta secção); spawns desta entrada: `design-autor` + `design-critic` → `deepseek-flash`.
