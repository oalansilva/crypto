UI impact: affected
live_route: /combo/results
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: `/combo/results` (canônico, `index.html`, e a análise aberta de Favoritos, `favorite.html`), `/favorites` (`favorites.html`) e `/combo/discovery` no Decidir (`discovery.html`, recapturado no r3 com uma varredura de 5 candidatos). Em todas, o shell autenticado e o conteúdo vivo são COPIED; o delta é só o da história.

## Context

Card [#1123](https://github.com/oalansilva/crypto/issues/1123), sétima história do épico [#1116](https://github.com/oalansilva/crypto/issues/1116). O briefing é o issue grelhado, com as quatro decisões de Alan de 27/10/2026 dentro de Entra, mais a decisão de Alan no Design de 28/10/2026 ([comentário](https://github.com/oalansilva/crypto/issues/1123#issuecomment-6462139347); ver `proposal.md`, "Decisões de Alan no Design"): no Decidir, uma referência escolhida vira uma coluna extra por candidato, sem mudar a ordem nem a elegibilidade. Não houve reentrevista. O *como* abaixo foi conferido em `develop` @ 9b83d25e. Os OpenSpec de #1117 a #1122 (`openspec/changes/card-1117-*` a `card-1122-*`) são os contratos reutilizados: catálogo e seletor de ativos, histórico Binance e amostra congelada (`execution_data_snapshots`, fixação por favorito), backtest de ação/ETF com calendário de NY, lote, Descoberta multiclasse e configuração do favorito (fonte, sessão, ajuste).

Estado atual, conferido no código:

- **Buy-and-hold:** `metrics/benchmark.py::calculate_buy_and_hold` compra no primeiro fechamento e vende no último; CAGR por dias corridos / 365,25. Com menos de 2 preços ou preço inicial ≤ 0, devolve **zero** (o que a história proíbe mostrar como comparação). `backtest_service._calculate_benchmark` e `combo_optimizer` (ranking e holdout) usam essa função.
- **Onde aparece:** só na Descoberta (`DiscoveryPage.tsx`: "CAGR vs B&H", "B&H … · Δ …", "benchmark B&H long-only" no short). A tela do resultado (`ComboResultsPage.tsx`) **não mostra referência nenhuma**: `EnhancedMetricsDisplay`/`PerformanceMetrics` existem, mas nenhuma página os usa. O body diz que o buy-and-hold "aparece no resultado"; no código de hoje não aparece. Isso não muda o escopo: a seção nova passa a mostrá-lo.
- **Resultado não é gravado no servidor:** `POST /api/combos/optimize` e `/backtest` devolvem o resultado e o front o leva em `history.state` para `/combo/results`. O favorito guarda o resultado (métricas, trades, `analysis_*`, `snapshot_id`). A análise do favorito abre a mesma `/combo/results` com `returnTo: '/favorites'` e `isOptimization: false`.
- **Retorno total da tela:** `ComboResultsPage` deriva "Retorno total" do composto dos trades fechados (`derivedMetrics`), não das métricas do servidor.
- **Planilhas:**
  - Favoritos: montada no navegador com SheetJS (`FavoritesDashboard.handleExportExcel`), cabeçalhos em inglês, sem classe, moeda, fonte, sessão, ajuste, referência nem amostra;
  - trades: `POST /api/combos/export-trades` (pandas + openpyxl, aba "Trades"), chamada com `fetch` sem token, embora a rota exija admin;
  - Descoberta: não exporta.
- **Amostra:** `market_history/snapshots.py` congela segmentos Parquet por SHA-256 com manifesto e prazo de 30 dias; manifesto fixado (`pinned`) por favorito não vence. `sample.provenance_from_entry` dá fonte, sessão, ajuste, `version_label`, `content_sha256`.
- **Calendário:** cripto 24/7 em UTC; ação/ETF pelo pregão regular de NY (`nyse_calendar.py`), com split ajustado e sem dividendos (SPY e AAPL iguais ajustado x não ajustado nos ex-dividendos).
- **Anualização:** a tela do resultado diz "dias corridos ÷ 365" nas convenções da execução (#1119); o buy-and-hold e a Descoberta usam 365,25.
- **Decidir, hoje:** "Ordenar por" oferece Calmar e "CAGR vs B&H" (só `calmar_ratio | delta_cagr_vs_bh`; outro valor dá 400). `rank_eligible` ordena os elegíveis (GO e depois NO-GO) pela métrica; inelegíveis (`low_sample`, `insufficient_sample`) vêm no fim, sem rank. B&H e Δ do próprio ativo aparecem em "+ detalhes". A tabela vira cartão abaixo de 720 px (`td[data-label]`). `discovery_results` grava métricas, janela, `snapshot_id` e `candle_version`, **não grava os trades**: a promoção os regenera a partir da amostra congelada. A amostra da varredura vence em 30 dias ("amostra até …") se nada a fixar. Ativos que saíram da Binance não entram na varredura (viés de sobrevivência na tela).

## Goals / Non-Goals

**Goals:**

- Mostrar, na tela do resultado e na análise do favorito, a comparação da estratégia com uma referência escolhida depois de rodar, padrão o próprio ativo.
- Gravar a comparação (números, período comum, o que ficou de fora, moedas, amostra da referência) uma vez, sem recalcular ao abrir ou exportar.
- Dar às três planilhas o mesmo contexto, montado pelo servidor, com "deduzido" e "não registrado" para favoritos antigos.
- Exportar o ranking da Descoberta.
- No Decidir, mostrar o resultado de cada candidato contra uma referência escolhida, numa coluna extra, gravada e sem mudar a ordem (decisão de Alan, 28/10/2026).

**Non-Goals:**

- Fonte nova de preço ou de câmbio; conversão USDT x USD.
- Escolher referência antes de rodar (o seletor do Decidir age sobre uma varredura já concluída; o formulário da varredura não ganha campo).
- Ordenar, filtrar ou mudar elegibilidade, rank global, B&H ou Δ da Descoberta e do lote por outra referência. A coluna extra do Decidir entra (decisão de Alan, 28/10/2026); ela não vira opção de "Ordenar por" nem filtro. O lote não ganha coluna.
- Retorno total com dividendos.
- Alocação de carteira, relatório fiscal, gráfico de curva da referência.

## Decisions

### 1. Rota primária: `/combo/results`

A troca de referência só existe em `/combo/results`: é a tela do resultado (rodada nova) e também a "tela do favorito" (a análise aberta de Favoritos usa a mesma rota). A planilha de trades também sai dela. `/favorites` muda pouco (a linha mostra "Ref.: SPY" e a exportação vai para o servidor) e `/combo/discovery` ganha um botão e uma frase. Por isso o canônico clona `/combo/results`; Favoritos, a análise do favorito e o Decidir são páginas extras.

Rework r3 (Descoberta): Alan diz que hoje usa mais a Descoberta, e o Decidir ganha a coluna extra. Mesmo assim `live_route` continua `/combo/results`: a comparação completa (período comum, o que ficou de fora, linha de gravação, todos os estados e a troca no favorito) e a planilha de trades só existem na tela do resultado, e a coluna do Decidir reaproveita o seletor, o contrato e o cálculo dela (decisões 3, 4 e 10). O Decidir continua página extra (`discovery.html`), agora com mais delta.

### 2. Seção "Comparação com referência"

Logo abaixo da análise da estratégia e acima de "Dados e execução", com a mesma moldura (`r19-data`):

- referência atual (símbolo, "(próprio ativo)" no padrão, classe, moeda, "buy-and-hold"; "buy-and-hold long-only" quando a estratégia é short);
- botão "Trocar referência" (44 px);
- três números no período comum: estratégia (retorno e CAGR), referência (retorno e CAGR) e diferença de CAGR em p.p., com o tom de alta/queda do resumo vivo;
- período comum (datas e dias), o que ficou de fora (datas e trades da estratégia) e "Retorno de preço, sem dividendos" quando a referência é ação/ETF;
- aviso de moeda no mesmo componente de aviso da execução (`r19-precision` em tom de alerta), com as duas moedas escritas;
- linha de gravação: quando e onde foi gravada (resultado ou favorito), a versão da amostra da referência, "Abrir ou exportar de novo não recalcula" e, na rodada nova, "Ao salvar nos Favoritos, a referência vai junto". No favorito, também "Refeita só quando o backtest do favorito é atualizado, com a mesma referência." (o único recálculo, decisão 5);
- subtítulo da seção: "Buy-and-hold da referência · fechamentos diários no período comum · CAGR com dias corridos ÷ 365,25".

Estados:

- válido;
- gravando/coletando (`role=status`, sem números: nem visíveis nem no DOM, até a gravação voltar);
- histórico insuficiente ("Sem comparação" + motivo + frase de apoio, sem números nem zero, sem aviso de moeda), com frase de apoio por motivo:
  - sem período comum (`no_overlap`): motivo com as duas datas e "Escolha outra referência com histórico no período da estratégia.";
  - período comum curto (`short_overlap`): "Período comum de N dias: o mínimo é 30." + as datas, e "Com poucos dias, anualizar exagera o CAGR. Escolha uma referência com mais histórico dentro do período da estratégia." O número 30 é proposta (Open Questions);
- falha na coleta (alerta com motivo e "Tentar de novo"; nada gravado, a comparação anterior continua);
- favorito sem comparação registrada ("Comparação não registrada", "Comparar com o próprio ativo" e "Trocar referência"; nada calculado ao abrir).

### 3. Seletor "Escolher referência"

Diálogo modal de escolha única: busca, filtro de classe (Todas, Cripto, Ações, ETFs), "Próprio ativo" no topo marcado "Padrão", linhas com símbolo, classe, moeda, nome e situação do histórico ("Histórico desde …" ou "Sem histórico guardado: coleta ao escolher"). Ativo marcado/indisponível no catálogo (#1117: suspenso, fora de mercado, sem negociação, sem regras, removido) aparece desabilitado: borda tracejada, rádio `disabled`, o estado ("Removido") e o motivo do catálogo na linha, ligado ao rádio por `aria-describedby`, mais "Não pode ser escolhido como referência."; clicar não muda a escolha e o Tab o pula. Antes da escolha, a opção que levaria a "Sem comparação" avisa na linha, em tom de alerta com ícone, sem bloquear: "Sem período comum com esta estratégia" quando o histórico guardado começa depois do fim da estratégia (ou termina antes do início) e "Só N dias em comum com esta estratégia" quando o período comum fica abaixo do mínimo. O aviso sai do histórico guardado do catálogo e da janela da estratégia, sem coletar. Os filtros de classe têm 44 px no toque. "Usar referência" (primário) e "Cancelar". Foco preso, Esc fecha, foco volta ao gatilho. No Apply, a lista vem de `GET /api/assets/catalog` (mesma busca e mesmas contagens do `AssetPicker`, em modo de escolha única); no celular o diálogo ocupa a tela.

### 4. Contrato da comparação

Novo `services/benchmark_comparison.py`, uma função pura de cálculo e uma de gravação:

```text
BenchmarkComparison {
  id (uuid), created_at, trigger: run | choice | favorite_refresh
  owner: { kind: result | favorite | discovery_result, favorite_id?, result_id?, column_id? }, user_id
  reference: { kind: own | catalog, symbol, asset_id, asset_class, currency, name,
               return_kind: price | price_no_dividends, long_only: bool }
  strategy:  { symbol, asset_class, currency, window: {start, end},
               return, cagr, trades_in, trades_out }        # no período comum
  reference_result: { return, cagr, first_close: {date, price}, last_close: {date, price} }
  common_window: { start, end, days } | null
  left_out: [ { start, end, trades } ]                      # partes da janela da estratégia
  delta: { cagr_pp }
  currency_note: usdt_as_usd | null
  status: valid | insufficient
  reason: { code: no_history | no_overlap | short_overlap, text } | null
  samples: { strategy: {snapshot_id, version_label} | null,
             reference: {snapshot_id, version_label, data_version, content_sha256,
                         source, session, adjustment} }
}
```

Regras:

- **Janela da estratégia:** `execution.window.covered` do resultado; no favorito, a do último refresh. Sem janela gravada (favorito antigo), o período pedido, e a planilha marca "deduzido".
- **Série da referência:** fechamentos 1d do histórico Binance (#1118), ajustados por split em ação/ETF; mesmo no próprio ativo de tempo gráfico intradiário (a comparação é diária e a tela diz "fechamentos diários").
- **Período comum:** início = maior dos dois inícios; fim = menor dos dois fins; encaixados nas datas com fechamento da referência (UTC na cripto, pregão de NY em ação/ETF). Exemplo: BTC/USDT de 01/01/2019 a 31/12/2024 contra SPY dá 02/01/2019 a 31/12/2024; o dia 01/01/2019 (feriado em NY) fica de fora com 0 trades.
- **Retorno da referência:** último fechamento / primeiro fechamento − 1 no período comum.
- **Retorno da estratégia:** composto dos trades fechados com entrada e saída dentro do período comum. Trade que cruza a borda fica de fora e é contado. Quando o período comum é a janela inteira, o número é igual ao "Retorno total" da tela, que também é o composto dos trades fechados.
- **CAGR:** dos dois lados, `(1 + R)^(365,25 / dias do período comum) − 1`, o mesmo denominador e a mesma convenção do buy-and-hold e da Descoberta. A linha da seção diz "fechamentos diários no período comum". A diferença de 365 (convenção da execução) para 365,25 fica registrada como P3.
- **Diferença:** CAGR da estratégia − CAGR da referência, em p.p.
- **Insuficiente:** sem candle diário depois da coleta (`no_history`), sem interseção (`no_overlap`) ou período comum com menos de 30 dias corridos (`short_overlap`, ver Open Questions). Nunca devolve zero: o caminho novo não usa o retorno 0,0 de `calculate_buy_and_hold`. O caminho da Descoberta e do holdout não muda.
- **Moeda:** classes com moedas diferentes (USDT x USD) ⇒ `currency_note = usdt_as_usd`; cripto contra cripto em outra cotação segue a mesma regra pela moeda do par.
- **Short:** referência sempre comprada (long-only), como na Descoberta.

### 5. Persistência e "sem recálculo escondido"

- **Tabela nova `benchmark_comparisons`:** colunas indexadas `id`, `user_id`, `favorite_id`, `created_at`, `status` e o resto do contrato em JSON. Coluna nova `favorite_strategies.benchmark_comparison_id` (FK, nula).
- **Amostra da referência:** congelada com o mecanismo do #1118, papel `benchmark`, só a série 1d no período comum. O manifesto é fixado enquanto um favorito aponta para a comparação. A comparação de uma rodada que não virou favorito vence com a amostra, em 30 dias.
- **Rodada nova:**
  - `optimize` e `backtest` gravam a comparação padrão (`trigger=run`) e a devolvem em `benchmark_comparison`;
  - trocar chama `POST /api/benchmark-comparisons {owner: result, strategy context, trades, reference_symbol}` e grava uma comparação nova;
  - o front troca `history.state.result.benchmark_comparison` (`navigate(..., {replace: true})`), então recarregar a página mantém a escolha. Hoje o resultado da rodada já vive só no `history.state`; isso não muda.
- **Salvar nos Favoritos:** `POST /api/favorites` recebe `benchmark_comparison_id`, o favorito aponta para ela e o manifesto da referência é fixado.
- **Favorito:**
  - trocar chama `POST /api/benchmark-comparisons {owner: favorite, favorite_id, reference_symbol}`. O servidor monta o lado da estratégia com os trades e a janela gravados no favorito, grava a comparação, troca o ponteiro e solta a fixação da amostra anterior;
  - `GET /api/favorites` devolve a comparação resumida, para "Ref.: SPY" e para a planilha.
- **Leitura:** abrir a tela e exportar leem a comparação gravada. Não há caminho que recalcule ao ler: a rota de leitura não chama o cálculo.
- **Refresh do favorito:** `favorite_backtest_refresh_service`, depois de um refresh com sucesso, recalcula com a referência escolhida (ou o próprio ativo) e grava com `trigger=favorite_refresh`. A tela mostra a nova data. É o único recálculo, e ele acompanha um evento já visível ("Backtest atualizado").
- **Favorito sem comparação:** a seção mostra "Comparação não registrada" e não calcula ao abrir. O primeiro refresh depois do deploy grava a do próprio ativo.

### 6. Coleta da referência na escolha

Ao escolher um ativo sem histórico guardado, o servidor coleta antes de calcular:

- ação/ETF por `prepare_equity_history(symbol, "1d", start, end, intrabar=False)`;
- cripto pelo `HistoryService` do #1118.

A chamada é síncrona com teto de tempo. A seção mostra "Coletando histórico de X na Binance…". Falha sem nada guardado ⇒ nada é gravado, a comparação anterior continua, alerta com o motivo e "Tentar de novo". Falha com parte guardada ⇒ calcula no que existe, e o período comum mostra o que ficou de fora. Só o catálogo e o histórico Binance existentes: nenhuma fonte nova.

### 7. Planilhas com contexto, pelo servidor

Novo `services/export_context.py`, um construtor único para as três planilhas, com as colunas na ordem do spec:

- Classe, Moeda, Fonte, Sessão, Ajuste;
- Período pedido, Período efetivo, Modo de execução, Versão da amostra;
- Referência, Tipo de retorno da referência, Período comum, Fora do período comum;
- Retorno e CAGR da estratégia no período comum, Retorno e CAGR da referência, Diferença de CAGR (p.p.);
- Situação da comparação, Aviso de moeda, Versão da amostra da referência, Comparação gravada em.

Cada valor sai com estado `registrado | deduzido | não registrado`. Na planilha, "deduzido" vira sufixo "(deduzido)" e "não registrado" é o próprio texto. Toda planilha ganha a aba "Legenda". "Tipo de retorno da referência" usa o texto da tela: "Retorno de preço, sem dividendos" para ação/ETF e "Retorno de preço" para cripto. A Legenda da planilha de Favoritos (e a da planilha de trades aberta de um favorito) também explica "Comparação refeita: só quando o backtest do favorito é atualizado, com a mesma referência". A de Favoritos diz ainda "Tela × planilha: a tela de Favoritos mostra a convenção da classe (fonte e sessão); a planilha só traz o que foi gravado e marca o resto como “não registrado”".

- **Favoritos:** `GET /api/favorites/export?ids=…` (admin, como o botão de hoje). O front manda os ids da lista filtrada na ordem da tela. As colunas de hoje continuam com os mesmos nomes e vêm antes das de contexto. O SheetJS sai dessa tela.
- **Trades:** `POST /api/combos/export-trades` passa a usar `authFetch` e recebe `context` (asset, data_provenance, execution, conventions, período e modo do resultado, `favorite_id` quando houver) e `benchmark_comparison_id`. Abas: "Trades" (como hoje + Moeda), "Contexto" (Campo, Valor, Estado) e "Legenda". Com `favorite_id`, o servidor lê o contexto do favorito e ignora o do corpo.
- **Descoberta:** `GET /api/combos/discovery/sweeps/{id}/leaderboard/export?metric&class&symbol&timeframe&direction`. Leva todos os candidatos do recorte (todas as páginas), na ordem e com o rank global do leaderboard. Abas "Ranking" e "Legenda".
  - Colunas: as do leaderboard de hoje e as de contexto.
  - Referência fixa "Próprio ativo (buy-and-hold, long-only)".
  - Período comum = janela de evidência gravada. Versão da amostra = `candle_version` + `snapshot_id`.
  - Retornos derivados só de CAGR e janela gravados, sem dado novo: `(1 + CAGR)^(dias / 365,25) − 1`.
  - Os 22 campos de contexto, com os nomes e a ordem do spec, como nas outras duas planilhas: Período pedido = período da varredura; "CAGR da estratégia no período comum" = CAGR anualizado gravado; Tipo de retorno = "Retorno de preço, sem dividendos" em ação/ETF e "Retorno de preço" em cripto; Fora do período comum = "nada"; Situação = "Válida"; Aviso de moeda vazio (mesma moeda); Versão da amostra da referência = "a mesma do candidato"; Comparação gravada em = conclusão da varredura.
  - Candidato com janela de evidência abaixo do mínimo do período comum (30 dias, Open Questions): Situação = "Histórico insuficiente: Período comum de N dias: o mínimo é 30." e as células de retorno, CAGR e diferença vazias, como no resultado. As colunas de hoje do leaderboard (B&H CAGR, Δ) seguem com o valor gravado: é só a regra de exibição dos campos de contexto, sem recálculo.
  - Com uma referência extra escolhida no Decidir (decisão 10), entram depois dos 22 campos as 13 colunas da comparação extra, com o nome do campo correspondente seguido de " (extra)": Referência (extra), Tipo de retorno da referência (extra), Período comum (extra), Fora do período comum (extra), Retorno da estratégia no período comum (extra), CAGR da estratégia no período comum (extra), Retorno da referência (extra), CAGR da referência (extra), Diferença de CAGR (p.p.) (extra), Situação da comparação (extra), Aviso de moeda (extra), Versão da amostra da referência (extra), Comparação gravada em (extra). Os 22 campos continuam com o próprio ativo. A Legenda ganha "(extra)". Sem referência extra, a planilha não tem essas colunas.
- **Favorito antigo:**
  - Classe e Moeda deduzidas do símbolo pela mesma regra que a tela já usa (`/USDT` ⇒ Cripto/USDT; senão catálogo/classe da tela ⇒ Ação ou ETF/USD) e marcadas "(deduzido)";
  - Fonte, Sessão, Ajuste, Versão da amostra, Período efetivo e Modo de execução sem registro ⇒ "não registrado";
  - sem comparação ⇒ Referência "Próprio ativo", Situação "não registrado" e células numéricas vazias.

### 8. Descoberta e lote

Nenhuma mudança no cálculo do ranking, na ordem, no rank global, no B&H, no Δ nem na elegibilidade. "Ordenar por" continua com Calmar e "CAGR vs B&H" (próprio ativo), e a rota do leaderboard continua recusando outra métrica. O Decidir ganha:

- a frase "Referência do ranking: o próprio ativo (buy-and-hold, long-only). A ordem, o rank global e a elegibilidade não mudam com a coluna extra nem com a referência escolhida num resultado ou favorito.";
- o botão "Exportar planilha" (44 px, com status do download em região `polite`, desabilitado sem linhas ou carregando);
- a faixa "Coluna extra" e a coluna "Contra <ativo>" (decisão 10).

O lote não ganha tela nem coluna: o ranking dele segue o próprio ativo, e o favorito que ele cria entra na regra 5.

### 9. Favoritos

A linha e o cartão móvel mostram "Ref.: SPY · comparação gravada 27/10" quando a referência gravada não é o próprio ativo (no protótipo, NVDA Trend com SPY e SPY Trend com "Ref.: BTC/USDT", coerentes com a prévia da planilha). Sem nada novo para o padrão, para não pesar a coluna Estratégia. "Exportar" mantém lugar e rótulo e passa a baixar do servidor.

### 10. Coluna extra no Decidir (decisão de Alan, 28/10/2026)

**Onde e padrão.** Uma faixa "Coluna extra" logo abaixo da frase "Referência do ranking", antes dos filtros, na mesma largura do cabeçalho do Decidir. Padrão: "Próprio ativo", **sem coluna extra** (o ranking já compara com o próprio ativo; repetir o número só pesaria a tabela). A faixa diz "Coluna extra: Nenhuma" e "Compare cada candidato com outra referência, como SPY, numa coluna a mais. A ordem e o rank global não mudam.", com o botão "Comparar com outra referência" (44 px). Com uma referência, a faixa mostra o ativo (símbolo, classe, moeda, "buy-and-hold" e, em ação/ETF, "Retorno de preço, sem dividendos"), a frase "A coluna não muda a ordem, o rank global nem a elegibilidade.", o resumo ("4 de 5 candidatos com comparação; 1 sem comparação (período comum curto).", ou "Nenhum candidato tem período comum com CRCL: …" quando ninguém tem), o aviso de moeda quando alguma linha o tem, a linha de gravação e o botão vira "Trocar referência". Mensagens de progresso e de falha ficam numa região `role=status`/`role=alert` dentro da faixa.

**Seletor.** O mesmo diálogo da decisão 3 (busca, filtro de classe com 44 px no toque, ativo marcado desabilitado com estado e motivo do catálogo ligado por `aria-describedby`, foco preso, Esc, foco volta ao gatilho, tela cheia no celular), com título "Escolher referência da coluna extra" e a primeira opção "Próprio ativo · Padrão · Sem coluna extra". O aviso antes da escolha é contado sobre os candidatos da varredura, sem coletar: "Sem período comum com nenhum candidato desta varredura" (alerta) e "N candidato(s) com período comum curto (…)" (nota discreta, porque não invalida a coluna). Escolher "Próprio ativo" tira a coluna.

**Coluna.** Cabeçalho "Contra SPY" com a dica "Δ CAGR · período comum", antes de "Ação". Célula válida: diferença de CAGR em p.p. (tom de alta/queda), "SPY +15.25% a.a." e o período comum (datas). Linha em que estratégia e referência têm moedas diferentes: "USDT tratado como USD" com ícone, visível (texto, não tooltip). Insuficiente: "Sem comparação" + motivo curto ("Período comum de 14 dias: o mínimo é 30." ou "Sem período comum com CRCL."), sem número nem zero. Calculando: "Calculando…", sem número no DOM. Candidato sem métrica (`insufficient_sample`): "Sem amostra". Candidato cuja amostra congelada venceu: "Sem comparação" + "Amostra do candidato vencida em <data>." (não há como regenerar os trades sem dado novo). No celular (abaixo de 720 px) a célula ocupa a largura do cartão, com o rótulo "Contra SPY" à esquerda, como as outras métricas.

**Valor, coerente com a seção do resultado.** Para cada candidato, a mesma função `benchmark_comparison.compute` da decisão 4: janela do candidato = janela de evidência gravada; período comum encaixado no calendário da referência; retorno da estratégia = composto dos trades fechados de dentro; os dois CAGRs com dias corridos ÷ 365,25; diferença em p.p.; long-only; `currency_note`; motivos `no_history | no_overlap | short_overlap`. Os trades do candidato são **regenerados da amostra congelada dele** (`snapshot_id`), pelo mesmo caminho determinístico da promoção, porque `discovery_results` não guarda trades. Nenhum dado novo do candidato é buscado. A planilha leva também "Fora do período comum (extra)" (datas e trades).

**Gravação, sem recálculo escondido.** Uma escolha = uma linha em `discovery_reference_columns` (`id`, `sweep_id`, `actor`, `reference` (símbolo, `asset_id`, classe, moeda), `reference_snapshot_id`, `status: collecting | computing | done | failed`, `done`/`total`, `error`, `created_at`, `completed_at`, `active`), única ativa por (`sweep_id`, `actor`). Cada célula = uma `benchmark_comparisons` com dono `discovery_result` (`result_id`, `column_id`). A amostra 1d da referência é congelada uma vez (papel `benchmark`, cobrindo a união das janelas dos candidatos) e fixada enquanto a coluna estiver ativa; as amostras dos candidatos também ficam fixadas enquanto a coluna existir. A escolha vale **por varredura e por usuário**: outra varredura começa sem coluna; recarregar ou voltar à varredura mostra a coluna lida do que foi gravado, sem calcular. Escolher de novo uma referência que já tem coluna gravada nessa varredura reativa a gravada (mostra a data dela), sem recalcular. Escolher "Próprio ativo" desativa a coluna e solta as fixações (GC em 30 dias, como as amostras).

**Coleta e falha.** Referência sem histórico guardado: coleta antes do cálculo, como na decisão 6 ("Coletando histórico de QQQ na Binance…"). Falha sem nada guardado: nada é gravado, a coluna anterior continua (ou nenhuma), alerta com o motivo e "Tentar de novo" (44 px).

**Contrato e custo.**

- `PUT /api/combos/discovery/sweeps/{id}/reference-column {reference_symbol | null}` (admin, dono da varredura): `null` = Próprio ativo. Responde 202 com a coluna (`status`, `done`, `total`) ou 200 quando reativa uma gravada.
- `GET /api/combos/discovery/sweeps/{id}/reference-column`: estado e progresso (o front consulta a cada 2 s enquanto `collecting | computing`). `POST …/reference-column/retry` depois de `failed`.
- `GET …/leaderboard` (mesmos filtros, `metric` e paginação de hoje): ganha `reference_column` (resumo e contagens) e, por linha da página, `reference_comparison` (resumo da célula), lido por junção; nada é calculado na leitura. Linhas ainda não calculadas vêm com `state: pending`.
- `GET …/leaderboard/export`: acrescenta as colunas "(extra)" quando há coluna ativa e `done`; com a coluna em cálculo, exporta sem elas e diz isso no status do download.
- Cálculo: um job no worker da fila de lotes (#1120), em lotes de 25 candidatos, com progresso gravado. Abrange todos os candidatos da varredura (o teto é o da própria varredura, `max_total` 1000), não só a página visível, para a coluna e a planilha não dependerem da paginação. Candidatos `insufficient_sample` e descartados não são calculados.

## Risks / Trade-offs

- **Retorno da estratégia no período comum vem dos trades, não de uma curva marcada a mercado:** um trade aberto na borda fica de fora inteiro. A tela conta esses trades em "Fora do período comum". Com o período comum igual à janela (caso comum), o número bate exato com "Retorno total".
- **Comparação diária para estratégia intradiária:** a referência usa fechamentos 1d, inclusive no próprio ativo de 4h/1h/15m. A diferença para um buy-and-hold no tempo gráfico é de um candle nas pontas. A tela diz "fechamentos diários".
- **Rodada nova sem registro no servidor:** a escolha sobrevive a recarregar (via `history.state`), mas não a abrir o link em outra aba. É o comportamento de hoje do resultado; a comparação fica no servidor por 30 dias.
- **Coleta síncrona na escolha:** um ativo longo pode levar segundos. O estado "Coletando…" e o teto de tempo cobrem isso, e a falha não grava nada.
- **Anualização 365,25 x 365:** a convenção da execução (#1119) diz 365 e o buy-and-hold usa 365,25. A comparação usa 365,25 dos dois lados (mesmo número da Descoberta). P3.
- **Favoritos antigos de fonte legada (Stooq):** a estratégia vem da fonte antiga e a referência da Binance. A comparação vale em percentual, mas a planilha marca a fonte como "não registrado" ou "Stooq · fonte antiga". A migração é do #1126.
- **Custo de gravação:** toda rodada grava uma comparação e uma amostra 1d pequena (≈ 3 mil linhas no pior caso). O vencimento em 30 dias segue o das amostras.
- **Custo da coluna extra:** uma escolha regenera os trades de todos os candidatos da varredura (até 1000), no worker da fila de lotes, em lotes. Uma varredura grande em 15m pode levar minutos; a coluna mostra "Calculando…" com progresso, a faixa diz quantos faltam e o ranking continua usável. Trocar de referência no meio cancela o job anterior.
- **Amostra do candidato vencida:** a amostra de uma varredura vence em 30 dias sem fixação. Numa varredura antiga, os candidatos vencidos ficam "Sem comparação · Amostra do candidato vencida" (regenerar com dado novo seria recálculo escondido). A partir da primeira escolha, a coluna fixa as amostras.
- **Referência que nenhum candidato cobre:** CRCL contra uma varredura que termina antes do histórico dela. O seletor avisa antes ("Sem período comum com nenhum candidato desta varredura") e a faixa resume o motivo, para a coluna inteira de "Sem comparação" não parecer erro.

### P3 aceitos (detalhe de Apply)

- Células numéricas da planilha como número com formato % (e texto só em "não registrado"/vazio), em vez das strings formatadas de hoje.
- Nome do arquivo da Descoberta (`descoberta_<sweep>_ranking.xlsx`) e da aba de contexto.
- Teto de tempo da coleta síncrona e mensagem exata da falha por código do #1118.
- Índices e GC de `benchmark_comparisons` junto do GC de amostras.
- Convenção de anualização 365,25 x 365 (texto da convenção da execução fica como está).
- Literais do CSS do delta copiados do incumbente (`11px`, `18px`, `#474d57`, sombra do modal) apontados pelo hook de design; no Apply, usar os tokens/classes do componente vivo.
- Achados do detector em regiões COPIED do incumbente (`flat-type-hierarchy`, `gray-on-color` em Favoritos).
- `EnhancedMetricsDisplay`/`PerformanceMetrics` sem uso: o Apply pode removê-los ou deixá-los; não são a seção nova.
- Coluna extra: tamanho do lote de cálculo, intervalo de consulta do progresso, cancelamento do job ao trocar de referência e atalho que pula a regeneração quando o período comum é a janela inteira e o resultado é provadamente igual ao gravado.
- Coluna extra: largura mínima da célula e quebra do motivo; texto exato de "Sem amostra" e de "Amostra do candidato vencida em <data>.".
- Gravação da escolha do Decidir no protótipo simulada com `sessionStorage` da aba; no produto, no servidor por varredura e usuário.

## Migration Plan

1. Alembic: tabela `benchmark_comparisons` (dono `result`, `favorite` ou `discovery_result`); tabela `discovery_reference_columns`; coluna `benchmark_comparison_id` (FK nula) em `favorite_strategies`. Sem backfill: favoritos existentes começam sem comparação e ganham a do próprio ativo no próximo refresh; varreduras existentes começam sem coluna extra.
2. Deploy de servidor e front juntos (a planilha de Favoritos e a de trades mudam de contrato).
3. Rollback: voltar o código ignora a coluna e a tabela; a planilha de Favoritos volta ao SheetJS. Nada é apagado.

## Open Questions

- **Mínimo do período comum:** a história pede "histórico suficiente" sem número. O Design propõe 30 dias corridos (abaixo disso, "Sem comparação" com o motivo). Alan confirma ou troca o número na Aprovação de Design. O protótipo mostra o estado como proposta: PENGU/USDT contra a rodada de BTC/USDT dá "Período comum de 14 dias: o mínimo é 30.", com a frase de apoio própria, e o seletor avisa antes "Só 14 dias em comum com esta estratégia". Se Alan trocar o número, muda só o N do texto e o limite do `short_overlap`. O mesmo mínimo vale para a coluna extra do Decidir (PENGU/USDT, janela de 14 dias: "Período comum de 14 dias: o mínimo é 30.") e para os campos de contexto da planilha da Descoberta.

## Apply contract

O Apply lê este `design.md`, os specs e os HTML de `frontend/public/prototypes/card-1123-benchmark-exportacao/` como spec de layout.

**Contrato visível (não P3):**

- **Resultado (`/combo/results`, rodada nova e análise do favorito):**
  - seção "Comparação com referência" entre a análise e "Dados e execução", com os estados válido, gravando/coletando, insuficiente (sem período comum e período comum curto, cada um com a sua frase de apoio), falha na coleta e não registrada;
  - números no período comum, período comum, o que ficou de fora, "Retorno de preço, sem dividendos", aviso "USDT tratado como USD, sem conversão" com as duas moedas, linha de gravação (no favorito, com a frase da refeitura);
  - seletor modal com busca, filtro de classe (44 px no toque), "Próprio ativo · Padrão", situação do histórico, aviso antes da escolha ("Sem período comum com esta estratégia", "Só N dias em comum com esta estratégia"), ativo marcado desabilitado com estado e motivo do catálogo, foco preso, Esc, retorno do foco, 44 px;
  - planilha de trades com abas Trades, Contexto e Legenda.
- **Favoritos:** "Ref.: <ativo> · comparação gravada <data>" na linha e no cartão; planilha pelo servidor com as colunas de hoje e as de contexto, "(deduzido)" e "não registrado"; Legenda com "Tela × planilha" e "Comparação refeita".
- **Descoberta (Decidir):** frase da referência do ranking; "Exportar planilha" com status; planilha com os mesmos 22 campos de contexto e, com referência extra, as 13 colunas "(extra)"; faixa "Coluna extra" (padrão Nenhuma, resumo, aviso de moeda, linha de gravação, progresso, falha com "Tentar de novo"); seletor reaproveitado com aviso contado sobre os candidatos; coluna "Contra <ativo>" em todos os candidatos (válida, calculando sem número, sem comparação com motivo, aviso de moeda na linha), cartão móvel com a linha a mais; escolha gravada por varredura e usuário, lida ao recarregar; ordem, rank global, "Ordenar por" e elegibilidade intocados.
- **Comportamentos dos specs:** janela comum, trades de fora, insuficiente sem zero, moeda, retorno de preço, gravação sem recálculo, refresh refaz com a mesma referência, herança ao salvar, coluna extra calculada uma vez sobre amostras congeladas, Descoberta e lote ordenados no próprio ativo.

**P3 aceito (Apply):** os itens da subseção "P3 aceitos".

## Prototype

- **Canônico:** `frontend/public/prototypes/card-1123-benchmark-exportacao/index.html`, clone de `/combo/results` com uma rodada nova de BTC/USDT 1d Long, período pedido 01/01/2019 a 31/12/2024, 9 trades, "Salvar nos Favoritos" ligado. URL: https://dev.criptofarol.com.br/prototypes/card-1123-benchmark-exportacao/
  - Seção "Comparação com referência" logo abaixo da análise, no padrão "BTC/USDT (próprio ativo)": +6352.66% (igual ao "Retorno total" vivo), CAGR +100.31%, referência +2360.60%, diferença +29.7 p.p.
  - "Trocar referência" abre o seletor (busca, Todas/Cripto/Ações/ETFs, Próprio ativo · Padrão, SPY, QQQ, NVDA, ETH/USDT, SOL/USDT, PENGU/USDT, CRCL e WAVES/USDT). CRCL avisa "Sem período comum com esta estratégia" e PENGU/USDT "Só 14 dias em comum com esta estratégia", antes da escolha. WAVES/USDT aparece desabilitado, "Removido", com "Saiu da lista spot da Binance em 17 jun. 2024. Não pode ser escolhido como referência."
  - O subtítulo da seção diz "CAGR com dias corridos ÷ 365,25".
  - SPY: "Gravando a comparação…", depois período comum 02 jan. 2019 – 31 dez. 2024, "01 jan. 2019 (sem pregão em Nova York) · 0 trades" de fora, "Retorno de preço, sem dividendos" e o aviso "USDT tratado como USD, sem conversão" com "BTC/USDT em USDT, SPY em USD".
  - SOL/USDT: período comum a partir de 11 ago. 2020, "3 trades fora", retorno da estratégia só dos trades de dentro, diferença negativa.
  - QQQ: "Coletando histórico de QQQ na Binance…" e depois a comparação.
  - CRCL: "Sem comparação" com "CRCL tem histórico desde 05/06/2025, depois do fim da estratégia (31/12/2024). Não há período comum.", "Escolha outra referência com histórico no período da estratégia.", sem números.
  - PENGU/USDT: "Sem comparação" com "Período comum de 14 dias: o mínimo é 30. PENGU/USDT tem histórico desde 17/12/2024 e a estratégia termina em 31/12/2024." e a frase própria "Com poucos dias, anualizar exagera o CAGR…", sem números.
  - "Exportar para Excel" mostra o arquivo e as abas (Trades, Contexto, Legenda).
  - **Demonstração** (fim da página, no fluxo): a aba Contexto da planilha de trades (22 campos), atualizada com a referência escolhida; a aba Legenda; "Período comum curto", que diz que o mínimo de 30 dias é proposta do Design à espera de Alan e tem "Ver período comum curto (PENGU/USDT)"; "Simular falha na coleta de QQQ" (alerta, nada gravado, "Tentar de novo").
- **Extra `favorite.html`** (clone de `/combo/results` aberto de Favoritos, NVDA 1d, "Voltar aos favoritos", sem "Salvar"): abre com SPY gravada no favorito ("Gravada no favorito NVDA Trend em 27/10/2026, 09:14", sem aviso de moeda). A linha de gravação diz "Refeita só quando o backtest do favorito é atualizado, com a mesma referência." BTC/USDT mostra o aviso ("NVDA em USD, BTC/USDT em USDT") e "2 trades fora". O seletor tem o mesmo WAVES/USDT desabilitado. A Demonstração tem "Ver como favorito sem comparação registrada" ("Comparação não registrada", "Comparar com o próprio ativo") e a Legenda com "Comparação refeita".
- **Extra `favorites.html`** (clone de `/favorites`): "Ref.: SPY · comparação gravada 27/10" na linha e no cartão de NVDA Trend e "Ref.: BTC/USDT · comparação gravada 27/10" na linha e no cartão de SPY Trend; "Exportar" mostra o arquivo; Demonstração com as colunas de hoje (Name, Symbol) e os 22 campos de contexto das quatro linhas, inclusive "BTC antigo" com "Cripto (deduzido)", "USDT (deduzido)" e "não registrado", e SPY Trend contra BTC/USDT com o aviso de moeda; Legenda com "Tela × planilha" e "Comparação refeita".
- **Extra `discovery.html`** (clone de `/combo/discovery` no Decidir, recapturado no r3: varredura `#c1123mix` de 01/01/2019 a 31/12/2024, ordenada por "CAGR vs B&H", com BTC/USDT, NVDA, SOL/USDT e SPY (rank 1 a 4) e PENGU/USDT 1h com janela de 14 dias, baixa amostra e sem rank):
  - frase "Referência do ranking: o próprio ativo (buy-and-hold, long-only). A ordem, o rank global e a elegibilidade não mudam com a coluna extra…" e "Exportar planilha" (44 px) com status "todas as páginas";
  - faixa "Coluna extra: Nenhuma" e "Comparar com outra referência"; o seletor (Próprio ativo · Padrão, SPY, QQQ, BTC/USDT, CRCL e WAVES/USDT desabilitado) avisa "Sem período comum com nenhum candidato desta varredura" em CRCL e "1 candidato com período comum curto (PENGU/USDT)" em SPY, QQQ e BTC/USDT;
  - SPY: "Calculando contra SPY: k de 5 candidatos…" (células "Calculando…", sem número) e depois "Contra SPY" nos 5: BTC/USDT +66.8 p.p. (02/01/2019 – 31/12/2024, "USDT tratado como USD"), NVDA +49.8, SOL/USDT +81.2 (com o aviso), SPY −3.2 e PENGU/USDT "Sem comparação · Período comum de 14 dias: o mínimo é 30."; a ordem 1–4 e "—" fica igual, embora a coluna não esteja em ordem;
  - QQQ: "Coletando histórico de QQQ na Binance…", depois o cálculo e a coluna; BTC/USDT como referência: o aviso de moeda passa para NVDA e SPY; CRCL: "Sem comparação · Sem período comum com CRCL." nos 5 e o resumo "Nenhum candidato tem período comum com CRCL…";
  - recarregar mantém a coluna gravada; "Próprio ativo" tira a coluna;
  - Demonstração: prévia da planilha com Rank global, Candidato e os 22 campos (PENGU/USDT com "Histórico insuficiente: Período comum de 14 dias: o mínimo é 30.") e, com referência extra, as 13 colunas "(extra)"; Legenda com "Retornos do ranking" e "(extra)"; "Simular falha na coleta de QQQ" (alerta, nada gravado, "Tentar de novo"); nota "Recarregar".
- **Apoio:** `live.css` (CSS vivo inteiro), `delta.css`, `delta.js`. O diálogo e o JSON de dados do protótipo ficam no fim do `body`, cada um num par `DELTA`. Nenhuma página é painel ANTES/DEPOIS nem "N estados"; cada Demonstração fica no fim, no fluxo. O gráfico de velas do clone fica vazio (é `canvas` na página viva e não entra no HTML capturado).

## Prototype Validation

Evidência do rework r3 (28/10/2026), que substitui a do r2. Qualquer mudança posterior nos arquivos abaixo a invalida. Scripts no scratchpad da sessão: `/tmp/claude-1001/-srv-apps-dev-criptofarol-source/9da083da-1d07-4a6e-9eb6-dddd4afcad74/scratchpad/c1123r3/`.

- **Captura viva:**
  - Playwright Python, Chromium headless shell 1243, `pt-BR`, tema escuro, fuso `America/Sao_Paulo`, API simulada, a 1440 e a 390 px; origem `https://dev.criptofarol.com.br`, bundle `index-C9_PkDmo.js` / `index-DOHmvARO.css` (o mesmo do r1, conferido no r3);
  - `/combo/results` (BTC/USDT rodada nova; NVDA aberto de Favoritos) e `/favorites`: captura do r1, sem mudança;
  - `/combo/discovery` no Decidir: **recapturado no r3** (`python3 -E -P capture.py cap discovery`), com a varredura `#c1123mix` de 5 candidatos (01/01/2019 – 31/12/2024) e "Ordenar por" = "CAGR vs B&H" escolhido na página viva;
  - toda região COPIED das quatro páginas é substring literal de uma captura (0 fora), e nenhum marcador cai dentro de tag; `live.css` = `index-DOHmvARO.css` inteiro.
- **Montagem:** `python3 -E -P build.py cap out` (o `build.py` do r2 com o Decidir novo em `disc.py`; `delta.css` e `delta.js` editados, com o diálogo extraído para uma função usada pelo resultado, pelo favorito e pelo Decidir). `index.html`, `favorite.html`, `favorites.html` e `live.css` saem byte a byte iguais aos do r2.
- **Arquivos** (bytes do arquivo; COPIED e DELTA sem os marcadores):

  | Arquivo | Bytes | sha256 | COPIED | DELTA |
  |---|---|---|---|---|
  | `index.html` (canônico) | 75.836 | `7a1dd22a9b45c4581b650a9146d831a3edb8b93b3d92023ea30c388107ef132f` | 7 pares, 56.200 B | 8 pares, 18.212 B |
  | `favorite.html` | 67.991 | `9ec8f65d63db69d326d9cc2068ed3b0cb9dfeb957fab79f909e212681cbe66ec` | 7 pares, 51.863 B | 8 pares, 14.682 B |
  | `favorites.html` | 96.707 | `843406787f1c3bc0fd4491234490770592a01e6a1ef1613dbf7960cb0a097b33` | 10 pares, 88.959 B | 10 pares, 5.991 B |
  | `discovery.html` | 75.122 | `6c2af663c4af51bca907621dc455c1ec4cf9134e24cf5f97d65b5a3ea87de740` | 13 pares, 47.504 B | 14 pares, 25.407 B |
  | `live.css` | 254.138 | `353ac045db2df0a13512af6bc3268d64eb4ad256a821969eb7c8118b1ba832f6` | clone inteiro | — |
  | `delta.css` | 16.483 | `ad738de29c63c802af3e3175cec83e8edbfe440f83ef8d17d92de17e1d5d0c3a` | — | delta |
  | `delta.js` | 23.811 | `8578c21f1c52f7610eecfc27f35c6d0542b02444cb2c04ee8aa9bf160e0b171c` | — | delta |

  Em `discovery.html`, o cabeçalho "Contra …" e as 5 células da coluna extra são pares `DELTA` próprios dentro da tabela COPIED (por isso 13 pares COPIED); a faixa "Coluna extra", o diálogo e o JSON de dados também ficam em `DELTA`.
- **URL pública** (`python3 -E -P serve_check.py <pasta do protótipo> cap`): os 7 arquivos respondem 200 em `https://dev.criptofarol.com.br/prototypes/card-1123-benchmark-exportacao/`, sha256 servido = disco nos 7, e a pasta `/` serve o `index.html`.
- **Gate do clone** (`python3 -E -P clonegate.py <repo>`, `scripts/process-fsm/design_clone_gate.py`, catálogo do HEAD): linhas 1–3 = `UI impact: affected` / `live_route: /combo/results` / `surface: existing`; `design_token_gap` = None; `evaluate_clone_gate` = True; `clone_gate_ok` = True; `classify(index.html, /combo/results)` = PASS, `copied_utf8_sum` 56.249 B. Informativo: `favorite.html` PASS (51.912), `favorites.html` PASS (89.029), `discovery.html` BLOCKED no catálogo (47.595), que pede marcos do Montar e não do Decidir (o mesmo do r2; o gate só lê o canônico).
- **Browser gate na URL pública** (`python3 -E -P gate.py`, saída em `gate.out`):
  - Playwright Python, Chromium headless shell 1243, contexto novo por largura: 1440×900 (desktop) e 390×844 (`isMobile`, `hasTouch`, toque), `pt-BR`, tema escuro, fuso São Paulo;
  - resultado: **348/348 asserts PASS**, 0 `pageerror`, 0 `console.error`, 0 resposta ≥ 400, sem rolagem horizontal em nenhuma página;
  - a suíte do r2 segue inteira; no Decidir, os asserts do r2 foram mantidos com os dados da varredura nova (5 linhas com o próprio ativo, Período pedido "01/01/2019 – 31/12/2024", CAGR gravado +82.00%, +65.00%, +95.00%, +12.00% e vazio no PENGU/USDT, Situação "Válida" nos 4 e "Histórico insuficiente: Período comum de 14 dias: o mínimo é 30." no PENGU/USDT);
  - novos do Decidir, nas duas larguras:
    - faixa, cabeçalho, as 5 células e o diálogo dentro de `DELTA`;
    - padrão "Nenhuma", coluna oculta, botão ≥ 44 px;
    - diálogo: foco na busca ao abrir, "Próprio ativo · Padrão" marcado, Tab e Shift+Tab presos, filtros de classe ≥ 44 px a 390 (≥ 36 a 1440), Cripto lista BTC/USDT e WAVES/USDT, WAVES/USDT `disabled` com motivo ligado e clique sem efeito, aviso em CRCL e nota de período curto em SPY antes da escolha, Esc fecha e devolve o foco ao gatilho;
    - SPY: "Calculando contra SPY" com nenhum número nas células em cálculo; depois "Contra SPY" no cabeçalho e no rótulo das 5 células; ordem e rank global iguais aos de antes (1 BTC/USDT, 2 NVDA, 3 SOL/USDT, 4 SPY, — PENGU/USDT); "Ordenar por" segue com 2 opções; BTC/USDT "+66.8 p.p.", "SPY +15.25% a.a.", "02/01/2019 – 31/12/2024"; aviso "USDT tratado como USD" só em BTC/USDT e SOL/USDT (e na faixa); PENGU/USDT `short_overlap` com "Sem comparação" e "Período comum de 14 dias: o mínimo é 30.", sem "%", "p.p." nem "0,00"; faixa com "Retorno de preço, sem dividendos", "não muda a ordem", "4 de 5 candidatos com comparação" e linha de gravação;
    - planilha: Rank global, Candidato, os 22 campos e as 13 colunas "(extra)", na ordem; Referência = próprio ativo e Referência (extra) = "SPY · ETF · USD"; Situação (extra) "Válida" nos 4 e insuficiente no PENGU/USDT com células vazias; aviso de moeda (extra) no BTC/USDT; tipo de retorno (extra) no NVDA; status do download cita "colunas (extra) contra SPY";
    - recarregar: a coluna volta gravada ("done", sem cálculo), com os mesmos valores e a mesma ordem;
    - QQQ: "Coletando histórico de QQQ na Binance" sem números, depois NVDA "+43.0 p.p." e a ordem igual;
    - CRCL: `no_overlap` e "Sem comparação" nos 5, sem "%" nem "p.p.", resumo "Nenhum candidato tem período comum com CRCL" e motivo na planilha;
    - falha na coleta: alerta com "Nada foi gravado" e "continua contra CRCL", "Tentar de novo" ≥ 44 px, coluna anterior mantida, e "Tentar de novo" grava QQQ;
    - "Próprio ativo": coluna e cabeçalho somem, a planilha volta aos 22 campos, a ordem segue igual, e recarregar continua sem coluna.
- **Detector Impeccable CLI** (`node .agents/skills/impeccable/scripts/detect.mjs --json` em cada um dos 4 HTML, `delta.css` e `delta.js`): 0 achados em `index.html`, `favorite.html`, `discovery.html`, `delta.css` e `delta.js`. Em `favorites.html` há só `flat-type-hierarchy` e `gray-on-color`, os mesmos do r1 e do r2, no corpo copiado (incumbente, P3). O hook de design segue apontando os literais do incumbente no `delta.css` (`11px`, `18px`, `#474d57`, sombra do modal; P3); o delta novo do Decidir usa só tamanhos da escala do DESIGN.md (12, 13, 14 e 16 px) e tokens do `:root` vivo.
- **Scripts** (`c1123r3/`):
  - captura: `capture.py` (mock do Decidir com 5 candidatos e período fixo), pasta `cap` (r1 + Decidir do r3);
  - montagem: `build.py`, `disc.py`, `clone.py`, `delta.css`, `delta.js`;
  - verificação: `gate.py` (browser gate, saída em `gate.out`), `clonegate.py`, `serve_check.py`, `vis3.py` (capturas de tela do Decidir em `vis/`).
- **`openspec validate card-1123-benchmark-exportacao --strict`:** "Change 'card-1123-benchmark-exportacao' is valid".

## Design Critique

Com-tela. Teto 1+1+1: autor, dupla A/B e 1 rework. O rework (r2) aplicou o P1, os P2 de produto e contrato e os P3 baratos da dupla. Depois da primeira submissão, Alan devolveu o card (T6) com uma decisão nova de escopo, a coluna extra na Descoberta. Ela justificou o segundo rework (r3) e uma nova onda A/B (`recriticar`, T4); ver "Segunda rodada" abaixo. Não houve terceiro rework.

### Primeira rodada (até a primeira submissão)

- Autor: `design-autor 1123 r1` (isolado). Rework: `design-autor 1123 r2` (isolado).
- Assessment A: `assessment-a 1123 r1` (isolado; produto, UX, acessibilidade, fidelidade). Assessment B: `assessment-b 1123 r1` (isolado; detector + navegador). Mesma onda (`model_selection_wave_capture` do A).
- Verdict: **PASS** (A: PASS com rework; B: PASS com rework leve; os dois aplicados no r2). Browser gate do r2: 246/246 na URL pública a 1440×900 e 390×844 (toque), sem erro de console. Gate do clone: `clone_gate_ok` True, `classify(index.html, /combo/results)` PASS. Tokens: `UI impact: affected` / `live_route: /combo/results` / `surface: existing`.
- Proto canônico: https://dev.criptofarol.com.br/prototypes/card-1123-benchmark-exportacao/ (clone de `/combo/results`). Páginas extras com texto visível alterado: `favorite.html`, `favorites.html`, `discovery.html`.
- Snapshots: `.impeccable/critique/1123-card-1123-benchmark-exportacao-A.md` e `…-B.md`. O Gist OpenSpec não é a crítica.

- **P0**: nenhum.
- **P1, corrigido no r2** (A P1-1 / B P2-2): a prévia da planilha do ranking da Descoberta tinha 14–16 dos 22 campos de contexto e não dizia "Retorno de preço, sem dividendos" em NVDA e SPY. Agora traz os 22 campos com os nomes e a ordem do spec, como Favoritos e Trades.
- **P2 de produto e contrato, corrigidos no r2**:
  - período comum abaixo do mínimo demonstrado na tela (PENGU/USDT, "Período comum de 14 dias: o mínimo é 30.", com frase de apoio própria), marcado como proposta à espera de Alan;
  - seletor com ativo desabilitado e o motivo do catálogo (WAVES/USDT) e aviso antes da escolha ("Sem período comum com esta estratégia", "Só 14 dias em comum com esta estratégia");
  - tag "Ref.: BTC/USDT" na linha e no cartão do SPY Trend em Favoritos;
  - "Refeita só quando o backtest do favorito é atualizado, com a mesma referência." no favorito;
  - Legenda de Favoritos com "Tela × planilha" (a tela mostra a convenção da classe; a planilha, só o que foi gravado);
  - filtros de classe do seletor com 44 px no toque.
- **P3 baratos, corrigidos no r2**: subtítulo "÷ 365,25"; diálogo e JSON de dados em pares `DELTA`; nenhum número da referência nova no DOM durante gravando/coletando; `max-width: 65ch` nos textos longos.
- **P3 aceitos, para o Apply**: live regions aninhadas no alerta de falha; cabeçalho "Referência" durante a coleta e no favorito sem comparação; versão da amostra da Descoberta só com o `snapshot_id` no mock; tipo de retorno vazio no caso insuficiente da planilha; dados de exemplo de NVDA com datas diferentes entre páginas; sem tela própria para ETF contra o próprio ativo e para short (cobertos pelo E2E de `tasks.md`); "Promover"/"Excluir" cortados no Decidir a 1440 (região COPIED, defeito que já existe); retorno derivado da prévia da Descoberta diferente do "+300%" COPIED do mock; achados do detector em regiões COPIED do incumbente (`gray-on-color`, `flat-type-hierarchy`, `ai-color-palette`, `side-tab` em `live.css`/`favorites.html`) e o `font-size` 11px da região COPIED "Dados e execução" (hook `design-system-font-size`, herdado); `discovery.html` BLOCKED no catálogo (informativo; o gate lê o canônico).
- **Decisão aberta para Alan na Aprovação de Design:** mínimo do período comum. O Design propõe 30 dias corridos (ver Open Questions); trocar o número muda só o N do texto e o limite do estado de período curto.
### Segunda rodada (decisão de Alan de 28/10: coluna extra na Descoberta)

- Decisão: [comentário](https://github.com/oalansilva/crypto/issues/1123#issuecomment-6462139347). No Decidir, uma referência escolhida dá uma coluna extra por candidato; a ordem, o rank global e a elegibilidade não mudam.
- Rework: `design-autor 1123 r3` (isolado), segundo rework, justificado pela mudança de escopo de Alan (não por achado de crítica). Mudou `discovery.html`, `delta.js`, `delta.css` e o OpenSpec (decisões 1, 4, 7, 8 e 10 nova; specs `discovery-leaderboard`, `benchmark-reference-choice`, `result-context-export`; tasks 4A, 6.2a–c e 7.3a). `index.html`, `favorite.html`, `favorites.html` e `live.css` ficaram byte a byte iguais ao r2 (conferido pelo B).
- Assessment A: `assessment-a 1123 r2`. Assessment B: `assessment-b 1123 r2`. Mesma onda, isolados.
- Verdict: **PASS** (A: PASS com rework, sem P0/P1; B: PASS, sem P0/P1/P2). Browser gate do r3: 348/348 na URL pública a 1440×900 e 390×844 (toque); B reexecutou com 197/197 próprios. Zero erro de console, de página e resposta ≥ 400; sem rolagem horizontal. Gate do clone: `clone_gate_ok` True, `classify(index.html, /combo/results)` PASS; as 13 regiões COPIED do `discovery.html` novo são trechos literais da captura do r3. Tokens inalterados.
- Snapshots: `.impeccable/critique/1123-card-1123-benchmark-exportacao-A-r2.md` e `…-B-r2.md`.
- **Decisão de Alan na crítica (28/10/2026), amostra vencida:** numa varredura em que a amostra do candidato já venceu (mais de 30 dias), a célula fica "Sem comparação · Amostra do candidato vencida", **com aviso**. O seletor avisa antes da escolha e sugere rodar a varredura de novo. Escolher uma referência guarda as amostras da varredura enquanto a coluna existir. Não há cálculo com dado novo nem retenção maior.
- **P0 / P1**: nenhum.
- **P2 residuais, para o Apply** (teto atingido; não há terceiro rework, e as correções são de texto e contrato, sem mudar escopo). O Apply segue estas instruções como parte do Design aprovado:
  - **amostra vencida visível** (A, junto da decisão de Alan): na faixa padrão, a frase "Escolher uma referência guarda as amostras desta varredura enquanto a coluna existir."; na linha do candidato, "amostra guardada pela coluna extra" no lugar da data de vencimento quando a coluna estiver ativa; no seletor, aviso contado antes da escolha ("N candidatos com amostra vencida"; quando forem todos, alerta com "Rode a varredura de novo"); no resumo da faixa, contagem "(amostra vencida)"; spec e E2E com o estado "Amostra do candidato vencida";
  - **coluna não parece a chave da ordem** (A): a dica do cabeçalho passa a "Δ CAGR · período comum · não ordena";
  - **promover com a coluna ativa** (A): o favorito promovido herda a comparação gravada da célula (mesma referência, mesma amostra, sem recálculo), e a promoção diz isso ("Leva a comparação com SPY gravada"). Candidato "Sem comparação" é promovido com a referência padrão (próprio ativo). Spec `discovery-leaderboard`/`benchmark-reference-choice` e tasks ganham o cenário no Apply;
  - **formato pt-BR na célula** (A): "+66,8 p.p.", "+15,25% a.a." e "2 jan. 2019", como o resto do Decidir; o cenário do spec segue esse formato.
- **P3 aceitos, para o Apply**: motivo de "Sem comparação" com `white-space: normal` (hoje herda `nowrap` e invade a coluna "Ação" no PENGU) e `max-width: 65ch` na faixa (B P3-1, P3-3); reescolher uma referência já gravada reativa a gravada sem recalcular, e os estados "Sem amostra" e "Amostra do candidato vencida" entram no E2E 6.3/7.3a (B P3-4); valores (extra) saem dos trades, não do mock (B P3-5, A); cancelar o cálculo anterior ao trocar de referência no meio (B P3-6); "4 de 5" diz se conta a varredura ou o recorte filtrado; Legenda "(extra)" explica por que o retorno do próprio ativo e o (extra) diferem na mesma linha; tom de queda com o token do componente vivo; estados de exportar durante o cálculo e de falha no cálculo; herdados do vivo (`th-hint` de 10 px, contraste 4,01:1 do cabeçalho, 4,48:1 do vermelho, "Promover" cortado a 1440, `Buy &amp;amp; Hold` escapado no título do Leaderboard, que pede card próprio); alerta de falha dentro de `role=status` (já aceito).

### Decisões abertas e disposition

- **Decisão aberta para Alan na Aprovação de Design:** mínimo do período comum. O Design propõe 30 dias corridos (ver Open Questions); vale para o resultado, o favorito, a coluna do Decidir e os campos de contexto da planilha da Descoberta. Trocar o número muda só o N do texto e o limite do estado de período curto.
- **Disposition:** o delta visível fica no resultado (`/combo/results`): seção "Comparação com referência" com troca depois de rodar, gravada, janela comum, aviso de USDT tratado como USD, retorno de preço, histórico insuficiente e período curto com motivo; o favorito aberto mostra a referência gravada; Favoritos ganha a tag "Ref." e a planilha com contexto completo; a Descoberta ganha "Exportar planilha" e a coluna extra "Contra <referência>", gravada por varredura e usuário, com o ranking, o rank global e a elegibilidade no próprio ativo. Sem fonte externa nova, sem conversão de câmbio e sem dividendos.

### Proxies

- `design.md` words: 7516 (antes desta seção)
- HTML generated vs copied (`index.html`): 19636 vs 56200
- Spawns: 7 (design-autor r1, assessment-a r1, assessment-b r1, design-autor r2, design-autor r3, assessment-a r2, assessment-b r2)
