UI impact: affected
live_route: /favorites
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card [#1120](https://github.com/oalansilva/crypto/issues/1120), quarta história do épico [#1116](https://github.com/oalansilva/crypto/issues/1116). O briefing é o issue grelhado (fronteira vazia), com as 5 decisões de Alan de 24/10/2026 dentro de Entra. Não houve reentrevista. Depois da crítica A/B, Alan decidiu mais um ponto em 24/10/2026 (comentário "Decisões de Alan no Design" no issue): lote pausado bloqueia um lote novo (decisão 16). Este é o pacote do rework r1. O *como* abaixo foi conferido em `develop` @ e762e470 (pós-#1119); #1117, #1118 e #1119 estão em `develop` e os seus OpenSpec (`openspec/changes/card-1117-catalogo-ativos`, `card-1118-historico-binance`, `card-1119-backtest-acoes-etfs`) são os contratos reutilizados. O #1122 ainda não foi entregue: o contrato com ele está na decisão 12.

Estado atual, conferido no código:

- **Quem roda o lote.** `ComboConfigurePage.tsx:358-391` (Combo) e `ComboOptimizePage.tsx:225-262` (Otimização) chamam `POST /api/combos/backtest/batch` quando sobra mais de 1 ativo; com 1 ativo vão pelo `POST /api/combos/optimize` com `run_scope: "single"` (#1119). A Otimização manda sempre `OPTIMIZE_FIXED_WINDOW` (1 a 31 jan. 2024) e não manda direção nem período. O Combo tem 1m, 5m, 15m, 1h, 4h e 1d (`ComboConfigurePage.tsx:536-541`); a Otimização tem também 30m.
- **Recusa por classe no lote.** `combo_routes.py:891-922`: `_ensure_crypto_symbols` (→ `refusal_for_symbols` sem `single_scope`, `asset_analysis_guard.py:105-150`) e `_ensure_crypto_data_source`, que só aceita CCXT. No front, `planRun` (`assetSelection.ts`, bloco "Plano por classe") tira ação/ETF de qualquer seleção com cripto ou com mais de uma ação/ETF, com `EQUITY_REASON` (`assetSelection.ts:120`) "… o lote vem depois". A captura viva da seleção mista diz "Roda 1 par cripto (BTC/USDT): otimiza, salva em favoritos e abre a página de favoritos. Fora: NVDA (Ação), SPY (ETF) — …"; 1m e 5m ficam escolhíveis sem marca.
- **O lote hoje.** `batch_backtest_service.py:105-362`: para cada símbolo, pula "unsupported", pula se já há favorito com mesma estratégia, símbolo, tempo, período e direção (`:161-203`), roda `ComboOptimizer.run_optimization` com `resolve_data_source_for_symbol`, pula com motivo o NO-GO do walk-forward (`:255-283`) e grava o favorito direto (`FavoriteStrategy`, nota "gerado em lote (<id8>)", `tier=3`, `:294-341`), sem passar pela recusa de favorito de ação/ETF do #1119 (`routes/favorites.py:58-90`). Erro vira `failed` + `errors[]`.
- **Estado do lote.** `batch_backtest_store.py`: um dicionário por lote no Redis (`setex` com `async_job_ttl_seconds`) ou em memória; só contadores (`processed`, `succeeded`, `failed`, `skipped`), `current_symbol` e `errors`. Não há estado por ativo nem retomada: `pause` e `cancel` (`batch_backtest_service.py:52-102`) valem antes do próximo símbolo e "paused" é final para o front (`useBatchJob.ts:19`). O id do lote vive só no estado do React; sair da página perde o painel.
- **Painel.** `BatchProgressPanel.tsx`: "N de M ativos", ativo atual, tempo, Pausar e Encerrar; no fim "X sucesso, Y falha, Z ignorado(s)", erros num `<details>` e o link "Abrir Strategy Favorites" para `/favorites` (sem filtro do lote).
- **Mesma amostra.** `combo_optimizer.py:2093-2152`: `run_optimization` congela candles (`_begin_sample`, `:2154`) e 15m (`_freeze_intraday`/`_freeze_equity_intraday`, `:2179-2222`) numa `ExecutionSample`; ação/ETF sempre, cripto com `MARKET_HISTORY_UNIFIED`. O backtest de 1 ação/ETF coleta antes com `prepare_equity_history` (`equity_backtest.py:241-315`) e otimiza com `BinanceEquityMarketDataProvider(ensure=False)` (`combo_routes.py:798-813`).
- **Favoritos.** `FavoritesDashboard.tsx:95` (`isCryptoPair`) e `:1034` (`matchesCryptoOnly`) escondem tudo que não tem `/`; filtros Symbol, Strategy, Time, Direção e Ordenar (Ret/T %, Return, Sharpe, Trades, `:959-1052`); célula do símbolo com base e cotação (`<small>USDT</small>`); célula da estratégia com título, descrição, apelido e estado da atualização diária (`formatRefreshStatus`, `:1155-1183`); coluna Período ("Todo") some na largura de 1440 px. O spec `favorites-asset-type-filter` exige só cripto.
- **Coleta sob demanda (#1118).** `HistoryService.ensure` com lock e limite; `prepare_equity_history` devolve a nota de janela parcial ou levanta `history_unavailable`. A cobertura por série está no catálogo (`asset.history.timeframes`), lida pelo seletor.

**Audience:** Alan, que monta um universo misto, roda a mesma estratégia em todos e compara o que saiu.
**Outcome:** lote misto que diz antes quanto vai coletar, mostra cada ativo, pode parar e voltar, e entrega uma lista única em Favoritos onde USD e USDT, precisão e convenções estão à vista.
**Direction:** clone+delta Operate de `/favorites`, `/combo/configure` e `/combo/optimize`. Tokens do produto, sem mundo visual novo.
**Scope:** lote do Combo e da Otimização, Favoritos (lista e filtro), texto da recusa na Descoberta. Fora: Descoberta com ação/ETF, atualização e alertas de favoritos de ação/ETF, Monitor, exportação, benchmark, ordens.

Regiões clonadas da página viva, só estas (capturadas em `https://dev.criptofarol.com.br`, bundle `index-BvxVmoZs.js` / `index-B4ZdBYXJ.css`, com a API simulada, a 1440 e a 390 px, marcadas com `COPIED:start`/`COPIED:end`):

- `index.html` (canônico, `/favorites`, 5 favoritos): fundo; AppNav desktop; AppNav móvel; conteúdo vivo (Como usar Favoritos, cabeçalho "Estratégias favoritas" com estrelas e filtro por estrela, filtros, busca, Exportar e Nova estratégia, cartões móveis, tabela `table.fav-strategies` com estrelas, Telegram, métricas e ações, rodapé). Os favoritos ADA/USDT e XRP/USDT da captura (mesmas estrelas e posição) viram NVDA e SPY só nas células que mudam.
- `configure.html` (extra, `/combo/configure`, BTC/USDT + NVDA + SPY): fundo; AppNav desktop e móvel; conteúdo vivo (Template Information, Configuration com o seletor do #1117/#1118, Timeframe, Período, Direction, Deep Backtest, walk-forward, Parameter Optimization Ranges, Otimizar, Ver logs).
- `optimize.html` (extra, `/combo/optimize`, BTC/USDT + NVDA + SPY, 1d): fundo; AppNav desktop e móvel; conteúdo vivo (Configuration com template, seletor, Timeframe, período fixo, Parameter Ranges, Run Optimization, painel "Ready to Optimize").
- `live.css`: o CSS vivo inteiro (`index-B4ZdBYXJ.css` do DEV), sem poda.

O delta fica só nos blocos `DELTA:start`/`DELTA:end`: filtro Classe e Symbol multiclasse, faixa do lote, contagem e rodapé com o filtro, resumo e filtro por estrelas só com cripto (e a nota de ação/ETF fora do Monitor), e por favorito o atributo de filtro/ordem, a célula do símbolo (classe e moeda), a célula da estratégia (precisão, convenções, período efetivo, "Limitações e origem"), o período efetivo e o ATR na moeda; em ação/ETF, as estrelas, o Telegram e o Revalidar desabilitados; no Combo e na Otimização, o texto da classe, o texto "coletado ao rodar o backtest ou o lote", os tempos "(só cripto)", o texto antes de rodar, o "Confirmar lote" e o painel do lote; no Combo, o campo Market Data e o valor do Período da captura; na Otimização, o template da captura e o lote na coluna larga; e o painel "Demonstração" no fim de cada página. Selects que o React preenche por propriedade (`value`) saem da captura sem `selected`: o Período ("Todo o histórico", como diz o aviso vivo "Será usado todo o histórico disponível") e o template (`multi_ma_crossover`, com os Parameter Ranges dele à vista) voltam ao valor capturado em blocos DELTA.

## Goals / Non-Goals

**Goals:**

- Lote com cripto, ação e ETF juntos, cada ativo pelo caminho do backtest individual do #1119.
- Ação e ETF fora com motivo antes de começar quando o tempo não serve; criptos rodam.
- Qualquer tamanho de lote, com a contagem de coleta antes de confirmar.
- Coleta e otimização ativo por ativo, com estado por ativo e motivo; problema de um ativo não para os outros nem vira resultado válido.
- Precisão diária marcada no lote e no favorito, com o trecho.
- Mesma amostra para todas as tentativas de um ativo; pausa, retomada e encerramento no mesmo lote, sem perder o que terminou.
- Favorito gravado pelo lote para ação e ETF como para cripto, com identidade e convenções.
- Favoritos como lista única ordenável com classe, moeda e convenções por linha e filtro por classe.

**Non-Goals:**

- Descoberta com ação/ETF (#1121): continua recusando; só o porquê troca (decisão 13).
- Atualização diária, período operacional, alertas, Telegram e Monitor de favoritos de ação/ETF; chave de unicidade com fonte, sessão e ajuste (#1122).
- Favoritar ação/ETF pela tela do resultado: segue recusado (#1119, decisão 15) até o #1122.
- Benchmark e exportação com as convenções novas (#1123).
- Seletor de período na Otimização (segue fixo em jan. 2024, como no #1119).
- Geração de estratégias, ordens, carteira.

## Decisions

1. **Página primária = `/favorites`; extras `/combo/configure` e `/combo/optimize`.** O resultado do lote só fica consultável em Favoritos (fato do issue) e quatro critérios do Entra moram lá (lista única, classe, moeda, convenções, filtro por classe, precisão e período efetivo da Verificação). `/favorites` está no catálogo do gate (`table.fav-strategies`, "Estratégias favoritas", "Symbol", "Estratégia", "Ações"). O Combo e a Otimização têm o delta do lote (aceite, fora com motivo, confirmar, coleta, estado por ativo, pausa) e ganham clone extra; não estão no catálogo, então são extras sem gate próprio. Nenhum arquivo é painel de estados. Alternativa rejeitada: lista de comparação nova no fim do lote, porque duplicaria Favoritos e sumiria ao sair da página.

2. **Seleção com mais de 1 ativo é sempre lote.** Hoje, se só 1 sobra (ex.: BTC/USDT com NVDA e SPY fora), o Combo roda o caminho de 1 ativo e abre Favoritos. Agora vai como lote, para que NVDA e SPY apareçam como "Fora" com o motivo no estado por ativo, como pede a Verificação. 1 ativo selecionado segue o caminho do #1119 (1 ação/ETF abre o resultado, sem salvar).

3. **Aceite por classe no servidor.** `refusal_for_symbols` ganha o escopo `batch`: ação e ETF passam; ativo marcado ou fora do catálogo segue recusado (`new_analysis=True`). `_ensure_crypto_data_source` sai do lote; a fonte é decidida por ativo (`binance_equity` para ação/ETF, a do pedido para cripto). `POST /backtest/batch` só devolve 422 quando nada roda, com o motivo de cada ativo.

4. **Plano do lote = `POST /api/combos/backtest/batch/preview`.** Recebe o mesmo corpo do lote e devolve, por ativo, `{symbol, asset_class, currency, plan: run|out, reason, needs_collection: [séries], covered_until}` e os totais por classe. Regras de "fora": ação/ETF com tempo fora de 15m, 1h, 4h e 1d (`timeframe_refusal` do #1119); na Otimização, ação/ETF em 15m, 1h ou 4h cuja cobertura do 5m no catálogo começa depois do fim da janela fixa (mesma regra do aviso de 1 ativo do #1119, agora por ativo), com o motivo "o 5m de NVDA começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo" (rework: crítica A P1-2 e B P2-1); ativo marcado. **`needs_collection` (definição do rework, crítica B P2-2):** uma série precisa de coleta quando, dentro da janela pedida, a Binance tem candles que ainda não estão guardados (ativo sob demanda, lacuna ou o trecho desde a última coleta). O que a Binance não tem não conta: a janela pedida maior que a série da Binance não gera coleta. As séries olhadas são a do tempo gráfico e, com intrabar, o 5m. Um ativo "sem lacunas · atualizado" no seletor não conta (NVDA). SPY, sob demanda, conta com 1d e 5m no Combo e só com 1d na Otimização, porque a Binance não tem 5m de SPY em jan. 2024. O preview devolve também `collect_kind` ∈ `none`, `missing`, `tail`, que dá o detalhe do lote grande ("2.351 sem histórico guardado e 37 só com o trecho desde a última coleta"). Nada é coletado no preview. O lote recalcula o plano ao começar (a cobertura pode ter mudado) e grava o plano no lote.

5. **Confirmar lote no fluxo, sem modal.** O botão de rodar com mais de 1 ativo chama o preview e abre um painel abaixo dele (`aria-labelledby`, foco no título), com: "Vão rodar" (total, por classe e moeda, nomes até 3 + "e mais N"), "Precisam de coleta de histórico" (N de M e de quê, em faixa azul), "Ficam fora" (nomes e motivo, em âmbar), "Configuração" e "Favoritos" ("o melhor de cada ativo, com a nota 'gerado em lote'; ativo que já tem favorito no mesmo período e direção é pulado"). "Confirmar e rodar" (amarelo) começa; "Voltar" fecha e devolve o foco ao botão de rodar. Qualquer tamanho é aceito, sem limite nem segunda confirmação (decisão de Alan). A contagem segue a decisão 4 e diz quem não conta: "1 de 3 — SPY (1d e 5m do intrabar). BTC/USDT e NVDA já estão guardados, sem lacunas e atualizados. Conta só o que a Binance tem para a janela e ainda não está guardado." Lote grande: "2.388 de 2.431 — 2.351 sem histórico guardado (1d e 5m do intrabar) e 37 só com o trecho desde a última coleta. Os outros 43 já estão guardados, sem lacunas e atualizados." "Configuração" usa o template, o tempo e o período escolhidos: no Combo, o select Período; na Otimização, a janela fixa. Ela nunca diz "1d" quando o tempo é outro. Na Otimização, o Confirmar e o painel do lote ocupam a coluna larga, no lugar de "Ready to Optimize", que volta quando não há lote. O texto antes de rodar fica sob Run Optimization (crítica A P2 e B P2-4). Alternativa rejeitada: modal, porque a tarefa não precisa de foco protegido e o texto antes de rodar já está ao lado.

6. **Texto visível (contrato).**
   - Nota da classe no seletor — Combo: "Cripto, ação e ETF rodam juntos no lote: cada ativo usa a sua fonte, sessão, ajuste e moeda, e o melhor resultado de cada um vira favorito. Ação e ETF não rodam em 1m e 5m: nesses tempos ficam fora com o motivo. 1 ação ou ETF sozinha abre o resultado, sem salvar." Otimização: "Cripto, ação e ETF rodam juntos no lote, no período fixo desta tela: cada ativo usa a sua fonte, sessão, ajuste e moeda, e o melhor resultado de cada um vira favorito. Ação e ETF não rodam em 1m, 5m e 30m, nem em 15m, 1h e 4h quando o 5m deles não cobre o período fixo: ficam fora com o motivo; use 1d aqui ou o Combo, que tem período. 1 ação ou ETF sozinha mostra o resultado ao lado."
   - Sob demanda no seletor (Combo e Otimização): "Histórico sob demanda · coletado ao rodar o backtest ou o lote". Isso vale para toda linha sob demanda, inclusive a cripto (SOL/USDT), que perde o texto antigo "coletado quando uma análise pedir".
   - Market Data no Combo com seleção mista: "Por ativo: CCXT (cripto) · Binance Ações (ação e ETF)". O campo segue a decisão 3 (cada ativo com a sua fonte). Seleção só de cripto mantém "CCXT (crypto exchange data)" (crítica B P2-3).
   - Tempos: com ação ou ETF e cripto na seleção, "1 minute (só cripto)" e "5 minutes (só cripto)" (Otimização: "1m/5m/30m (só cripto)"), escolhíveis.
   - Antes de rodar: "Lote de 3 ativos (1 cripto, 1 ação, 1 ETF): otimiza cada um com esta configuração e grava o melhor de cada em favoritos (nota "gerado em lote"). Antes de começar, você confirma o lote." Com 1m ou 5m no Combo: "Lote de 3 ativos: roda 1 (BTC/USDT). Fora antes de começar: NVDA (Ação), SPY (ETF) — ação e ETF não rodam em <tempo>; para incluí-los, use 15m, 1h, 4h ou 1d." Na Otimização com 1m, 5m ou 30m, o conselho troca para "use 1d aqui ou o Combo, que tem período". Na Otimização com 15m, 1h ou 4h e o 5m fora da janela: "Lote de 3 ativos: roda 1 (BTC/USDT). Fora antes de começar: NVDA (Ação), SPY (ETF) — o 5m deles começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo, que tem período." O trecho de fora fica em âmbar. O mesmo motivo, com o tempo escolhido, aparece em "Ficam fora" e no estado "Fora" de cada ativo.
   - Só ações/ETFs em tempo que não serve: "Nada será executado: …" com o mesmo motivo (regra do #1119 para 1 ativo, estendida).
   - O texto "… o lote vem depois" sai do Combo e da Otimização.

7. **Coleta dentro do lote.** Para cada ativo, na ordem da seleção: (a) coleta — `prepare_equity_history` para ação/ETF (série do tempo e, com intrabar, o 5m), o carregador de hoje para cripto; (b) otimização com o provedor sem nova coleta (`ensure=False`, como no #1119); (c) gravação. `HistoryService.ensure` ganha um retorno de progresso (`on_progress(series, page, pages_total)`) que o lote grava no ativo ("5m do intrabar · página 7 de 20"); sem total conhecido, "página 7". Falha sem nada guardado → "Falha" com `history_unavailable_message`; parcial → segue, com a nota de janela coberta do #1119 no resultado. Coleta é sequencial (1 ativo por vez), respeitando o lock e o limite do #1118; não há coleta antecipada dos próximos.

8. **Estados por ativo.** `items[]` no lote, com `state` ∈ `queued`, `collecting`, `optimizing`, `success`, `success_daily`, `insufficient`, `rejected`, `failed`, `skipped`, `out`, `not_run`, mais `reason`, `progress`, `favorite_id`, `execution` (precisão, trecho, janela coberta), `snapshot_id`, `started_at`, `finished_at`. Rótulos: Na fila, Coletando histórico, Otimizando, Sucesso, Sucesso · precisão diária, Insuficiente, Rejeitado, Falha, Pulado, Fora, Não rodou. **Insuficiente** = a janela coberta tem menos candles do que a estratégia precisa para aquecer os indicadores (maior período + 1), ou a Binance não tem candles na janela (sem erro); **Rejeitado** = NO-GO/ERROR no walk-forward (regra de hoje); **Falha** = erro de coleta ou de execução; **Pulado** = já nos favoritos (regra de hoje); **Fora** = decidido no plano; **Não rodou** = lote encerrado antes. Só Sucesso e Sucesso · precisão diária gravam favorito. Ícone + texto em cada estado (nunca só cor).

9. **Painel do lote.** Substitui o `BatchProgressPanel`: título "Lote <id8>" com selo (Rodando, Pausando, Pausado, Encerrado, Concluído), "N de M ativos · tempo · resta ~X"; linha viva `role=status aria-live=polite` só com o ativo e a etapa em curso (não a lista inteira); barra de concluídos (`role=progressbar`); nota âmbar "Precisão diária em N ativos: …" quando houver; filtro por estado (botões com `aria-pressed` e contagem, só estados presentes); lista `<ol>` com Ativo (símbolo, chip da classe, moeda), Estado e Detalhe (motivo, progresso da coleta, ou "Favorito gravado · janela · precisão · abrir em Favoritos"); acima de 50 itens, "Mostrar mais 50". O painel tem `container-type: inline-size`: abaixo de 620 px de largura (celular e a coluna estreita da Otimização) cada ativo vira cartão. Resumo final: "Lote concluído: N de M em T · F favorito(s) gravado(s) (D com precisão diária) · sem resultado válido: X." e o link "Ver os F resultados do lote em Favoritos" (com 1: "Ver o resultado do lote em Favoritos"; `/favorites?lote=<id8>`); no Combo continua o link vivo "Descoberta sistemática (varredura)". O título do lote tem `tabindex="-1"` e recebe o foco ao começar e ao encerrar. Na Otimização o painel fica na coluna larga (decisão 5), então só no celular vira cartões.

10. **Pausar, Retomar, Encerrar e reabrir.** Pausa e encerramento são pedidos que o worker lê entre etapas: a etapa em curso (coleta ou otimização do ativo atual) termina, depois o lote para; enquanto isso, "Pausando…". Pausar e Encerrar ficam com `aria-disabled="true"` e continuam focáveis, e o foco fica em "Pausando…" em vez de cair no `<body>`. Ao pausar, o foco vai para Retomar. Pausado mostra Retomar e Encerrar; o ativo interrompido volta a "Na fila" com o que falta ("histórico coletado; otimiza ao retomar"). `POST /batch/{id}/resume` põe o mesmo lote na fila de novo; o worker pula itens finais e continua do próximo passo (coleta já guardada não é refeita, porque `ensure` só busca o que falta). Encerrar marca o resto "Não rodou" e mantém os favoritos. `GET /batch/active` devolve o lote não final mais recente do usuário; Combo e Otimização mostram o painel dele ao abrir. O estado do lote passa para PostgreSQL (tabelas `batch_backtest_jobs` e `batch_backtest_items`, migração do projeto), sem prazo enquanto pausado; Redis fica só como fila do Celery. Alternativa rejeitada: Redis com prazo maior, porque pausa longa ainda expiraria e o projeto pede PostgreSQL para estado de execução.

11. **Mesma amostra.** Cada ativo passa por `run_optimization`, que congela candles e 15m no começo (`_begin_sample`); no lote, a cripto também congela (o lote liga o caminho unificado por ativo, como a ação/ETF), para que toda tentativa leia a amostra e nenhuma volte à Binance. O `snapshot_id` vai para o item, para `favorite.metrics.data_provenance` e para o resultado. Retomar não reabre amostra de ativo concluído; ativo que ainda não otimizou congela a sua ao começar.

12. **Favorito de qualquer classe e contrato com o #1122.** O lote grava o favorito como hoje (`FavoriteStrategy`, nota "gerado em lote (<id8>)", sem sobrescrever; cripto com `tier=3`, ação/ETF sem nível, `tier` nulo, até o #1122), agora com `parameters.data_source` (`binance_equity` ou `ccxt`) e `metrics.asset`, `metrics.execution`, `metrics.conventions`, `metrics.data_provenance` (com `snapshot_id`) e `metrics.batch_id`. Contrato com o #1122: (a) o lote chama `favorite_uniqueness.lock_and_find_duplicate` e a checagem de "já nos favoritos" com `data_source` e `asset`; o #1122 estende a chave com fonte, sessão e ajuste sem mudar a assinatura do lote; (b) atualização diária, período operacional, alertas, Telegram, estrelas no Monitor e Revalidar de ação/ETF são do #1122; até ele chegar, a linha e o cartão de ação/ETF em Favoritos dizem "Atualização diária, Monitor, Telegram e Revalidar: ainda não para ações e ETFs" no lugar do estado de atualização. As estrelas, o botão Telegram e o "Revalidar" de ação/ETF ficam visíveis, sem estrela marcada, com `aria-disabled="true"`, focáveis e ligados a essa linha por `aria-describedby`; o clique não faz nada. O resumo por estrelas ("Acompanhar N", "Interesse alto N", "Top picks N") e o filtro por estrelas contam só cripto, e uma nota sob o resumo diz "Monitor, Telegram e Revalidar: ainda não para ações e ETFs. Os N favoritos de ação e ETF ficam fora destes níveis." O Monitor segue só cripto (crítica A P1-1); (c) a recusa de favoritar ação/ETF pela tela do resultado (#1119) continua até o #1122. O aceite do #1120 espera o #1122 (decisão de Alan).

13. **Recusa na Descoberta com porquê novo.** `EQUITY_REASON` deixa de valer para o lote; a Descoberta passa a usar "ação e ETF por enquanto rodam no Combo e na Otimização (1 ativo ou lote); a Descoberta vem depois" (`DISCOVERY_EQUITY_REASON`, `discovery_service`, `catalog_symbol_reason` no caminho da Descoberta e o texto do front da Descoberta). Aviso, lugar e comportamento ficam os do #1117; por isso não há clone da Descoberta (mesmo critério do #1119).

14. **Favoritos: lista única.** `matchesCryptoOnly` e os `isCryptoPair` dos filtros saem. `GET /api/favorites/` devolve `asset` (de `metrics.asset` ou, em favorito antigo, pelo catálogo; cripto pelo `/`). Delta visível:
    - Filtro **Classe** antes de Symbol: "Todas (N)", "Cripto (N)", "Ações (N)", "ETFs (N)"; a grade de filtros passa a 6 colunas a partir de 1100 px.
    - Célula do símbolo: em vez de só a cotação, "<chip da classe> · <moeda>" (chips nas cores do `.ap-fact.cls-*` vivo do seletor); USD e USDT nunca juntos na mesma linha; o ATR (coluna avançada) leva a moeda.
    - Célula da estratégia, depois do estado da atualização, à vista: precisão ("Precisão intrabar (15m)" azul com ícone de info, ou "Precisão diária · sem 15m de <início> a <fim>" âmbar com ícone de aviso), convenções em uma linha ("Binance Spot · 24/7 · 365 dias/ano" ou "Binance Ações · NY · split · 252/ano") e "Período efetivo <início> – <fim>" (a coluna Período some a 1440 px, então o período efetivo vai também para cá). Atrás de um `<details>` fechado ("Limitações e origem" em ação/ETF; "Origem" em cripto do lote) ficam as convenções completas ("Convenções: Binance Ações · pregão regular de Nova York · ajustado por split · 252 pregões/ano"), as limitações ("simulação com fração · taxa assumida · preços ajustados podem diferir do negociado"; "taxa assumida" só com `fee_confirmed=false`) e "Gerado em lote <id8> · <data>". Assim a linha de NVDA cai de ≈283 para ≈255 px a 1440 e o cartão de ≈685 para ≈640 px a 390. O resto da altura é da descrição e do apelido vivos (crítica A P2). Favorito antigo sem `execution`: "Precisão e período efetivo: aparecem na próxima atualização diária".
    - Nome acessível: as células símbolo e estratégia perdem o `aria-label` vivo (`fav.symbol` e título + apelido + descrição). O nome passa a vir do conteúdo, que já tem classe, moeda e precisão.
    - Os selects da faixa de filtros ganham `:focus-visible` com o anel do produto (`--accent-primary`), porque o vivo zera o `outline` e o "Mostrar todos os favoritos" devolve o foco ao Classe.
    - Coluna Período (quando visível): "Todo" + "efetivo <início> – <fim>".
    - Cartão móvel: "<chip> · <moeda>" sob o símbolo e o mesmo bloco de precisão, convenções, limitações, período efetivo e lote.
    - Faixa do lote com `?lote=<id8>`: "Mostrando só o lote <id8> (<data>): os favoritos gravados por ele, de todas as classes." + "Mostrar todos os favoritos" (44 px; limpa o filtro e devolve o foco ao filtro Classe).
    - Ordenar (Ret/T %, Return, Sharpe, Trades) vale para todas as classes juntas (métricas em %, sem moeda); "N filtradas" e o rodapé seguem os filtros. Sem soma nem conversão USD↔USDT.

15. **Regressão e demonstração.** Teste de contrato: lote misto aceito; lote só cripto igual ao de antes (mesma amostra, salvo o gap do #1119); ação no lote igual ao backtest de 1 ativo; 5m tira ação/ETF e roda cripto; Descoberta segue recusando; favorito de ação/ETF pela tela do resultado segue recusado. Demonstração no card: lote BTC/USDT + NVDA + SPY em 1d (favoritos consultáveis com período efetivo, precisão e limitações) e o mesmo em 5m (NVDA e SPY fora, BTC/USDT roda). E2E Playwright das três telas com a API simulada, seguindo o protótipo.

16. **Lote pausado bloqueia um lote novo (decisão de Alan, 24/10/2026).** Com um lote pausado do usuário, Otimizar (Combo) e Run Optimization (Otimização) não abrem o Confirmar de um lote novo. No lugar dele, o mesmo painel no fluxo mostra "Há um lote pausado", "Retome ou encerre o lote <id8> antes de começar outro. Encerrar mantém os N favoritos já gravados e marca o resto "Não rodou"." e os botões "Retomar o lote <id8>", "Encerrar o lote <id8>" e "Voltar". O foco vai para o título e o painel do lote pausado segue visível abaixo. Retomar e Encerrar agem sobre o lote pausado como os botões do painel; Voltar devolve o foco ao botão de rodar. Lote encerrado ou concluído não bloqueia. No servidor, `POST /backtest/batch` e `/backtest/batch/preview` devolvem 409 `batch_paused` com o id do lote pausado enquanto ele existir, e o front mostra o mesmo aviso. Assim `GET /batch/active` nunca tem dois candidatos. Lote rodando segue a regra de hoje (o botão não começa outro).

## Risks / Trade-offs

- [Lote grande coleta por horas (milhares de ações, 5m da Binance)] → contagem antes de confirmar, progresso por ativo, pausa e retomada duráveis; coleta sequencial com o limite do #1118, sem paralelismo novo. Estimativa de tempo só durante o lote (média dos concluídos), não antes.
- [Estado do lote sai do Redis para o PostgreSQL] → migração nova; lotes antigos no Redis terminam como estão (não migram); o front lê os dois formatos até o fim deles (`items` ausente = painel antigo).
- [Cripto passa a congelar amostra no lote] → leitura extra no começo de cada ativo; teste de regressão garante resultado igual.
- [Pausa espera a etapa em curso] → uma otimização longa pode atrasar a pausa; "Pausando…" diz qual ativo e etapa está terminando.
- [Favorito de ação/ETF existe antes do #1122 atualizar] → linha diz que a atualização diária ainda não vale para ações e ETFs; aceite espera o #1122.
- [Chave de unicidade sem fonte/sessão/ajuste até o #1122] → hoje cada ticker tem uma só fonte por classe, então não há colisão real; o #1122 estende a chave.
- [Otimização com janela fixa de jan. 2024] → ação/ETF em 15m, 1h e 4h quase sempre ficam fora (o 5m começa em mai. 2026); 1d roda em precisão diária. Herdado do #1119.
- [Servidor de protótipos só enxerga worktree novo depois de reiniciado] → neste card `criptofarol-dev-prototypes.service` foi reiniciado em 24/10/2026 e a URL pública responde 200.

### P3 aceitos (detalhe de Apply)

Do autor:

- Nomes de campos e rotas (`items`, `state`, `success_daily`, `collect_kind`, `/batch/preview`, `/batch/{id}/resume`, `/batch/active`, `batch_paused`), nomes das tabelas e a forma do `on_progress`.
- Limiar exato de "Insuficiente" (maior período do template + 1 candle, ou o que o otimizador já exige) e o texto exato do motivo.
- Formato de número e data (o formatador vivo: "+1284.50%", "24/10, 09:12"; o protótipo mistura com "24 out. 2026" do #1119), ordem das linhas do bloco novo da estratégia, ícones.
- Amostra do protótipo: números, datas, id do lote, tempos e páginas de coleta, a taxa "assumida", a lista "AÇÃO N" do lote grande e o painel Demonstração (não vai para o produto).
- Achados do detector no incumbente clonado (cinza sobre cor e roxo/gradiente dos botões vivos, tipografia do AppNav), todos em COPIED ou na marcação viva das estrelas de cripto.

Da crítica A/B (aceitos como detalhe de Apply, sem resolver aqui):

- A P3 / B P3-10 · Amostra: ATR "1834.20 USDT" igual em BTC, ETH e SOL; SOL com apelido "(batch)" sem lote; NVDA e SPY sem janela efetiva própria no detalhe da Otimização; formatos de número e data misturados.
- A P3 · Célula Symbol: "Ação ·" quebra e deixa "USD" sozinho na linha a 1440; `nowrap` no par chip·moeda.
- A P3 / B P3-5 · Linha viva recriada a cada render (`innerHTML`); no React o nó `role=status` fica estável e só o texto troca.
- A P3 · "Só ações/ETFs em tempo que não serve → Nada será executado" não demonstrado; texto e regra na decisão 6 e no spec.
- A P3 / B P3-8 · Incumbentes fora do card: botões de rodar com 22 px (reset `*` vivo), select de Timeframe com 20 px, rótulos de filtro a 3,65:1, "Backtest atualizado" a 3,54:1, descrição a 4,46:1, modal "Strategy Comparison" (admin) sem classe/moeda, `TODO: Date picker (#1120)` desatualizado no `ComboOptimizePage.tsx`, achados do detector no `live.css` (39 CLI, 335 hook) e no AppNav.
- B P3-6 · Filtros Symbol, Strategy, Time e Direção sem ligação no protótipo; o contrato ("N filtradas" e rodapé seguem os filtros) vale para todos no Apply.
- B P3-9 · `parse_live_route` captura a linha seguinte (`surface: existing`) como justificativa; é processo, fora do card.
- Encerrar durante a execução marca na hora o ativo em curso como "Não rodou" no protótipo; no produto o pedido vale ao fim da etapa (decisão 10).

## Migration Plan

1. Migração: tabelas do lote e dos itens no PostgreSQL. Sem mudança em `favorite_strategies` (os campos novos vão em `metrics` e `parameters`, JSON).
2. Deploy do servidor com o lote misto, o preview, a retomada e o lote ativo; o front novo no mesmo deploy (o front antigo não manda ação/ETF no lote).
3. Favoritos passa a listar ação/ETF no mesmo deploy; antes do #1122, as linhas de ação/ETF dizem que a atualização diária ainda não vale.
4. Lotes em andamento no Redis na hora do deploy terminam no caminho antigo.

Rollback: voltar o front e o servidor devolve a recusa de ação/ETF no lote e o filtro só cripto; os favoritos de ação/ETF já gravados ficam no banco e voltam a ficar ocultos; as tabelas do lote ficam sem uso.

## Open Questions

Nenhuma aberta de produto. As decisões de Alan de 24/10/2026 estão no Entra (5m tira ação/ETF e roda cripto; qualquer tamanho com contagem de coleta, pausa e cancelamento; precisão diária marcada; resultado vira favorito com aceite dependente do #1122; lista única com USD e USDT separados). Depois da crítica A/B, Alan decidiu que um lote pausado bloqueia um lote novo (decisão 16). As escolhas de *como* (Favoritos como lista de comparação, seleção com mais de 1 ativo sempre lote, confirmar no fluxo, pausa ao fim da etapa, texto novo da Descoberta) estão nas decisões 1, 2, 5, 10 e 13.

## Apply contract

O Apply lê este `design.md` e os HTML em `frontend/public/prototypes/card-1120-lote-multiclasse/` como spec de layout.

**Contrato visível (não P3):**

- Favoritos: lista única de cripto, ação e ETF (tabela e cartões); filtro Classe com contagens e anel de foco nos selects; chip de classe e moeda por linha (nunca as duas moedas); bloco da estratégia com precisão (azul ou âmbar com trecho), convenções em uma linha e período efetivo à vista, e "Limitações e origem" num `<details>`; células sem o `aria-label` vivo; favorito antigo diz quando os dados aparecem; em ação/ETF, estrelas, Telegram e Revalidar `aria-disabled` com o motivo, e o resumo e o filtro por estrelas só com cripto, mais a nota; faixa do lote com `?lote=` e "Mostrar todos os favoritos"; ordenação comum; sem rolagem horizontal a 390 px.
- Combo e Otimização: textos da decisão 6 (inclusive Market Data por ativo e o fora por cobertura da Otimização em 15m/1h/4h); tempos "(só cripto)" na seleção mista; seleção com mais de 1 ativo sempre lote; Confirmar lote no fluxo com a contagem de coleta da decisão 4, quem fica fora e por quê, e a configuração com o tempo e o período escolhidos; na Otimização, Confirmar e painel na coluna larga; lote pausado bloqueia lote novo (decisão 16); Pausando… com `aria-disabled` e foco no título depois de Encerrar; painel do lote com selo, linha viva, barra, nota de precisão diária, filtro por estado, lista por ativo com classe e moeda, "Mostrar mais 50", Pausar/Pausando…/Retomar/Encerrar, resumo e link para `/favorites?lote=`; painel do lote ativo ao reabrir; cartões abaixo de 620 px de largura do painel.
- Descoberta: só o porquê da recusa troca (decisão 13).
- Comportamentos dos specs: aceite e recusas por classe e tempo, preview sem coleta, coleta por ativo com progresso, estados e motivos, mesma amostra, pausa/retomada duráveis, favorito com identidade, API de favoritos com `asset`.

**P3 aceito (Apply):** os itens da subseção "P3 aceitos" em Risks / Trade-offs.

## Prototype

- Canônico: `frontend/public/prototypes/card-1120-lote-multiclasse/index.html`, clone de `/favorites` com 5 favoritos: NVDA (Ação, USD, precisão diária com o trecho, gerado no lote 7f3c2a91), BTC/USDT (Cripto, USDT, intrabar, lote), ETH/USDT (favorito antigo, sem `execution`), SPY (ETF, USD, precisão diária, lote) e SOL/USDT (4h). Filtro Classe e Ordenar funcionam; `?lote=7f3c2a91` mostra a faixa e só os 3 do lote. NVDA e SPY com estrelas, Telegram e Revalidar desabilitados e o motivo; resumo por estrelas "Acompanhar 1" com a nota; "Limitações e origem" fechado em cada linha do lote. Demonstração: "Todos os favoritos" / "Pelo fim do lote".
- Extra `configure.html`: clone de `/combo/configure` com BTC/USDT, NVDA e SPY em 1d, todo o histórico: nota da classe nova, sob demanda "backtest ou o lote", Market Data por ativo, tempos "(só cripto)", texto antes de rodar. Otimizar abre o Confirmar lote ("1 de 3" precisam de coleta: SPY). Confirmar e rodar abre o painel com BTC/USDT Sucesso, NVDA Otimizando (nada a coletar) e SPY Na fila. Avançar leva SPY a "Coletando · 5m do intrabar · página 7 de 20". Pausar → Pausando… → Pausado → Retomar. Com o lote pausado, Otimizar mostra "Retome ou encerre o lote 7f3c2a91 antes de começar outro". Encerrar. Trocar o Timeframe para 1m/5m mostra o fora antes de começar com o tempo escolhido, e trocar o Período muda a Configuração do Confirmar. Demonstração: "O mesmo lote em 5m", "Lote grande (2.431)", "Avançar uma etapa" (até Concluído, com NVDA e SPY em precisão diária e o link para Favoritos) e "Lote com problemas" (sucesso, precisão diária, insuficiente, rejeitado, falha, pulado, fora).
- Extra `optimize.html`: clone de `/combo/optimize` com `multi_ma_crossover` e a mesma seleção no período fixo (1 a 31 jan. 2024). Mostra a nota da classe, os tempos "1m/5m/30m (só cripto)" e o texto antes de rodar. Run Optimization → Confirmar lote ("1 de 3": SPY só 1d) → painel, os dois na coluna larga no lugar de "Ready to Optimize", com as mesmas ações e o mesmo bloqueio do lote pausado. 15m, 1h e 4h deixam NVDA e SPY "Fora" pela cobertura do 5m, e 1m, 5m e 30m mandam usar "1d aqui ou o Combo". Demonstração extra: "O mesmo lote em 1h".
- Apoio: `live.css` (CSS vivo inteiro), `delta.css`, `delta.js`.
- Nenhuma página é painel ANTES/DEPOIS nem "N estados"; o painel Demonstração fica no fim, no fluxo, sem `position:fixed`.

## Prototype Validation

Evidência do rework r1 (24–25/10/2026). Ela substitui a do autor a1, e qualquer mudança posterior nos arquivos abaixo a invalida. Os HTML saem de um build determinístico a partir das mesmas capturas vivas do a1 (`develop` @ e762e470, bundle `index-BvxVmoZs.js`, API simulada, 1440 e 390 px). Toda região COPIED é substring literal da captura (`copiedcheck.py`: 0 fora da captura nas três páginas) e não há marcador dentro de tag. O "Ver logs" do Combo voltou a ser só o botão (B P3-1).

| Arquivo | Bytes | sha256 | COPIED | DELTA |
|---|---|---|---|---|
| `index.html` (canônico) | 112.127 | `90498666055ce3a3c289cb8a923b0d6b67497fe5f98f5695a9f39a5609560dc3` | 56/56 pares, 62.877 B | 53/53, 45.471 B |
| `configure.html` | 37.671 | `1dc2798d4613d57731aba25cb30dbcf3a894ffa5f0dbe7df1e5f8de8c7f47e5b` | 13/13 pares, 31.979 B | 10/10, 4.101 B |
| `optimize.html` | 32.393 | `66f6f4736d81be1c7309f2abb2bd24dba4f7b9118e4810bf42307c777785e469` | 12/12 pares, 27.803 B | 9/9, 3.067 B |
| `live.css` | 227.726 | `da9e66e69f963f98815d45baf15fbb0dc8eea0f31b3225a363a8be171b5abf7b` | clone inteiro | — |
| `delta.css` | 19.886 | `9e40704ba233a53f6df8e328aee249f24ab3682faa4ec0d987bd81944da7bdee` | — | delta |
| `delta.js` | 33.386 | `798fb4e3b656be2c4f864baf3ba19c9a4cce13eb6815bdecb67b64f27c66af3e` | — | delta |

- **Gate do clone** (`scripts/process-fsm/design_clone_gate.py`, catálogo do HEAD): `design_token_gap` = None; `UI impact: affected` / `live_route: /favorites` / `surface: existing` em L1–L3; `evaluate_clone_gate` = True; `clone_gate_ok` = True; `canonical_proto_html` = `index.html`; `classify(index.html, /favorites)` = PASS (`copied_utf8_sum` 62.877 B: as estrelas, o Telegram e o Revalidar de NVDA e SPY passaram a DELTA). `/combo/configure` e `/combo/optimize` não estão no catálogo: extras sem gate próprio. `openspec validate card-1120-lote-multiclasse --strict`: válido.
- **Browser gate na URL pública:** `python3 -E -P gate_r1.py https://dev.criptofarol.com.br <proto_dir>`, com Playwright Python, Chromium headless shell 1243, `pt-BR` e tema escuro. Cada página × viewport abre em contexto novo; o 390 usa `isMobile` e toque. URLs: `https://dev.criptofarol.com.br/prototypes/card-1120-lote-multiclasse/` (+ `configure.html`, `optimize.html`). Resultado: **518/518 asserts PASS**.

  | Página | 1440×900 | 390×844 |
  |---|---|---|
  | `index.html` (pasta `/`) | 55/55 | 55/55 |
  | `configure.html` | 93/93 | 93/93 |
  | `optimize.html` | 112/112 | 110/110 |

  Cobertura comum:
  - sha256 servido == disco nos 6 arquivos;
  - COPIED e DELTA em pares, sem atributo `<!--` no DOM;
  - Demonstração no fluxo;
  - sem rolagem horizontal em cada estado;
  - nenhum "o lote vem depois".

  Asserts novos do r1, por item:
  - (A P1-1) NVDA e SPY com 3 estrelas, Telegram e Revalidar `aria-disabled`, focáveis, sem estrela marcada e com `aria-describedby` → "Monitor, Telegram e Revalidar: ainda não para ações e ETFs". O clique não marca. BTC/USDT segue com os controles vivos. Resumo "Acompanhar 1", filtro "Acompanhar 1" e a nota.
  - (A P1-2 / B P2-1) Na Otimização em 15m, 1h e 4h: o texto antes de rodar, "Ficam fora" e o estado "Fora" de NVDA e SPY trazem o motivo de cobertura. A Configuração não diz "1d" e vão rodar só BTC/USDT. Em 1m, 5m e 30m o conselho é "use 1d aqui ou o Combo, que tem período", sem "15m, 1h, 4h". A nota da classe cita a regra.
  - (B P2-2) "1 de 3" com "BTC/USDT e NVDA já estão guardados, sem lacunas e atualizados" e a regra. SPY conta com "1d e 5m do intrabar" no Combo e com "1d" na Otimização ("O 5m de SPY não entra"). O lote grande mostra "2.388 de 2.431", "2.351 sem histórico guardado", "37 só com o trecho" e "43 já estão guardados". NVDA otimiza sem coleta e o progresso de coleta fica em SPY.
  - (B P2-3) Market Data "Por ativo: CCXT (cripto) · Binance Ações (ação e ETF)".
  - (A P2 / B P2-4) Na Otimização, o template é `multi_ma_crossover`. Confirmar e painel ficam na coluna larga, com "Ready to Optimize" oculto enquanto há lote e de volta depois do Voltar. A 1440 os dois passam de 620 px e a lista sai em colunas.
  - (A P2 densidade) "Limitações e origem" fecha num `<details>` e abre com as convenções completas, as limitações e o lote. Classe, moeda, precisão, convenções curtas e período efetivo ficam à vista. NVDA mede ≈255 px a 1440 (era 283) e ≈640 px a 390 (era 685).
  - (A P2 / B P3-4) "Pausando…" com `aria-disabled` e sem `disabled`, foco nele e Encerrar `aria-disabled`; o clique não muda nada. Depois de Encerrar (pelo painel ou pelo aviso), o foco vai ao título do lote.
  - (A P2) As células símbolo e estratégia ficam sem `aria-label`.
  - (A P2) "Mostrar todos" pelo teclado leva o foco ao Classe com outline visível.
  - (B P3-1) "Ver logs" com o texto e o `title` íntegros.
  - (A P3 / B P3-2) Sucesso, chip ETF e selo Concluído em `rgb(14, 203, 129)` no Combo e na Otimização.
  - (B P3-3) A Configuração do Confirmar diz o tempo escolhido (1m, 5m, 30m, 15m, 1h, 4h) e o Período do select ("15 dias" / "todo o histórico").
  - (A P3) "Ver o resultado do lote em Favoritos" com 1 favorito e "Ver os 2/3 resultados" com mais; nenhum "coletado quando uma análise pedir".
  - (Decisão 16) Com o lote pausado (pausa na otimização de NVDA, pausa na coleta de SPY e lote grande), rodar mostra "Retome ou encerre o lote 7f3c2a91 antes de começar outro.". Não aparece Confirmar nem "Confirmar e rodar". O foco vai ao aviso, o painel pausado segue visível e os botões têm 44 px. "Retomar o lote" volta a Rodando no mesmo id; "Encerrar o lote" deixa Encerrado com os 2 favoritos. Lote encerrado não bloqueia.

  Do a1, seguem cobertos: Favoritos (ordem, classe e moeda, filtro Classe, Ordenar, `?lote=`), Confirmar no fluxo e Voltar, painel e linha viva, Pausado → Retomar, Concluído com precisão diária e link, Encerrar, 5m, "Lote com problemas" e lote grande com "Mostrar mais".

  Console: 0 `console.error`, 0 `pageerror`, 0 resposta ≥ 400 e 0 `requestfailed` nas 6 cargas e nos fluxos.

  Scripts no scratchpad do rework: `r1/build_r1.py` (build a partir de `cap/`), `r1/copiedcheck.py`, `r1/gate_r1.py`, `r1/detclass.py` e `r1/hookmode.mjs`.
- **Detector Impeccable** (`node .agents/skills/impeccable/scripts/detect.mjs --json`, cada achado localizado pela região do marcador):
  - `delta.css` e `delta.js`: `[]`.
  - `index.html`: 5 achados, todos COPIED: 4 `gray-on-color` (estrelas vivas marcadas de BTC/USDT e ETH/USDT, cartão e linha) e 1 `flat-type-hierarchy` (AppNav). O a1 registrou "2" por engano (B P3-7); o certo no a1 era 9. Caiu para 5 porque as estrelas de NVDA e SPY viraram DELTA sem âmbar.
  - `configure.html`: 10 achados, todos COPIED (`gray-on-color` nos chips e no checkbox vivos, roxo/gradiente do Otimizar, AppNav).
  - `optimize.html`: 5 achados, todos COPIED (roxo/gradiente do Run Optimization, AppNav).
  - Modo hook (`DESIGN.md` da raiz): `delta.css` 0 e `delta.js` 0; os HTML ganham só os 3 `design-system-font-size` do AppNav (COPIED).
  - O marcador do `<details>` do primeiro rascunho (triângulo com bordas) disparou `border-accent-on-rounded` e virou `clip-path`, sem achado depois.
  - Nenhum achado silenciado.

## Impeccable

Operate, refinamento clone+delta de `/favorites`, `/combo/configure` e `/combo/optimize`. Setup com `node .agents/skills/impeccable/scripts/context.mjs --target frontend/src/pages/FavoritesDashboard.tsx` (PRODUCT.md + DESIGN.md). Shape: em Favoritos, a resposta a "posso comparar estas linhas?" fica onde o olho já está — chip de classe e moeda colados ao símbolo, precisão e convenções logo abaixo do estado da atualização, âmbar só quando a precisão caiu; no lote, a pergunta é "o que vai acontecer e onde está cada ativo?", então a contagem de coleta vem antes de confirmar (painel no fluxo, não modal) e o painel mostra uma linha viva curta, filtros por estado e a lista por ativo, que vira cartões quando o espaço aperta (container query, para servir à coluna estreita da Otimização). Tokens do produto (`--accent-primary`, `--fav-up`, `--ap-info-*`, `--ap-warn-*`, `--ap-danger-*`, `--border-default`, `--bg-secondary`, `--text-tertiary`), chips nas cores do `.ap-fact.cls-*` vivo, rampa 12/13/14/16 px, raios 8/12 px, alvos de 44 px, foco visível, ícone + texto em todo estado, `role=status` só na linha viva e na faixa do lote, `aria-pressed` nos filtros, contraste AA medido (comentário do `delta.css`). Sem borda colorida lateral nova, sem modal, sem cor inventada. No rework r1, `--fav-up` passa a ter fallback (`var(--fav-up, #0ecb81)`), porque o token só existe dentro de `.favorites-workbench`. Controles fora de escopo (Monitor, Telegram, Revalidar em ação/ETF) ficam à vista e desabilitados, com o motivo, e não somem. A densidade cede ao `<details>` só o que não serve para comparar linhas (limitações, convenções completas, origem). A seção de crítica fica para o pai.

## Design Critique

Com-tela. Teto 1+1+1: autor, dupla A/B e 1 rework. O rework (r1) aplicou a decisão de Alan no Design e os achados de produto e mecânicos da dupla. Não houve segundo rework.

- Autor: `design-autor 1120 a1` (isolado). Rework: `design-autor 1120 r1` (isolado).
- Assessment A: `assessment-a 1120 a1` (isolado; produto, UX, acessibilidade, fidelidade). Assessment B: `assessment-b 1120 a1` (isolado; detector + navegador).
- Verdict: **PASS**. Tokens: `UI impact: affected` / `live_route: /favorites` / `surface: existing`.
- Proto canônico: https://dev.criptofarol.com.br/prototypes/card-1120-lote-multiclasse/
- Protos extras: https://dev.criptofarol.com.br/prototypes/card-1120-lote-multiclasse/configure.html e https://dev.criptofarol.com.br/prototypes/card-1120-lote-multiclasse/optimize.html
- Snapshots: `.impeccable/critique/1120-card-1120-lote-multiclasse-A.md` e `…-B.md`. O Gist OpenSpec não é a crítica.

- **P0**: nenhum.
- **P1** (A), corrigidos no r1:
  - Favoritos: Monitor, Telegram e Revalidar desabilitados em ação/ETF, com motivo visível; ação/ETF fora do resumo de níveis do Monitor (até o #1122).
  - Otimização com 15m/1h/4h: ação/ETF cujo 5m não cobre a janela fixa de jan. 2024 ficam "Fora" com motivo antes de rodar; conselho "use 1d aqui ou o Combo".
- **Juízo, decidido por Alan no Design** ([comentário](https://github.com/oalansilva/crypto/issues/1120#issuecomment-6391037848)), aplicado no r1:
  - Lote pausado bloqueia um lote novo: o Otimizar pede para retomar ou encerrar antes de começar outro (decisão 16).
- **P2 de produto, corrigidos no r1**:
  - contagem "precisa de coleta" contra o que a Binance tem e o histórico já guardado, não contra a janela pedida;
  - Market Data no Combo com seleção mista: fonte por ativo;
  - painel do lote e Confirmar na coluna larga da Otimização, com o template escolhido;
  - densidade de Favoritos: limitações, convenções completas e origem atrás de `<details>` (redução parcial: ≈255 px a 1440, ≈640 px a 390; o resto é descrição e apelido vivos).
- **P2 mecânicos, corrigidos no r1**: foco durante "Pausando…" e depois de Encerrar; `aria-label` vivo das células símbolo/estratégia; `:focus-visible` nos filtros; marcadores dentro do botão "Ver logs"; fallback de `--fav-up`; Confirmar seguindo tempo e período escolhidos; plural; texto antigo de coleta; contagem do detector.
- **P3 aceitos, para o Apply**: os itens da subseção "P3 aceitos (detalhe de Apply)" em Risks / Trade-offs, mais os achados do detector nos HTML, todos em regiões COPIED do incumbente (AppNav, estrelas, cinza sobre cor herdado).
- **Disposition:** o delta visível fica em Favoritos (`/favorites`, lista única de comparação), no Combo (`/combo/configure`) e na Otimização (`/combo/optimize`). Descoberta com ação/ETF fica para o #1121; atualização e alertas de favoritos de ação/ETF, para o #1122 (aceite deste card depende dele); benchmark e exportação, para o #1123.

### Proxies

- `design.md` words: 7372 (antes desta seção)
- HTML generated vs copied (`index.html`): 42366 vs 61283
- Spawns: 4 (design-autor a1, assessment-a a1, assessment-b a1, design-autor r1)
- `proxy modelo: design-autor → Opus 5.5 (claude-opus-5-5)` (a1 e r1)
- `proxy modelo: Assessment A → Opus 5.5 (claude-opus-5-5)`
- `proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5)`

Design Agent verdict: PASS
