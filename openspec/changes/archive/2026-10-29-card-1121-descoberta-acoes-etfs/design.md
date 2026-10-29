UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card [#1121](https://github.com/oalansilva/crypto/issues/1121), quinta história do épico [#1116](https://github.com/oalansilva/crypto/issues/1116). O briefing é o issue grelhado (fronteira vazia), com as 4 decisões de Alan de 26/10/2026 dentro de Entra. Não houve reentrevista. O *como* abaixo foi conferido em `develop` @ 5bd1695f, depois do #1117, #1118, #1119 e #1120, os quatro Homologados. Os OpenSpec deles (`openspec/changes/card-1117-catalogo-ativos`, `card-1118-historico-binance`, `card-1119-backtest-acoes-etfs`, `card-1120-lote-multiclasse`) são os contratos reutilizados. O #1122 ainda não foi entregue; o contrato com ele está na decisão 10.

Estado atual, conferido no código:

- **Recusa por classe.** `asset_analysis_guard.py:174-215` (`discovery_symbol_reasons`) devolve ação e ETF com `DISCOVERY_EQUITY_REASON` (`asset_catalog_service.py:66-74`, "… a Descoberta vem depois"). O Preflight (`discovery_service.py:348-536`) conta isso como fora e, sem cripto, bloqueia com "Inclua ao menos 1 par cripto" (`:473-483`). No front, `resolveSelection` marca toda não-cripto como `class` (`assetSelection.ts:506-518`), `axisCount` conta só cripto (`DiscoveryPage.tsx:647`) e a nota do seletor diz "Nesta etapa as análises rodam só com cripto" (`DiscoveryPage.tsx:2198-2205`). O texto sob demanda de ação diz "a coleta começa quando as análises aceitarem ações" (`assetSelection.ts:212-217`).
- **Aquisição fixa em cripto.** `discovery_inputs.prepare` só congela pelo caminho unificado quando o símbolo tem `/` (`discovery_inputs.py:110`). `_prepare_snapshot` usa `CcxtMarketDataProvider` + `IncrementalLoader.fetch_intraday_data` e `freeze_crypto` (`:50-102`). Sem `MARKET_HISTORY_UNIFIED`, cai no spool CCXT (`:112-153`). O supervisor congela, mede a listagem (`discovery_supervisor.py:136-151`) e chama `run_optimization(..., data_source="ccxt")` (`:157-162`). Com a amostra ativa, o otimizador lê `FrozenProvider` (`combo_optimizer.py:2333-2337`) e `_begin_sample` não congela de novo (`:2201-2224`).
- **Precisão já existe no motor.** `_extract_trades_with_execution` devolve `precision_requested`, `precision_effective` e `intraday_missing` (`combo_optimizer.py:504-560`). A guarda de cobertura cai para o candle do tempo gráfico e diz o trecho sem 15m (`:575-617`). O resultado traz `asset`, `execution` e `conventions` (`:3109-3147`), mas `run_combination` não os guarda (`tasks/discovery_tasks.py:250-480`).
- **Cobertura 24/7.** `_expected_candles_for_window` conta 6 velas/dia em 4h e 1/dia no resto (`tasks/discovery_tasks.py:740-750`). A elegibilidade exige ≥ 90% (`:384-392`). Com o pregão de NY, todo 1d de ação teria ≈ 69% e todo 4h ≈ 33%: tudo cairia em "Baixa amostra".
- **Custos.** `fees_slippage_record` grava sempre `TRADING_FEE` 0,075% (`metrics/backtest_execution_costs.py:65-73`), mas a ação e o ETF simulam 0,10% (`:16-21`). O cabeçalho do Decidir tira janela, candles e taxa da primeira linha elegível (`DiscoveryPage.tsx:1530-1545`).
- **Ranking e linha.** `_result_row` já expõe `provenance` (`data_source`, `asset_class`, `session`, `adjustment`, `period_covered`) e `snapshot_id` (`discovery_service.py:1843-1910`). `discovery_results` já tem essas colunas (`models_discovery.py:132-140`). A linha do Decidir não mostra símbolo, classe nem moeda: o mercado só aparece em "+ detalhes" (`DiscoveryPage.tsx:2760-2830`). Os filtros são Ordenar, Símbolo e Timeframe (`:2633-2690`).
- **Promoção.** `promote_result` grava `FavoriteStrategy` com `tier=3` e as métricas de `build_promoted_favorite_metrics` (`discovery_service.py:2032-2260`, `discovery_favorite_metrics.py:184`). Não grava fonte, classe, execução nem convenções, e não passa `data_source`/`asset` a `lock_and_find_duplicate` (`favorite_uniqueness.py:65-78`, já aceita os dois desde o #1120).
- **Favoritos já renderiza a identidade.** `favoriteRowData` (`favoriteClass.ts:174-195`) mostra classe, moeda, precisão, convenções, período efetivo e "Limitações e origem" a partir de `analysis_asset`, `analysis_execution` e `analysis_conventions` (#1120). Ação e ETF sem estrela já aparecem com Monitor, Telegram e Revalidar desabilitados.
- **Tentativas e retomada.** `MAX_ATTEMPTS = 3` (`discovery_recovery.py:25`). O heartbeat grava o `candle_manifest` no `input_snapshot` da combinação (`:153-165`), então uma nova tentativa reaproveita a amostra. Pausar, Retomar e Cancelar estão em `discovery_service.command` (`:1268-1370`).
- **Fato divergente do issue.** O body diz que o período padrão da Descoberta é "todo o histórico". O código abre o rascunho em **15 dias** (`sweepPeriod.ts:16`, `DISCOVERY_DEFAULT_PERIOD = '15d'`); a captura viva confirma. Este card não muda o padrão. A Verificação ("NVDA em todo o histórico") escolhe "Todo o histórico" no select.

**Audience:** Alan, que monta uma varredura com cripto, ação e ETF e quer ver os candidatos lado a lado, sabendo de onde vem cada número.
**Outcome:** uma Descoberta que aceita as três classes e congela a amostra certa para cada ativo. O que caiu para precisão diária fica marcado, e cada ativo tem um estado. O ranking único mostra classe, moeda e convenções, e a ação ou o ETF pode ser promovido a favorito com a identidade da execução.
**Direction:** clone+delta Operate de `/combo/discovery` (Montar, Acompanhando, Decidir e o modal de promoção). Tokens do produto, sem mundo visual novo; chips de classe nas cores do `.ap-fact.cls-*` vivo e do `.b20-cls` do #1120.
**Scope:** Preflight, aquisição e congelamento por classe, estado por ativo, teto, viés de sobrevivência, ranking com classe/moeda/convenções, filtro Classe e promoção. Fora: ordens, novas famílias de estratégia, Monitor/alertas de ação e ETF (#1122), benchmark e exportação (#1123), mudar o período padrão.

Regiões clonadas da página viva, só estas (capturadas em `https://dev.criptofarol.com.br/combo/discovery`, bundle `index-SlORbkwS.js` / `index-BKQOezYM.css`, API simulada, 1440 e 390 px, marcadas com `COPIED:start`/`COPIED:end`):

- `index.html` (canônico, `/combo/discovery`):
  - fundo vivo;
  - AppNav desktop (barra lateral e topo, 1440 px) e AppNav móvel (topo, 390 px);
  - cabeçalho ("Descoberta de estratégias swing", breadcrumb, "Histórico de varreduras") e as abas Montar / Acompanhando / Decidir;
  - modo **Montar** com BTC/USDT, NVDA e SPY, `multi_ma_crossover`, 1d, Long e Todo o histórico: Rascunho de varredura (Templates, Ativos com o seletor do #1117/#1118, Timeframes, Direção, Período, Ranking) e o Preflight;
  - modo **Acompanhando** da varredura `#c1121mix` (Sweep ativo, progresso, Pausar/Cancelar/Novo rascunho, Rascunho congelado, Parciais);
  - modo **Decidir** (Leaderboard · Calmar, filtros, tabela com 3 candidatos, paginação e notas);
  - modal "Promover a favorito tier 3";
  - fim da página viva.
- `live.css`: o CSS vivo inteiro (`index-BKQOezYM.css`), sem poda. É a única folha da rota.

O delta fica só nos blocos `DELTA:start`/`DELTA:end`:

- **Montar:**
  - texto sob demanda das linhas do seletor e nota da classe;
  - estado, total, 3 linhas, fórmula, detalhe técnico, estimativa e botão do Preflight com 3 combinações;
  - o bloco "Fora desta varredura" vira "Vão rodar / Precisam de coleta / Precisão diária prevista / teto / Viés de sobrevivência";
  - taxa por classe;
  - datas do período personalizado (aparecem com "Personalizado", como no JSX vivo).
- **Acompanhando:** quadro "Por ativo" (cabeçalhos de coluna, lista e "Mostrar mais 50"); classe, moeda, precisão, convenções e período efetivo em cada parcial.
- **Decidir:**
  - estado da varredura no cabeçalho ("em execução" deixou de ser COPIED), cabeçalho multiclasse, nota "Sem resultado" e aviso de sobrevivência;
  - filtro Classe;
  - classe, moeda, precisão, convenções e período efetivo em cada linha;
  - nota de cobertura por calendário e moedas separadas.
- **Modal:** identidade da execução e destino de ação/ETF.
- **Cola do clone:** os invólucros dos três modos e do modal (cada um mostrado por vez, como o React faz), os invólucros `.cf-desk`/`.cf-mob` do AppNav e o painel "Demonstração".

O estado de formulário que o React põe por propriedade (checkbox marcado, valor do select e da busca) foi refletido em atributo na captura, para o HTML estático mostrar o que a tela viva mostrava.

## Goals / Non-Goals

**Goals:**

- Cripto, ação e ETF na mesma varredura; marcado e fora do catálogo seguem fora com motivo.
- Cada ativo coletado e congelado pela sua fonte; o otimizador recebe a fonte do ativo.
- Mesma amostra para treino, tentativas e avaliação final; corte 70/30 no tempo; cobertura pelo calendário da classe.
- Precisão diária marcada com o trecho, prevista no Preflight e nunca silenciosa.
- Estado explícito por ativo; amostra insuficiente e falha nunca viram candidato.
- Teto de 1.000 contando ação e ETF, com recusa antes de começar.
- Orçamento, progresso, cancelamento e retomada valendo para ação e ETF.
- Ranking único com classe, moeda e convenções por linha e filtro Classe.
- Promoção de ação e ETF com a identidade da execução; cripto como hoje.
- Aviso de viés de sobrevivência.

**Non-Goals:**

- Ordens automáticas ao descobrir ou favoritar (Não entra).
- Novas famílias de estratégia (Não entra).
- Atualização diária, Monitor, alertas, Telegram, estrelas e Revalidar de ação/ETF; chave de unicidade com sessão e ajuste (#1122).
- Benchmark escolhido e exportação com as convenções (#1123).
- Mudar o período padrão da Descoberta (15 dias hoje) ou a direção (só Long nesta etapa, como hoje).
- Short na Descoberta, lote, Combo e Otimização (já entregues).

## Decisions

1. **Página única = `/combo/discovery`; sem URL extra.** A Descoberta tem os três modos e o modal na mesma rota, e o canônico clona os quatro. Favoritos não muda visivelmente: a promoção grava as mesmas chaves `analysis_*` que `favoriteRowData` já lê (#1120). O favorito de NVDA aparece lá com classe, moeda, precisão, convenções, período efetivo e "Limitações e origem" sem código novo em Favoritos, por isso não há clone extra. A Verificação "chega a favorito" é demonstrada no próprio Decidir ("Favorito · sem estrela" + "Ver em Favoritos"). `/combo/discovery` está no catálogo do gate ("Descoberta de estratégias swing", "Preflight", "Rascunho de varredura", todos em COPIED). Alternativa rejeitada: clone extra de `/favorites`, que mostraria só o que o #1120 já entregou.

2. **Aceite por classe no Preflight.** `discovery_symbol_reasons` deixa de devolver ação e ETF; marcado e fora do catálogo seguem. `DISCOVERY_EQUITY_REASON` e o ramo "Inclua ao menos 1 par cripto" saem do Preflight. O bloqueio passa a ser "nenhuma combinação válida" só por marcado/fora do catálogo. No front, a Descoberta passa a tratar ação e ETF negociáveis como `runs` (opção da Descoberta em `resolveSelection`, sem mexer no Combo). `axisCount` conta todos os que rodam. O Preflight ganha `by_class` (ativos e combinações por classe e moeda). Visível:
   - estado "Pronto para iniciar";
   - "Vão rodar 3 ativos: 1 cripto (USDT) · 1 ação · 1 ETF (USD). Cada um com a sua fonte, sessão, ajuste e moeda.";
   - nota do seletor "Cripto, ação e ETF entram na mesma varredura: cada ativo usa a sua fonte, sessão, ajuste e moeda (USDT ou USD). Sem 15m que cubra a janela, ação e ETF rodam em precisão diária, com a marca no resultado.";
   - texto sob demanda "Histórico sob demanda · coletado ao rodar a varredura" (mapa próprio da Descoberta, como o `ON_DEMAND_TEXT_BACKTEST` do #1120).

3. **Aquisição e congelamento por classe, pelo caminho do #1118.** `discovery_inputs.prepare` decide pelo catálogo (`asset_identity`, `equity_backtest.py:120`), não pela `/`. A cripto segue o `_prepare_snapshot` de hoje, renomeado `_prepare_crypto`. Ação e ETF:
   - (a) `prepare_equity_history(symbol, timeframe, start, end, intrabar=True, on_progress=…)` (`equity_backtest.py:241-318`) coleta a série do tempo gráfico (1d nativo, ou o 5m de onde saem 15m/1h/4h) e o 5m do intrabar;
   - (b) lê pelo `HistoryService` e congela com `ExecutionSample.freeze_symbol` (`market_history/sample.py:124-146`) nos papéis `candles` e `intraday`; sem 15m, congela vazio, como `_freeze_equity_intraday` (`combo_optimizer.py:2240-2262`);
   - (c) o manifesto leva `provenance` com `data_source = binance_equity`, classe, sessão e ajuste;
   - (d) o supervisor passa `data_source` do manifesto (`binance_equity` ou `ccxt`) a `run_optimization`, no lugar do `"ccxt"` fixo.

   O spool CCXT antigo continua só para cripto sem o caminho unificado. A taxa da simulação já é por símbolo (`fee_for_symbol`). Alternativa rejeitada: chamar `run_optimization` sem amostra prévia para ação e ETF. O motor congelaria sozinho, mas a coleta ficaria fora do lease e a listagem (insuficiente antes do otimizador) não teria dados.

4. **Uma amostra por ativo, tempo e janela na varredura.** Hoje cada combinação congela a sua (mesmo conteúdo, segmentos deduplicados por SHA). Passa a ser uma por `(sweep, símbolo, tempo, janela)`. A primeira combinação congela e grava o manifesto no sweep (`snapshot.samples[<símbolo>|<tempo>]`, sob o lock do sweep); as outras do mesmo ativo e tempo leem esse manifesto e não coletam de novo. Assim todos os templates e direções de NVDA 1d avaliam a mesma amostra. Treino 70% e avaliação 30% no tempo (`split_train_holdout`, `DISCOVERY_SPLIT_TRAIN_RATIO = 0.7`) e o burn-in do treino não mudam. A retomada e a nova tentativa já reaproveitam o `candle_manifest` (`discovery_recovery.py:153-165`). A amostra fica 30 dias e o favorito a fixa (`snapshots.pin`), como no #1118.

5. **Cobertura pelo calendário da classe.** `_expected_candles_for_window` passa a usar `nyse_calendar.expected_candles(timeframe, start, end)` (`market_history/nyse_calendar.py:195`) para ação e ETF. A cripto continua 24/7. Corrige também 15m e 1h, hoje contados como 1/dia, mas só para ação e ETF; a cripto fica igual (regressão). Sem isso, toda ação ou ETF cairia em "Baixa amostra". Visível: "100% velas" em NVDA e a nota "Cobertura conta as velas esperadas no calendário da classe: 24/7 na cripto, pregões de Nova York na ação e no ETF (fim de semana e feriado não contam)…".

6. **Precisão diária marcada e prevista.** `run_combination` guarda `result.asset`, `result.execution` e `result.conventions` em `metrics` (`asset`, `execution`, `conventions`). `_result_row` os devolve, com `precision` derivada (`intrabar_15m`, ou `daily` com os trechos `intraday_missing`). Rótulos iguais aos de Favoritos (`precisionText`, `favoriteClass.ts:118-140`): "Precisão intrabar (15m)" (azul, ícone de info) e "Precisão diária · sem 15m de <início> a <fim>" (âmbar, ícone de aviso), no Acompanhar, no Decidir, no modal e no favorito. O Preflight ganha `precision_forecast`, que compara a cobertura do 5m no catálogo (`asset.history.timeframes`) com a janela. Ativo sob demanda não tem previsão: "SPY: sem histórico guardado; a precisão aparece depois da coleta.". Texto: "Precisão diária prevista em 1d: NVDA — o 15m dele começa em 2 jan. 2026, então 2 jan. 2003 a 31 dez. 2025 roda no candle diário. … O resultado sempre marca o trecho." A previsão nunca troca a marca do resultado, que vem da execução.

7. **Estado explícito por ativo.** O motivo de amostra insuficiente distingue três casos:
   - "sem candles": `prepare_equity_history` levanta `history_unavailable` sem erro de coleta, ou a série congelada vem vazia;
   - "poucas velas": `listing_len < 2` ou treino < 30;
   - "falha de coleta": `history_unavailable` com `error_code`.

   Os dois primeiros viram `insufficient_sample` determinístico, com `eligibility_reason` "sem candles de 4h de NVDA nessa janela (o 5m da Binance começa em 2 jan. 2026)" ou "treino N < mínimo 30". O terceiro vira `OperationalFailure` e entra no orçamento de tentativas; esgotado, fica "Falha" com o motivo. `GET /sweeps/{id}` ganha `assets[]`: `{symbol, asset_class, currency, done, total, state, stage, page, pages, reason}`, agregado das combinações e do último evento de progresso da combinação em curso.

   O Acompanhar ganha "Por ativo" (`<ol>`):
   - **Colunas** Ativo · Combinações · Estado · Detalhe, com uma linha de cabeçalho visível quando o quadro tem mais de 620 px; cada célula leva o rótulo da coluna em texto para leitor de tela. Abaixo de 620 px vira cartão, sem cabeçalho.
   - **Estados**, sempre com ícone + texto: Na fila; Coletando histórico · <série> · página N de M; Pausado na coleta · <série> · página N de M · retoma daqui; Rodando · <tempo>; Concluído; Concluído · precisão diária; Amostra insuficiente: <motivo>; Falha: <motivo>; Não rodou · varredura cancelada.
   - **Desfecho misto:** quando as combinações de um ativo terminam diferentes, o Estado mostra a contagem de cada desfecho ("1 concluída · 1 amostra insuficiente", "1 concluída · 1 falha"), em âmbar, e o Detalhe diz o motivo por tempo ("1d: Precisão diária · sem 15m de … · 4h: Amostra insuficiente — sem candles de 4h de NVDA nessa janela …"). Nunca "Concluído" sozinho quando parte não concluiu.
   - **Ordem e limite:** o ativo em curso fica no topo, depois as falhas e as amostras insuficientes, e o resto na ordem da varredura. O quadro mostra 50 ativos e "Mostrar mais 50" (com "Mostrando N de M ativos") carrega os próximos, como no #1120. O teto aceita até 1.000 ativos, então o limite é necessário.
   - Uma linha `role=status aria-live=polite` anuncia só o ativo e a etapa em curso. Os contadores vivos ("N processadas = …") ficam.

   As parciais e o ranking só têm `succeeded`; insuficientes aparecem no Decidir como hoje ("Amostra insuficiente", sem rank e sem Promover). **O Decidir não esconde quem ficou sem resultado:** no fim, a tela salta para o Decidir (comportamento vivo), então o cabeçalho ganha a nota "Sem resultado: SPY — Falha: a Binance não respondeu ao histórico nas 3 tentativas. ver Por ativo" (falha), "Sem resultado: NVDA e SPY — Não rodou · varredura cancelada." (cancelada) ou "Amostra insuficiente: NVDA 4h e SPY 4h — …" (insuficiente), junto da nota de viés. "ver Por ativo" abre o Acompanhando com o foco no título do quadro. Ícone de falha em vermelho; cancelada em cinza; insuficiente em âmbar.

8. **Teto de 1.000 com ação e ETF.** O `DEFAULT_MAX_TOTAL` (`discovery_service.py:42`) passa a contar ação e ETF, que agora são válidos. Acima dele, `errors.total` e o Preflight mostram o total, as classes e "Estreite a seleção". Texto:
   - "Acima do teto de 1.000 combinações";
   - "2.433 combinações válidas passam do limite de 1.000: 2.433 ativos (1 cripto · 2.431 ações · 1 ETF) × 1 template × 1 timeframe × Long.";
   - "Estreite a seleção: menos ativos (filtre antes de usar "Todos do filtro"), menos templates ou menos timeframes. Nenhuma varredura foi criada."

   "Iniciar varredura" fica desabilitado e o servidor recusa a criação, como hoje.

9. **Orçamento, progresso, cancelamento e retomada.** A coleta roda dentro do processo filho da combinação, sob o mesmo lease, heartbeat, `MAX_ATTEMPTS = 3` e limites de recurso. `on_progress` de `prepare_equity_history` vira evento `progress` (`{"phase": "collecting", "series": "5m", "page": 7, "pages": 16}`), então a coleta longa não parece worker parado. Pausar e Cancelar valem nas mesmas fronteiras de hoje (lease em curso termina); retomar continua das pendentes. O `HistoryService.ensure` só busca o que falta, então páginas já gravadas não são refeitas. O Preflight ganha `collection` (mesma regra do `needs_collection` do #1120): conta só o que a Binance tem para a janela e não está guardado. Texto: "Precisam de coleta de histórico: 1 de 3 — SPY (1d e 5m do intrabar). BTC/USDT e NVDA já estão guardados. A coleta acontece no começo do ativo e entra no tempo da varredura."

10. **Promoção de ação e ETF como no lote; contrato com o #1122.** Quatro mudanças:
    - `promote_result` grava `tier = 3` para cripto e `tier = None` para ação e ETF (como `batch_backtest_service._save_favorite`). O payload continua exigindo `tier: 3` (contrato fixo); o servidor deriva o nível guardado.
    - Grava `parameters.data_source` e `parameters.direction`, e em `metrics` grava `analysis_asset`, `analysis_execution`, `analysis_conventions` e `data_provenance` (com `snapshot_id`), além da proveniência de hoje (`origin_type`, `sweep_id`, `result_id`…). A janela efetiva vai em `start_date`/`end_date` como hoje.
    - Chama `lock_and_find_duplicate` com `data_source` e `asset`. O #1122 estende a chave com sessão e ajuste sem mudar a chamada.
    - A atualização diária, o Monitor, os alertas, as estrelas e o Revalidar de ação e ETF são do #1122. Até lá, Favoritos já mostra o motivo (#1120). O aceite depende do #1122 (decisão de Alan).

    Visível no modal: "Promover a favorito" (ação/ETF) ou "Promover a favorito tier 3" (cripto). Abaixo do mercado aparecem a classe e a moeda, a precisão, as convenções, "Período efetivo …" e "Amostra <id8> · guardada enquanto o favorito existir · Direção Long". O destino de ação/ETF é "Favoritos · sem nível de estrela", com "Monitor, Telegram e Revalidar: ainda não para ações e ETFs". Depois de confirmar, a célula Ação mostra "Favorito · sem estrela" e o link "Ver em Favoritos" (44 px). A cripto mostra "Favorito tier 3", como hoje. O botão de confirmar ganha o foco ao abrir; Esc, Voltar e Fechar devolvem o foco ao Promover.

11. **Ranking numa lista só.** A ordem de hoje (GO acima de NO-GO, Calmar ou CAGR vs B&H, trades, id; `rank_eligible`, `discovery_service.py:1927-1990`) vale para todas as classes. As métricas são percentuais, sem moeda. Cada linha do Decidir e das Parciais ganha um bloco compacto abaixo do id, em duas linhas lógicas:
    - **identidade e precisão:** "NVDA · 1d · Long [Ação] USD ⚠ Precisão diária (2003–2025)". O símbolo entra porque hoje o Decidir não o mostra na linha. A precisão traz o trecho em anos; o trecho exato ("Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025") fica no `title` e em texto para leitor de tela, e aparece por extenso no modal, no "Por ativo" e em Favoritos. Intrabar: "ⓘ Precisão intrabar (15m)".
    - **convenções e período:** "Binance Ações · NY · split · 252/ano  2 jan. 2003 – 23 out. 2026" (as convenções de `conventionsShort`; o período efetivo leva o rótulo "Período efetivo" em `title` e para leitor de tela).

    Cada grupo (ativo · tempo · Long; classe + moeda; precisão; período) não quebra por dentro, e entre grupos não há "·", então nenhuma linha começa ou termina com separador nem deixa a moeda sozinha; nas convenções a quebra só cai antes de um "·". O bloco usa a largura que a coluna Candidato já tem (até 232 px a 1440; o resto da linha no cartão), e não os 180 px fixos de `.candidate-cell-min`; o mínimo de 180 px fica, então a tabela (`min-width: 1240px`) não cresce. Medido no protótipo (NVDA): o bloco cai de 167 para 71 px e a linha de 368 para 238 px a 1440 (754 → 603 px a 390). Na coluna de 232 px as duas linhas lógicas ocupam 4 linhas visuais; numa coluna mais larga, 2.

    Nunca duas moedas na mesma linha. O filtro **Classe** fica antes de Símbolo: "Todas (N)", "Cripto (N)", "Ações (N)", "ETFs (N)". Opção com contagem 0 fica desabilitada. Se a classe escolhida ficar sem candidato, a tabela mostra "Nenhum candidato de <classe> nesta varredura." com "Limpar filtros". O select Classe tem 44 px de altura abaixo de 768 px (os três selects vivos ao lado seguem com o reset incumbente, P3). O `leaderboard` aceita `asset_class` e devolve `class_counts`, com rank global preservado. "Limpar filtros" zera Classe. A faixa de filtros passa a 4 colunas + botão a partir de 768 px.

    Com mais de uma classe, o cabeçalho troca janela, candles e taxa da primeira linha por "3 classes · janela, candles e amostra em cada linha · taxa por lado: cripto 0,075% · ação e ETF 0,10% · slippage do timeframe". O estado do cabeçalho segue a varredura real (`STATE_LABEL` vivo: "em execução", "pausada", "concluída", "cancelada", "falha parcial"), nunca "em execução" depois do fim. `fees_slippage_record` passa a receber a classe. A nota do Preflight diz "taxa por lado: cripto 0,075% · ação e ETF 0,10% · …".

12. **Viés de sobrevivência em toda varredura (decisão de Alan no Design, 26/10/2026).** Toda janela da Descoberta termina no passado ou hoje e o "todos" usa só o catálogo de hoje (#1117), então o aviso aparece em toda varredura, com a janela. Preflight: "Viés de sobrevivência: a varredura usa só os ativos do catálogo de hoje. Ativos que saíram da Binance antes de hoje não entram, e a janela começa em 2 jan. 2003." Decidir: "… esta varredura usou só os ativos do catálogo de hoje (janela desde 2 jan. 2003). Ativos que saíram da Binance antes de hoje não estão no ranking." Usa o tom neutro (cinza, ícone de histórico), não âmbar: é limitação permanente, não alerta da execução. O preflight devolve `survivorship = {catalog_as_of, window}`. Alan escolheu, no comentário do issue durante o Design (26/10/2026), que o aviso aparece em toda varredura, e não só quando a janela termina antes de hoje. O spec `multiclass-discovery` já estava assim.

13. **Regressão de cripto.** Uma varredura só de cripto mantém as combinações, a amostra por ativo e tempo, as métricas, a elegibilidade (cobertura 24/7) e o ranking. Muda só o bloco de classe, moeda, precisão e convenções da linha e a nota de taxa por classe. Os testes de contrato cobrem:
    - varredura mista aceita;
    - NVDA congelado de `binance_equity` com `snapshot_id` igual em treino, tentativas e avaliação;
    - NVDA 1d em todo o histórico com precisão diária e trecho;
    - 4h de ação em 2019–2020 como amostra insuficiente "sem candles";
    - falha de coleta virando "Falha" depois de 3 tentativas;
    - teto com 2.433;
    - promoção de NVDA com `tier` nulo e chaves `analysis_*`;
    - cripto igual à de antes.

    O E2E Playwright de `/combo/discovery` com a API simulada segue o protótipo.

## Risks / Trade-offs

- [Varredura com milhares de ações coleta por horas] → o teto de 1.000 limita; o Preflight diz quantos precisam de coleta; a coleta é sequencial por combinação sob o limite do #1118 e a amostra é única por ativo e tempo (decisão 4).
- [Duas combinações do mesmo ativo começam juntas e as duas congelam] → o lock do sweep ao gravar `samples`; a perdedora descarta a sua referência (`snapshots.finish`) e lê a vencedora.
- [Cobertura pelo calendário de NY muda a elegibilidade de ação/ETF] → era a intenção; a cripto continua 24/7 e o teste de regressão garante.
- [Previsão de precisão diferente do resultado] → a previsão diz "prevista" e o ativo sob demanda fica sem previsão; a marca do resultado vem sempre da execução.
- [Favorito de ação/ETF antes do #1122] → Favoritos já mostra que atualização, Monitor, Telegram e Revalidar ainda não valem; o aceite espera o #1122.
- [Período padrão de 15 dias] → 1d de ação em 15 dias tem 10 velas e cai em amostra insuficiente com motivo; isso é o comportamento de hoje para cripto e fica explícito.
- [Servidor de protótipos lê os worktrees só ao iniciar] → `criptofarol-dev-prototypes.service` (`scripts/dev_prototype_server.py:36-49`) foi reiniciado depois deste worktree e a URL pública já serve o protótipo (o rework r1 foi validado nela).
- [Ordem do "Por ativo" muda durante a varredura] → o ativo em curso sobe para o topo e a linha viva anuncia só a etapa; com centenas de ativos, é o que evita procurar o ativo em curso na lista.

### P3 aceitos (detalhe de Apply)

- Nomes de campos e rotas: `by_class`, `collection`, `precision_forecast`, `survivorship`, `assets[]`, `class_counts`, `snapshot.samples`, chaves de `metrics`; a forma do evento de progresso da coleta.
- Onde o manifesto da amostra única fica (snapshot do sweep ou tabela própria) e o lock usado.
- Limiar exato de "poucas velas" (hoje `listing < 2` ou treino < 30) e o texto exato dos motivos.
- `evaluate_listing_sample` (`tasks/discovery_tasks.py:86-125`) infere `stooq` para ticker sem `/` e não tem chamador hoje: remover ou alinhar à fonte por classe.
- `_materialize_combinations` (`discovery_service.py:878-897`) só exclui combinações listadas em `exclusions`, que cortam o detalhe em 200: conferir que marcados além de 200 não viram combinação.
- Formato de número e data (o formatador vivo mistura "17 de ago. de 2017" no modal e "17 ago. 2017" na linha), ícones, ordem dos grupos do bloco do candidato, o formato do trecho em anos quando o trecho cabe num ano só.
- Amostra do protótipo: números, datas, ids de resultado e amostra, páginas de coleta, a estimativa "~81h", a lista de chips do cenário do teto (mostra só 3), os números da linha BTC/USDT 4h do período passado e o painel Demonstração (não vai para o produto).
- "Precisam de coleta" e "Precisão diária prevista" com centenas de ativos: truncar com "+N".
- `discovery-promotion`: o payload continua exigindo `tier: 3` e o servidor grava `tier` nulo para ação e ETF (decisão 10). A redação é contraintuitiva; o Apply documenta no teste.
- Com `overLimit`, o vivo troca a nota do escudo por `[data-testid=over-limit-note]`; o Apply decide se o bloco `.d21-limit` substitui essa nota, para não haver duas recusas.
- O chip do Acompanhando mostra `PARTIAL_FAILURE`/`COMPLETED` em caixa alta, como o vivo (`state.toUpperCase()`).
- `parse_live_route` do gate leva a linha seguinte (`surface: existing`) como justificativa; inofensivo com rota de catálogo (processo, fora do card, já apontado no #1120).
- Incumbentes fora do card, todos em COPIED:
  - reset `*` vivo que zera padding das utilidades: os selects Ordenar, Símbolo e Timeframe medem 18 px (o Classe, do delta, tem 44 px abaixo de 768 px) e os cartões do modal ficam sem padding;
  - tabela do Decidir e das Parciais com 1240 px num contêiner de 1175 px a 1440: Promover e Excluir ficam cortados até rolar (igual com e sem o delta);
  - tamanhos de 10/11 px dos chips e notas vivos que alcançam os `<span>` do delta ("Pronto para iniciar", `leaderboard-meta`, "Data Inicial/Final");
  - "slippage 0%" e "taxa 0,1%" do formatador vivo;
  - "+ detalhes", Símbolo e Timeframe sem ligação no protótipo;
  - logo do AppNav por caminho absoluto, que só carrega no domínio DEV;
  - achados do detector no AppNav e nos botões vivos.

## Migration Plan

1. Sem migração de tabela: `discovery_results` já tem as colunas de proveniência; `asset`, `execution` e `conventions` vão em `metrics` (JSON).
2. Deploy do servidor (Preflight, aquisição por classe, amostra única, cobertura por calendário, estado por ativo, filtro, promoção) e do front no mesmo deploy. Uma varredura em andamento no deploy termina com o caminho antigo (só cripto) e não ganha `assets[]`. O front mostra o painel antigo quando `assets` falta.
3. Resultados antigos sem `execution` mostram "Precisão: não registrada nesta varredura" no lugar da marca.

Rollback: voltar front e servidor devolve a recusa de ação/ETF na Descoberta. Varreduras e resultados de ação/ETF já gravados continuam no banco. Os favoritos promovidos continuam em Favoritos (#1120).

## Open Questions

Nenhuma aberta.

- **Resolvida — quando aparece o aviso de viés de sobrevivência?** Em toda varredura (opção A), por decisão de Alan no Design, 26/10/2026, no comentário do issue. Toda janela da Descoberta termina no passado ou hoje e o "todos" usa o catálogo de hoje. Registrada na decisão 12; o spec `multiclass-discovery` não muda.

As 4 decisões de Alan de 26/10/2026 estão no Entra: precisão diária marcada; teto de 1.000 que recusa e pede para estreitar; ranking único com USD e USDT separados; promoção como no lote, com aceite dependente do #1122. As escolhas de *como* estão nas decisões 1 a 13.

## Apply contract

O Apply lê este `design.md` e `frontend/public/prototypes/card-1121-descoberta-acoes-etfs/index.html` como spec de layout.

**Contrato visível (não P3):**

- **Montar:**
  - nota da classe e texto sob demanda da decisão 2;
  - Preflight com "Pronto para iniciar", total com ação e ETF, "Vão rodar" por classe e moeda, "Precisam de coleta", "Precisão diária prevista" e o aviso de sobrevivência;
  - recusa do teto com o total, as classes e "Estreite a seleção", com Iniciar desabilitado;
  - taxa por classe.
- **Acompanhando:**
  - "Por ativo" com os estados da decisão 7 (ícone + texto, desfecho misto com as duas contagens, cabeçalhos de coluna acima de 620 px e cartão abaixo, ativo em curso + falhas + insuficientes no topo, "Mostrar mais 50", linha viva só da etapa em curso);
  - Pausar, Retomar e Cancelar como hoje; depois de "Confirmar cancelamento" o foco vai ao título do progresso;
  - parciais só com resultados, com o bloco de classe, moeda, precisão, convenções e período efetivo.
- **Decidir:**
  - cabeçalho multiclasse com o estado real da varredura e aviso de sobrevivência;
  - nota "Sem resultado" (falha, não rodou) e "Amostra insuficiente" no cabeçalho, com "ver Por ativo";
  - filtro Classe com contagem, rank global preservado, opção 0 desabilitada, estado vazio com "Limpar filtros" e 44 px abaixo de 768 px;
  - bloco compacto do candidato da decisão 11;
  - amostra insuficiente sem rank e sem Promover;
  - falha fora do ranking;
  - nota de cobertura por calendário.
- **Modal:**
  - identidade da execução;
  - título e destino por classe;
  - foco no confirmar e retorno ao Promover;
  - célula "Favorito · sem estrela" + "Ver em Favoritos" (ação/ETF) ou "Favorito tier 3" (cripto).
- **Comportamentos dos specs:**
  - aceite por classe;
  - aquisição e congelamento por classe;
  - amostra única por ativo e tempo;
  - cobertura pelo calendário da classe;
  - "sem candles" como amostra insuficiente;
  - falha no orçamento de tentativas;
  - teto;
  - progresso da coleta;
  - promoção com `tier` por classe e chaves `analysis_*`;
  - regressão de cripto.

**P3 aceito (Apply):** os itens da subseção "P3 aceitos" em Risks / Trade-offs.

## Prototype

- Canônico: `frontend/public/prototypes/card-1121-descoberta-acoes-etfs/index.html`, clone de `/combo/discovery`. URL: https://dev.criptofarol.com.br/prototypes/card-1121-descoberta-acoes-etfs/
- **Montar:** BTC/USDT, NVDA e SPY, 1 template, 1d, Long, Todo o histórico. O Preflight mostra "Pronto para iniciar", 3 combinações, "Vão rodar 3 ativos", "Precisam de coleta 1 de 3 — SPY", "Precisão diária prevista em 1d: NVDA" e o viés de sobrevivência.
- **Iniciar varredura** abre o Acompanhando `#c1121mix`. "Por ativo" começa com BTC/USDT rodando e NVDA e SPY na fila.
- **Avançar uma etapa** leva NVDA a "Coletando histórico · 1d · página 3 de 6", depois a "Concluído · precisão diária". Em seguida, SPY passa por "Coletando · 5m do intrabar · página 7 de 16".
- **Pausar e Retomar** funcionam ("Pausado na coleta · … · retoma daqui"; o cabeçalho do Decidir diz "pausada"). **Cancelar** abre a confirmação viva, marca o resto "Não rodou · varredura cancelada" e leva o foco ao título do progresso; o Decidir diz "cancelada" e "Sem resultado: NVDA e SPY — Não rodou · varredura cancelada."
- **No fim**, a tela vai para o Decidir com foco no título e o cabeçalho "concluída": 3 candidatos com o bloco compacto (classe, moeda, precisão com o trecho em anos, convenções e período efetivo).
- **Classe = Ações** deixa só NVDA, rank 2. **Promover NVDA** abre "Promover a favorito", com a identidade por extenso, "Amostra 8b41d7e2" e "Favoritos · sem nível de estrela". Confirmar mostra "Favorito · sem estrela" + "Ver em Favoritos". BTC/USDT continua "tier 3".
- **Demonstração:**
  - "Período passado (2019–2020) · 1d e 4h": Personalizado com as datas; previsão "Sem candles prováveis em 4h: NVDA e SPY". No fim, o contador diz "6 processadas = 4 sucesso + 0 falha + 0 ignoradas + 2 amostra insuficiente"; no "Por ativo", NVDA e SPY "1 concluída · 1 amostra insuficiente" (no topo) com "1d: Precisão diária · … · 4h: Amostra insuficiente — sem candles de 4h de NVDA nessa janela (o 5m da Binance começa em 2 jan. 2026)" e BTC/USDT "Concluído · 2 de 2". O Decidir tem 4 linhas válidas (BTC/USDT 1d e 4h, NVDA 1d, SPY 1d), 2 linhas "Amostra insuficiente" sem Promover, "6 de 6 candidatos", "Cripto (2) · Ações (2) · ETFs (2)" e a nota "Amostra insuficiente: NVDA 4h e SPY 4h".
  - "Todos do filtro em Ações (2.431) + BTC/USDT + SPY": "Bloqueado — veja o que falta", 2.433, a recusa do teto e Iniciar desabilitado.
  - "SPY: coleta falha até o fim das tentativas": SPY sobe ao topo com "tentativa 2 de 3" e depois "Falha: a Binance não respondeu ao histórico de SPY nas 3 tentativas"; SPY sai do ranking. O Decidir diz "falha parcial", mostra "Sem resultado: SPY — Falha: …" com "ver Por ativo" e "ETFs (0)" desabilitado.
- Apoio: `live.css` (CSS vivo inteiro), `delta.css`, `delta.js`. Nenhuma página é painel ANTES/DEPOIS nem "N estados"; o painel Demonstração fica no fim, no fluxo.

## Prototype Validation

Evidência do autor, rework r1 (26/10/2026), que substitui a do a1. Qualquer mudança posterior nos arquivos abaixo a invalida.

- **Captura viva:** a do a1 (Playwright Python, Chromium headless shell 1243, `pt-BR`, tema escuro, `https://dev.criptofarol.com.br/combo/discovery` com a API simulada; Montar, Acompanhando, Decidir e modal a 1440 px e AppNav móvel a 390 px). O r1 remontou o `index.html` das mesmas capturas: toda região COPIED segue substring literal de uma captura (0 fora) e nenhum marcador cai dentro de tag. A única mudança de fronteira: "em execução" do `leaderboard-meta` passou de COPIED para DELTA, porque agora segue o estado real. `live.css` não mudou (sha `876e5fe6…`, igual ao CSS vivo).
- **Gate do clone** (`scripts/process-fsm/design_clone_gate.py`, catálogo do HEAD):
  - `design_token_gap` = None; tokens em L1–L3;
  - `evaluate_clone_gate` = True e `clone_gate_ok` = True;
  - `classify(index.html, /combo/discovery)` = PASS; os três textos do catálogo estão em COPIED;
  - `copied_utf8_sum` 70.219 B, DELTA 15.678 B, `index.html` 90.890 B; 38/38 pares COPIED e 38/38 DELTA.
- **`openspec validate card-1121-descoberta-acoes-etfs --strict`:** válido.
- **Arquivos (disco = URL pública):** `index.html` 90.890 B (`1d1b1d53…`) · `live.css` 241.100 B (`876e5fe6…`) · `delta.css` 11.874 B (`b2b9de59…`) · `delta.js` 45.113 B (`6959a969…`). Detector Impeccable CLI: 0 achados em `index.html`, `delta.css` e `delta.js`.
- **Browser gate na URL pública** (Playwright Python, 1440×900 e 390×844 com `isMobile` e toque, contexto novo por cenário): **148/148 asserts PASS** (74 por viewport), 0 `console.error`, 0 `pageerror`, 0 resposta ≥ 400, sem rolagem horizontal em nenhum estado. Cobre os cinco cenários (misto, período passado, teto, falha, cancelar) e, do r1:
  - Por ativo: cabeçalhos de coluna a 1440 e cartão a 390; ativo em curso, falha e insuficiente no topo; "1 concluída · 1 amostra insuficiente" com "2 de 2 combinações"; "Mostrar mais" oculto com 3 ativos;
  - período passado: contador "6 processadas = 4 sucesso + 0 falha + 0 ignoradas + 2 amostra insuficiente", 4 linhas válidas (BTC/USDT 4h com rank 4 e modal "BTC/USDT · 4h · Long"), "6 de 6 candidatos", "Cripto (2) · Ações (2) · ETFs (2)", ids de amostra `RS-NVDA1121E5`/`RS-SPY1121F6`;
  - Decidir: cabeçalho "pausada", "concluída", "falha parcial" e "cancelada"; nota "Sem resultado" (falha e cancelada) e "Amostra insuficiente"; "ver Por ativo" abre o quadro com foco no título;
  - filtro Classe: "ETFs (0)" desabilitado, estado vazio com "Limpar filtros", 44 px a 390;
  - bloco do candidato: nenhum grupo quebra por dentro; trecho exato no `title` e para leitor de tela; modal por extenso;
  - "Destino obrigatório" com o mesmo tamanho do irmão vivo; foco no título do progresso depois de "Confirmar cancelamento"; textos longos ≤ 75ch.
- **Altura da linha do candidato** (Decidir, cenário misto, antes → depois): a 1440, BTC/USDT 333 → 255 px, NVDA 368 → 238 px, SPY 422 → 292 px (bloco 132/167/167 → 88/71/71 px); a 390, 719 → 621, 754 → 603, 776 → 625 px. Parciais: 176 → 135 px a 1440 e 533/550 → 510 px a 390. A tabela continua com 1240 px e o Promover termina no mesmo x (1477) a 1440.
- Scripts no scratchpad do autor: `c1121r1/build.py` (+ `patch_build*.py`), `c1121r1/run_gate.py`, `c1121r1/gate_r1.py`, `c1121r1/measure.py`.

## Design Critique

Com-tela. Teto 1+1+1: autor, dupla A/B e 1 rework. O rework (r1) aplicou a decisão de Alan no Design e os P2 de produto e mecânicos da dupla. Não houve segundo rework.

- Autor: `design-autor 1121 r0` (isolado). Rework: `design-autor 1121 r1` (isolado).
- Assessment A: `assessment-a 1121 a2` (isolado; produto, UX, acessibilidade, fidelidade). Assessment B: `assessment-b 1121 a2` (isolado; detector + navegador). A primeira tentativa da dupla (`a1`) foi negada pelo hook antes de nascer (faltava `model_selection_wave_capture`) e não rodou.
- Verdict: **PASS** (A: PASS; B: PASS com rework, aplicado no r1). Tokens: `UI impact: affected` / `live_route: /combo/discovery` / `surface: existing`.
- Proto canônico: https://dev.criptofarol.com.br/prototypes/card-1121-descoberta-acoes-etfs/ (sem página extra: Favoritos não muda na tela).
- Snapshots: `.impeccable/critique/1121-card-1121-descoberta-acoes-etfs-A.md` e `…-B.md`. O Gist OpenSpec não é a crítica.

- **P0**: nenhum.
- **P1**: nenhum.
- **Juízo, decidido por Alan no Design** ([comentário](https://github.com/oalansilva/crypto/issues/1121#issuecomment-6406343490)), aplicado no r1:
  - O aviso de viés de sobrevivência aparece em toda varredura (decisão 12).
- **P2 de produto, corrigidos no r1**:
  - Por ativo mostra desfecho misto ("1 concluída · 1 amostra insuficiente"), não só "Concluído";
  - falha e "não rodou" ficam visíveis no Decidir ("Sem resultado: SPY — … ver Por ativo"), com o cabeçalho seguindo o estado real da varredura;
  - filtro Classe com 0 candidatos: opção desabilitada e estado vazio com "Limpar filtros";
  - Por ativo com "Mostrar mais 50", com o ativo em curso, as falhas e as amostras insuficientes no topo;
  - bloco de classe, moeda, convenções e precisão do candidato compactado em duas linhas lógicas (bloco de 167 → 71 px a 1440).
- **P2 mecânicos, corrigidos no r1**: estados do spec "Per-asset state" alinhados à decisão 7; cabeçalhos do Por ativo acima de 620 px e rótulo por célula para leitor de tela; contagens do cenário período passado (linha BTC 4h); filtro Classe com 44 px a 390; tamanho de "Destino obrigatório", foco depois de "Confirmar cancelamento", id de amostra, `75ch` e `nowrap` de chip + moeda.
- **P3 aceitos, para o Apply**: os itens da subseção de P3 aceitos em Risks / Trade-offs, mais os achados do detector nos HTML em regiões COPIED do incumbente (selects de 18 px, cartões do modal sem padding, tabela de 1240 px num contêiner de 1175 px).
- **Disposition:** o delta visível fica na Descoberta (`/combo/discovery`): seleção mista no Preflight, teto de 1.000 com pedido para estreitar, precisão diária com marca, estado por ativo, ranking único com classe/moeda/convenções e filtro por classe, promoção a favorito e aviso de viés. Atualização e alertas de favoritos de ação/ETF ficam para o #1122 (aceite deste card depende dele); benchmark e exportação, para o #1123.

### Proxies

- `design.md` words: 6276 (antes desta seção)
- HTML generated vs copied (`index.html`): 15678 vs 70219
- Spawns: 4 (design-autor r0, assessment-a a2, assessment-b a2, design-autor r1); mais 2 nascimentos negados pelo hook (`assessment-a/b 1121 a1`)
