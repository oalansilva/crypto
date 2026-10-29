UI impact: affected
live_route: /combo/discovery
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card [#1118](https://github.com/oalansilva/crypto/issues/1118), segunda história do épico [#1116](https://github.com/oalansilva/crypto/issues/1116). O briefing é o issue grelhado, com as 5 decisões de Alan de 22/10/2026 já gravadas no body, mais as 2 decisões de Alan no Design ([comentário de 23/10/2026](https://github.com/oalansilva/crypto/issues/1118#issuecomment-6354593360)): coleta de ação/ETF só pela consulta até o #1119 (decisão 5) e favorito com a amostra do último refresh (decisões 14 e 18). Não houve reentrevista. O *como* abaixo foi conferido em `develop` @ a1a699d3 (pós-#1117).

Estado atual:

- **Dois históricos da mesma série.** O gráfico (`GET /market/candles`, `backend/app/api.py`) só aceita cripto e lê `market_ohlcv` (Timescale) no modo canônico. Backtest, combo (`combo_optimizer.py`), otimização (`sequential_optimizer.py`) e descoberta (`discovery_inputs.py`) leem pelo `IncrementalLoader` (`src/data/incremental_loader.py`), que baixa direto pela CCXT e grava Parquet em `data/storage/binance/<SÍMBOLO>_<tf>.parquet`. Não há regra que sincronize as duas cópias.
- **`market_ohlcv` apaga histórico.** `backend/app/database.py` aplica `add_retention_policy('market_ohlcv', INTERVAL '2 years')` e compressão depois de 30 dias. A unicidade é `(symbol, timeframe, candle_time)`; `source` não entra na chave, então duas fontes ou dois ajustes se sobrescrevem.
- **Escritor canônico de cripto.** `OhlcvIngestionService` (`ohlcv_storage.py`) mantém todos os pares USDT em 15m, 1h, 4h e 1d (spec `market-candles`). Continua neste card: é cripto e não é lote de ações.
- **Amostra da Descoberta.** `discovery_inputs.prepare` congela candles e 15m em Parquet com SHA-256 por combinação, num spool de até 2 GiB, e `discovery_recovery` apaga os bytes quando a combinação termina (`inputs_cleaned`). Não há reprodução exata depois disso.
- **Refresh diário dos favoritos.** `runtime_worker.py` sobe `favorite_backtest_refresh_loop` (`favorite_backtest_refresh_service.py`): a cada hora (`FAVORITE_BACKTEST_REFRESH_LOOP_SECONDS` = 3600) pega os favoritos com o último refresh há mais de 24 h (`…_INTERVAL_SECONDS` = 86400), no máximo 12 por passada e com pausa se a CPU passar de 60%. `refresh_favorite` trava a linha (`with_for_update`), prepara os candles pelo provedor (`_prepare_market_data`: timeframe do favorito e 15m), roda `ComboOptimizer.run_optimization` com os parâmetros fixos e `deep_backtest=True` até hoje, e grava `favorite.metrics` (o número de `/favorites`) e `auto_backtest_runs.stage_3_result` num único commit. Se falhar, `favorite.metrics` fica como estava e o run fica `FAILED`.
- **Seletor (#1117).** `asset_catalog_service.serialize_item` devolve cripto como `local` (intervalo 1d de `market_ohlcv`) ou `on_demand`, e ação/ETF como `not_collected`. `historyText` (`assetSelection.ts`) mostra "Histórico não coletado". As análises recusam ação/ETF com `asset_class_not_supported` até o #1119.
- **Binance de ações.** Rota pública do gráfico `/bapi/equity/v1/public/equity/kline/chart`, `limit=1000`, paginação `endTime=min(t)-1`, erro de negócio com HTTP 200 (code 488006), `startTime` sem semântica Spot, sem 15m nativo (`1T`, `5T`, `10T`, `30T`, `1H`, `2H`, `4H`, `1D`, `1W`, `1M`), sessões `ETH`/`DAY_EXTENDED` observadas e tratamento de dividendos em `ADJUSTED` não verificado. `market_data_providers.py` só tem CCXT e Stooq na fábrica.

Medidas (22/10/2026, DEV):

- Cache Parquet atual: 2.491 arquivos, 1,8 GB. O 15m é 1,6 GB (720 pares); 1d 42 MB; 1h 47 MB.
- BTC/USDT 15m: 321.399 candles desde 17 ago. 2017 em 14,4 MB, ou 44,8 B por candle em Parquet. 1d: 3.354 candles; 1h: 80.363; 4h: 20.107.
- O 15m de cripto em Parquet soma por volta de 36 milhões de candles (1,6 GB ÷ 44,8 B).
- NVDA 1d na Binance: 3 páginas, 3.000 candles de 11 nov. 2014 a 16 out. 2026 (épico).
- O tamanho de `market_ohlcv` em DEV não foi medido: o banco usa autenticação *peer* do usuário do serviço. O Apply mede antes da migração (tarefa 1.1).

**Audience:** Alan, que monta análises e precisa confiar no período.
**Outcome:** gráfico e análises leem a mesma série; ação e ETF têm histórico Binance consultável e com cobertura informada; cada execução tem amostra estável e diz se pode ser refeita igual.
**Direction:** clone+delta Operate no seletor vivo do #1117. Tokens do produto, sem mundo visual novo.
**Scope:** autoridade, coleta, calendário, versão, cache, amostra e cobertura no seletor e no Decidir. Fora: rodar análise com ação/ETF (#1119+), gráfico de ação/ETF, retirada de provedores (#1126).

Regiões clonadas da página viva, só estas (capturadas em `https://dev.criptofarol.com.br` com a API simulada, a 1440 e a 390 px, e marcadas com `COPIED:start`/`COPIED:end`):

- `index.html` (canônico, `/combo/discovery`): fundo e AppNav desktop; AppNav móvel; conteúdo vivo (breadcrumb, título, "Histórico de varreduras", abas, Rascunho com Templates, cabeçalho do seletor, busca, filtros de classe, paginação, ações, selecionados, Timeframes, Direção, Período, Ranking e Preflight); aba Decidir viva (varredura concluída, leaderboard com 2 resultados); restos da linha de evidência e dos dois resultados; nota de classe do componente (texto do `classNote`).
- `combo.html` (extra, `/combo/configure`): fundo e AppNav desktop; AppNav móvel; conteúdo vivo (Template Information, Configuration com o seletor, Timeframe, Período, Direction, Deep Backtest, walk-forward, dica de período, Parameter Optimization Ranges, Otimizar).
- `optimize.html` (extra, `/combo/optimize`): fundo e AppNav desktop; AppNav móvel; conteúdo vivo (Configuration com o seletor estreito, Timeframe, Parameter Ranges, Run Optimization, painel "Ready to Optimize").
- `live.css`: regras do CSS vivo usadas por essas telas (poda do bundle `index-CElzlQFP.css` pelas capturas).

O delta fica só nos blocos `DELTA:start`/`DELTA:end`: as linhas do seletor (renderizadas por `cobertura.js` com o fato de histórico, o botão "Cobertura" fora do `<label>` e o detalhe por timeframe), a proveniência e o estado da amostra na evidência e nos resultados do Decidir, e o painel "Demonstração" no fim de cada página.

## Goals / Non-Goals

**Goals:**

- Uma autoridade de candles (PostgreSQL) para gráfico e análises, em cripto, ação e ETF, com série identificada por ativo, fonte, sessão, ajuste e timeframe.
- Histórico Binance de ação e ETF coletado sob demanda, validado, com limite de requisições, retomada e calendário de Nova York, só no pregão regular.
- 15m de ação/ETF montado do 5m e marcado como derivado.
- Versão por série: correção e evento corporativo valem nas próximas consultas e não mudam execução em andamento.
- Cache Parquet derivado e reconstruível.
- Amostra estável por execução; o favorito guarda a amostra do último refresh diário; os demais por 30 dias.
- Cobertura visível no seletor e estado da amostra no Decidir.
- Migração da cripto sem perder histórico nem quebrar favoritos e resultados.

**Non-Goals:**

- Rodar backtest, combo, otimização ou descoberta com ação ou ETF (#1119 a #1121). A recusa `asset_class_not_supported` continua.
- Gráfico de candles de ação e ETF. `/market/candles` continua só cripto.
- Retirar Stooq, Yahoo e Alpha Vantage (#1126) ou provedores antes da migração dos consumidores.
- Pré e pós-mercado; coleta em segundo plano de favoritos; lote diário do catálogo de ações e ETFs.
- 1h e 4h de ação e ETF: entram com a análise dessas classes (#1119), pela mesma regra do 15m.
- Botão de "refazer igual" na tela: a reprodução fica disponível no serviço e na API (decisão 1 limita o delta visível ao seletor; o Decidir só mostra o estado da amostra).

## Decisions

1. **Página primária = `/combo/discovery`; extras `/combo/configure` e `/combo/optimize`.** As três têm o mesmo seletor com o delta visível, então cada uma ganha clone próprio. O index não é painel das três. O Decidir fica no index porque é a mesma rota (aba). Alternativa rejeitada: clonar o protótipo do #1117, que não é a página viva atual.

2. **Autoridade = PostgreSQL/Timescale, Parquet como cache.** A tabela `market_ohlcv` passa a ser o histórico guardado das três classes. Motivos: já é a fonte do gráfico, tem upsert idempotente para vários workers, compressão nativa e backup do banco; Parquet sem lock coordenado não aguenta coletas concorrentes. Custo estimado: 36 milhões de candles de 15m de cripto ocupam 4 a 5 GB sem compressão (110 a 140 B por linha com índice) e por volta de 0,4 a 0,7 GB comprimidos (10 a 20 B por linha); as ações crescem só sob demanda (NVDA 1d = 3.000 linhas; 5m = 19.656 linhas por ano por ativo). A política de retenção de 2 anos sai (spec `ohlcv-storage`), porque apagaria o histórico; a compressão depois de 30 dias fica. Alternativas rejeitadas: Parquet como autoridade (concorrência e backup) e duas cópias completas (é o problema de hoje).

3. **Identidade de série.** Nova tabela `market_series` (`series_id`, `asset_id` do catálogo, `source` = `binance_spot` | `binance_equity`, `session` = `24x7` | `rth`, `adjustment` = `na` | `adjusted` | `raw`, `timeframe`, `origin` = `native` | `derived`, `data_version`, estado da coleta). `market_ohlcv` passa a ter chave `(series_id, candle_time)`. Como a chave primária de uma hypertable comprimida não muda no lugar, o Apply cria a hypertable nova, copia, confere e troca os nomes (`market_ohlcv` → `market_ohlcv_legacy`, nova → `market_ohlcv`). As colunas `symbol`, `timeframe` e `source` ficam para leitura de compatibilidade até o #1126.

4. **Um serviço de histórico para todos.** `HistoryService.read(series, janela)` devolve candles e cobertura (pedido, coberto, lacunas, atualização, versão, nativo/derivado, insuficiente). `ensure(series, janela)` coleta só o que falta antes de ler. O gráfico (`/market/candles`), o `IncrementalLoader` (modo leitura, sem CCXT), `combo_optimizer`, `sequential_optimizer` e `discovery_inputs` passam a chamar esse serviço. Nova consulta `GET /market/history` (autenticada) atende qualquer classe e é a "consulta" de ação/ETF neste card. O escritor de cripto existente grava nas séries `binance_spot`.

5. **Coleta sob demanda e quem a dispara (decidido por Alan em 23/10/2026).** Até o #1119 aceitar ação e ETF nas análises, essas classes só coletam por consulta direta: `ensure` é chamado por `GET /market/history` e, a partir do #1119, pela análise que aceitar a classe. Análise recusada por classe (`asset_class_not_supported`) não chama `ensure`, e catálogo, filtro, busca e "Todos do filtro" também não. Por isso não há teto novo em "Todos do filtro" neste card: "Todos do filtro" em ETFs seguido de Iniciar não coleta nenhum dos 3.112 ETFs. Na tela, o estado sob demanda de ação/ETF diz "Histórico sob demanda · a coleta começa quando as análises aceitarem ações" (ou "ETFs"), sem botão nem outro gatilho. Cripto sob demanda diz "Histórico sob demanda · coletado quando uma análise pedir", porque as análises já aceitam cripto.

6. **Coleta que retoma.** `market_series_fetch` guarda por série a direção, o cursor (`endTime` da próxima página), páginas feitas, estado, último erro e tentativas. Cada página é gravada com upsert na mesma transação que avança o cursor. Uma coleta por série, por `pg_try_advisory_lock(series_id)`; quem não pega o lock espera até 30 s lendo o que já foi gravado e devolve a cobertura atual. Reinício retoma do cursor. Atualização: busca a página mais recente e anda para trás até sobrepor o que existe.

7. **Adaptador Binance de ações (`BinanceEquityProvider`).** Validação por página: `code == "000000"`; `data.bars` lista; `t`, `ct`, `o`, `h`, `l`, `c`, `v` numéricos; `ct - t + 1` igual à duração do timeframe; `l ≤ min(o,c)`, `h ≥ max(o,c)`, preços > 0, volume ≥ 0; `t` único e ordenado; nada depois do `endTime` pedido. Outro `code` com HTTP 200 vira `BinanceBusinessError(code)`; campo ausente vira `formato da Binance mudou`. Página inválida não grava nada. Página vazia com `000000` é pedida de novo uma vez antes de virar "início do histórico na Binance". Limite: balde de fichas no PostgreSQL (uma linha por fonte, `SELECT … FOR UPDATE`), 2 req/s para ações, 2 séries coletando ao mesmo tempo; 429/418 respeitam `Retry-After`; 3 falhas seguidas (429, 418, 5xx) abrem o circuito por 5 min e a cobertura fica "falha temporária". Cripto continua pela CCXT com `enableRateLimit`. Custo de tempo: NVDA 1d completo = 3 páginas (1,5 s); 1 ano de 5m = 20 páginas (10 s).

8. **Pregão regular e calendário.** Calendário XNYS da biblioteca `exchange_calendars` (pregões, feriados, meio-pregões, fuso `America/New_York`, horário de verão). Candles gravados em UTC. O filtro local é a autoridade: só entram candles de 5m dentro da janela do pregão; o resto é descartado sem virar lacuna. O parâmetro de sessão da Binance que já devolve só o regular é verificado no Apply (tarefa 2.2); sem ele, pede-se o modo que traz o pregão inteiro e filtra-se. O 1D precisa bater com o pregão regular (abertura das 09:30 e fechamento das 16:00 contra o 5m agregado em 20 pregões de NVDA e SPY); se a Binance só tiver 1D com pré/pós, o 1d de ação/ETF não é exposto e o Apply para com P0 visível. Lacuna = candle esperado pelo calendário que não veio.

9. **15m derivado na leitura.** Montado do 5m na hora de ler, em blocos de 3 ancorados às 09:30 de Nova York, sem atravessar o fechamento (meio-pregão termina às 13:00). Bloco com 5m faltando sai marcado incompleto e aparece como lacuna do 15m, "herdada do 5m". Essa lacuna não soma de novo no resumo da linha do seletor: o resumo conta só lacunas de séries nativas, porque a falta é uma só. A versão do 15m é `(versão do 5m, versão da regra)`. Não é gravado como série nativa, para não duplicar dados.

10. **Ajuste.** Ação/ETF usa `adjusted` (Binance `ADJUSTED`) por padrão; `raw` é outra série e só existe se pedida. Verificação no Apply: NVDA 1d sem salto entre 7 e 10 jun. 2024 (split 10:1); SPY comparado nos ex-dividendos de 2025 entre `ADJUSTED` e o modo sem ajuste para saber se dividendos entram. O rótulo da série diz o que foi verificado ("ajustado por split" ou "ajustado por split e dividendo").

11. **Versão e correções.** Cada atualização rebusca a página mais recente já guardada e compara candle a candle (tolerância relativa 1e-9). Diferença em candle antigo (split, dividendo, correção) recoleta a série numa tabela de preparo e troca tudo numa transação, com `data_version + 1`. Leitores em transação veem uma versão inteira. Cache e amostra usam a versão na chave, então nada mistura páginas de versões diferentes.

12. **Cache Parquet derivado.** Caminho `data/storage/series/<series_id>/v<versão>/<tf>.parquet`, escrito de forma atômica a partir do PostgreSQL. Versão nova = arquivo novo; o antigo some no próximo varrimento. Teto de 3 GiB com descarte por último acesso (hoje são 1,8 GB). Apagar o diretório só faz o próximo pedido refazer o arquivo, sem chamar a Binance.

13. **Amostra por segmentos com SHA-256.** No início de uma execução (backtest, combo, otimização, descoberta), o serviço congela a janela em segmentos mensais por `(série, versão, mês)` em Parquet, gravados uma vez em `data/snapshots/segments/<sha[:2]>/<sha>.parquet`, e um manifesto em `execution_data_snapshots` (série, versão, janela, lista de segmentos, criação, `retain_until`, `pinned`). Todas as tentativas leem só do manifesto (o `FrozenProvider` atual passa a ler segmentos e confere o SHA-256). Na descoberta, isso substitui o spool `inputs-*` por combinação e o `inputs_cleaned`. Meses fechados são compartilhados entre execuções; só o mês corrente muda.

14. **Prazo de 30 dias para resultados não favoritados.** Custo medido: 15m de cripto = 44,8 B por candle; 2 anos de 15m = 70.080 candles ≈ 3,1 MB; um mês ≈ 130 KB. Uma varredura de 30 pares em 2 anos grava ≈ 126 MB na primeira vez e ≈ 6 MB nas seguintes (só o mês corrente). Em regime, 30 dias ficam abaixo de 0,5 GB no uso típico e nunca passam muito de 1,6 GB (o 15m inteiro de cripto, todos os meses distintos). 90 dias custariam pouco mais, mas guardariam amostra de varreduras que ninguém mais revisa; 7 dias seriam curtos para quem revisa o Decidir na semana seguinte. Regra única de prazo por manifesto: `retain_until` = 30 dias depois do mais tarde entre o fim da execução e o momento em que o manifesto deixou de ser a amostra de um favorito (desfavoritar ou ser trocado pelo refresh, decisão 18). Manifesto apontado por `favorite_strategies.snapshot_id` tem `pinned = true` e não vence. Na promoção, o favorito copia o `snapshot_id` do resultado; essa amostra só vale até o primeiro refresh, que a troca (decisão de Alan de 23/10/2026: a amostra da promoção deixa de ser a referência). Um job diário apaga manifestos vencidos e depois segmentos sem referência.

15. **Proveniência no resultado.** `discovery_results` e as métricas de favoritos ganham `data_source`, `asset_class`, `session`, `adjustment`, `timeframe_origin`, `period_requested`, `period_covered`, `data_version` e `snapshot_id`. `candle_source`/`candle_version` passam a ser preenchidos pela série ("Binance Spot", versão). Resultados e favoritos antigos ficam como estão e são tratados como "sem amostra guardada".

16. **Cobertura no seletor.** `market_series_coverage` (por série: início, fim, lacunas, atualização, estado e último pedido) é atualizada nas gravações, para o catálogo não varrer a tabela de candles. `serialize_item` devolve `history.status` = `on_demand` | `collecting` | `covered` | `partial` | `failed` | `frozen` e a lista por timeframe. Textos:
   - sob demanda: ação "Histórico sob demanda · a coleta começa quando as análises aceitarem ações", ETF idem com "ETFs", cripto "Histórico sob demanda · coletado quando uma análise pedir" (decisão 5);
   - coberto, com início comum a todos os timeframes: "Histórico desde DD mmm. AAAA · N timeframes · sem lacunas|N lacunas · atualizado DD mmm., HH:MM";
   - coberto, com inícios diferentes: o "desde" diz de qual timeframe é, por grupo, por exemplo "1d desde 11 nov. 2014 · 5m e 15m desde 19 mai. 2026 · sem lacunas · atualizado …". Nunca um "desde" só para todos quando o intraday começa depois;
   - "N lacunas" conta só lacunas de séries nativas: o 15m derivado mostra a sua como "herdada do 5m" na tabela, sem somar (decisão 9);
   - "Coletando histórico · 1d, página 2 · pedido às HH:MM";
   - "Coleta falhou DD mmm., HH:MM · motivo · já coletado: 1d desde …";
   - "Parcial: pedido desde …; a Binance tem desde …".

   O botão "Cobertura" (`aria-expanded`, `aria-controls`) abre a tabela por timeframe: período coberto, lacunas com data e hora, atualização e origem ("nativo" ou "montado do 5m", com o selo "derivado"), mais a linha "Binance Ações · pregão regular de Nova York · ajustado. Mercado fechado não conta como lacuna." Enter e Space alternam; Esc, com o foco no botão ou dentro da tabela, fecha e devolve o foco ao botão. Fuso declarado: lacunas de ação/ETF no horário de Nova York, escrito na própria célula ("10:05–10:40, horário de Nova York"), porque o pregão é definido lá; a coluna de atualização diz o fuso local do navegador no rótulo ("Atualizado (Brasília)" no protótipo); lacunas de cripto, quando houver, no fuso local. A linha selecionável vira `<div class="ap-row">` com `<label for>` no nome e a linha inteira clicável, porque um segundo controle (o botão) dentro do `<label>` é HTML inválido. "Histórico não coletado" deixa de existir. O texto vale para as três classes, porque a cripto passa a ter a mesma autoridade.

17. **Decidir.** A linha de evidência troca "ccxt v1" pela série ("Binance Spot · 1d nativo · v7") e acrescenta "amostra guardada até DD mmm. AAAA; favoritos guardam a amostra do último refresh". Cada resultado diz o estado da própria amostra da varredura ("amostra até …" ou "não reproduzível exatamente"); resultado favoritado acrescenta "favorito: Favoritos guarda a amostra do último refresh", porque o número que se refaz igual é o de `/favorites`, não o da varredura (decisão 18). Vencido, a evidência diz "amostra expirada em …: não reproduzível exatamente". O estado da amostra usa 11 px na evidência e nos resultados (o tamanho do `.candidate-meta` vivo), não os 10 px do resto da linha de evidência.

18. **Refresh diário do favorito troca a amostra (decidido por Alan em 23/10/2026).** Reusa o fluxo vivo descrito no Contexto, sem loop novo nem coleta nova:
   - `_prepare_market_data` passa a chamar `HistoryService.ensure` da série do favorito (para cripto, o escritor canônico já mantém a série; `ensure` só completa o fim que falta, como o provedor faz hoje). Favorito de ação/ETF não existe antes do #1119, então este card não acrescenta coleta em segundo plano dessas classes (Não entra).
   - `ComboOptimizer.run_optimization` congela a amostra no início, como toda execução (decisão 13); o manifesto novo nasce com `pinned = false` e `retain_until` = fim da execução + 30 dias.
   - No mesmo commit que grava `favorite.metrics`: `favorite_strategies.snapshot_id` passa ao manifesto novo (`pinned = true`), `auto_backtest_runs.snapshot_id` guarda o mesmo manifesto, e o manifesto substituído fica `pinned = false` com `retain_until` = troca + 30 dias (regra da decisão 14). Assim, refazer igual reproduz o número que aparece em `/favorites`.
   - Refresh que falha não troca nada: o favorito continua com a amostra e o número anteriores, que seguem coerentes entre si. O manifesto da tentativa falha não sustenta número nenhum e recebe `retain_until` = momento da falha, para o GC levar.
   - Por que 30 dias para a amostra substituída, e não apagar na hora: `auto_backtest_runs.stage_3_result` guarda o número de cada refresh, então o número de ontem continua visível no histórico de runs; 30 dias é a mesma regra dos não favoritos. Custo: meses fechados são segmentos compartilhados; cada refresh grava só o segmento do mês corrente (≤ 130 KB no 15m de cripto), então cada favorito soma no máximo 30 × 130 KB ≈ 4 MB em regime.
   - Favorito antigo (sem amostra) ganha amostra no primeiro refresh depois desta mudança; até lá, não promete reprodução exata.

## Risks / Trade-offs

- [Rota BAPI interna sem contrato] → adaptador isolado, validação estrita, falha visível e circuito; nenhuma página inválida vira dado.
- [1D da Binance pode incluir pré/pós] → verificação obrigatória (decisão 8); se falhar, 1d de ação/ETF não é exposto e o Apply para com P0.
- [Tratamento de dividendo desconhecido] → verificação com SPY e rótulo honesto (decisão 10).
- [Crescimento do PostgreSQL sem a retenção de 2 anos] → compressão aos 30 dias, coleta de ações só sob demanda, medida do tamanho antes e depois da migração (tarefa 1.1) e alerta acima de 80% do disco.
- [Troca da hypertable em PROD] → janela com o escritor parado, cópia conferida por contagem e soma por série, troca de nomes reversível; segue `docs/prod-migration-runbook.md`.
- [Parquet e tabela divergem na migração] → divergência registrada; vale a tabela; a chave não vira com divergência acima de 0,01% dos candles de uma série.
- [Amostra de execução enche o disco] → segmentos compartilhados, teto de alerta em 5 GiB e GC diário; o prazo não encurta sozinho.
- [Cobertura no seletor fica velha] → atualizada na gravação, com hora visível.
- [Cores âmbar, azul e vermelha (`#fbbf24`, `#93c5fd`, `#ff8294`) fora do `DESIGN.md`] → vêm do `AssetPicker.css` vivo; o hook do Impeccable as sinaliza e elas ficam como estão para manter o incumbente. O painel de demonstração usa cores próprias e não vai para o produto.

## Migration Plan

1. Medir `market_ohlcv` (linhas e bytes por timeframe e fonte) e o cache Parquet em DEV e PROD.
2. Criar `market_series`, a hypertable nova, `market_series_fetch`, `market_series_coverage`, `execution_data_snapshots` e a coluna `favorite_strategies.snapshot_id` (Alembic).
3. Remover a política de retenção de 2 anos de `market_ohlcv` antes de qualquer cópia.
4. Copiar `market_ohlcv` para a nova (série `binance_spot`, `24x7`, `na`) e importar do Parquet só os candles que faltam (Binance via CCXT, mesma fonte). Registrar divergências.
5. Conferir por série: contagem, primeiro e último candle e soma de fechamento. Trocar os nomes.
6. Ligar `MARKET_HISTORY_UNIFIED=1`: gráfico e análises passam pelo `HistoryService`; o cache novo é materializado sob demanda.
7. Regressão de cripto (gráfico, backtest, combo, otimização, descoberta) com o histórico existente; comparar um backtest de BTC/USDT antes e depois.
8. O cache antigo `data/storage/binance` fica só leitura por uma release e é apagado depois.

Rollback: desligar `MARKET_HISTORY_UNIFIED` volta os consumidores ao caminho antigo; `market_ohlcv_legacy` e o Parquet antigo continuam lá até o fim da release. Sem a política de retenção, nada se perde no rollback.

## Open Questions

Nenhuma de produto. A questão "análise recusada coleta?" foi decidida por Alan em 23/10/2026 (só a consulta coleta até o #1119; decisão 5), e a amostra do favorito também (último refresh; decisões 14 e 18).

## Apply contract

O Apply lê este `design.md` e os HTML em `frontend/public/prototypes/card-1118-historico-binance/` como spec de layout.

**Contrato visível (não P3):**

- O fato de histórico em cada linha do seletor, nas três telas, com os estados sob demanda (com o texto da classe), coletando, coberto (com lacunas e atualização), parcial, falha ("já coletado: …") e congelado (marcado), e sem "Histórico não coletado".
- Resumo da linha: "desde" por timeframe quando os inícios diferem; lacunas contadas só nas séries nativas.
- Botão "Cobertura" fora do `<label>`, com `aria-expanded`, alvo ≥ 24 px (32 px no protótipo), por teclado (Enter/Space alternam, Esc fecha e devolve o foco), sem marcar o ativo; tabela por timeframe com período, lacunas com data, hora e fuso, atualização com o fuso no rótulo e origem; 15m com "montado do 5m", selo "derivado" e lacuna "herdada do 5m"; linha de fonte, sessão e ajuste; layout que cabe na coluna estreita da Otimização e a 390 px.
- Decidir: proveniência da série na evidência, "amostra guardada até …; favoritos guardam a amostra do último refresh", "favorito: Favoritos guarda a amostra do último refresh" e "não reproduzível exatamente", com o estado da amostra a 11 px.
- Comportamentos dos specs: mesma série em todo lugar, sem coleta por seleção nem por análise recusada, período honesto, retomada, calendário, pregão regular, 15m derivado, versão, cache reconstruível, amostra estável, favorito com a amostra do último refresh e 30 dias.

**P3 aceito (Apply):** nomes de tabelas, colunas, serviços e rotas internas; forma da troca da hypertable; balde de fichas no PostgreSQL ou equivalente com o mesmo limite; caminho dos arquivos de cache e segmentos; teto de 3 GiB do cache; tolerância 1e-9; formato exato das datas (o do `formatDate` vivo); ordem dos fatos na linha; ícone da seta do botão; textos da Demonstração (não vão para o produto); a nota de classe continua igual; números de catálogo e coberturas do protótipo são amostra.

**P3 aceitos da dupla (Apply):**

- `role=status` da coleta em andamento é re-renderizado a cada filtro ou página e reanuncia o progresso; o Apply anuncia só quando o progresso muda.
- Demais motivos de falha: o protótipo só mostra "limite de requisições da Binance"; o Apply escreve os textos de indisponibilidade, erro de negócio (sem mostrar o código `488006` cru) e "formato da Binance mudou".
- Total de páginas no paginador e no "página N" da coleta: opcional no Apply.
- Coluna Ação cortada no Decidir a 1440 px ("Promover"/"Excluir" dentro do contêiner da tabela): vem do clone vivo, não do delta.
- O botão "Cobertura" dentro do `<label>` foi corrigido no protótipo (decisão 16); o Apply segue a mesma estrutura no `AssetPicker.tsx`.

## Prototype

- Canônico: `frontend/public/prototypes/card-1118-historico-binance/index.html`, clone de `/combo/discovery`. Vista inicial: Montar, seletor com BTC/USDT e ETH/USDT cobertos, NVDA coberto ("1d desde 11 nov. 2014 · 5m e 15m desde 19 mai. 2026"), SPY com 1 lacuna, QQQ coletando e AAPL sob demanda ("a coleta começa quando as análises aceitarem ações"). Interações:
  - "Cobertura" em NVDA → tabela com 1d, 5m e 15m "montado do 5m" (derivado);
  - "Cobertura" em SPY pelo teclado → lacuna de 14 out. 2026, 10:05–10:40, horário de Nova York, no 5m e o bloco 10:00–10:45 "herdada do 5m" no 15m; SPY continua fora da seleção; Esc fecha e devolve o foco ao botão;
  - "Próxima" → IBIT "Parcial", SOL/BNB cobertos, MSFT/TSLA sob demanda e WAVES/USDT marcado com histórico congelado;
  - Demonstração → QQQ "Concluída" ou "Falhou (limite da Binance)" ("já coletado: 1d desde 05 jan. 2023");
  - aba Decidir → evidência com "Binance Spot · 1d nativo · v7" e "amostra guardada até 21 nov. 2026; favoritos guardam a amostra do último refresh"; Demonstração → "Passou de 30 dias" e "BTC/USDT favoritado" ("favorito: Favoritos guarda a amostra do último refresh").
- Extra `combo.html`: clone de `/combo/configure` com o mesmo delta no seletor (BTC/USDT selecionado, como no vivo). A Demonstração dessas duas telas diz que o estado da amostra fica no Decidir da Descoberta, que elas não têm.
- Extra `optimize.html`: clone de `/combo/optimize` com o seletor estreito; a tabela de cobertura reorganiza em duas colunas pela largura da coluna.
- Arquivos de apoio: `live.css` (CSS vivo podado), `cobertura.css` e `cobertura.js` (delta e demonstração).
- Nenhuma página é painel ANTES/DEPOIS nem "N estados"; o painel Demonstração fica no fim, no fluxo, sem `position:fixed`.

## Prototype Validation

Evidência do autor, rework r1 (23/10/2026). O `index.html` não mudou no rework (o delta dele é renderizado por `cobertura.js`); mudaram `combo.html` e `optimize.html` (texto da Demonstração), `cobertura.css` e `cobertura.js`.

| Arquivo | Bytes | sha256 | COPIED | DELTA |
|---|---|---|---|---|
| `index.html` (canônico) | 47.342 | `5db21b21c59f4fd41df36c916ed1ba737bd2bfef637834722a03fa7bdeb811ff` | 9/9 pares, 43.646 B | 5/5 |
| `combo.html` | 30.813 | `c145950d1dab43fdf653a575ef626d2ff64c503951e5d260737f6dfbe34b62b8` | 4/4 pares, 28.415 B | 2/2 |
| `optimize.html` | 25.141 | `de8cded7e26a2392d7af5ba5bd7cce68b5be2bd017d959f54c0123171dc14a4e` | 4/4 pares, 22.739 B | 2/2 |
| `live.css` | 67.424 | `03835ef5c21e5a086823248e0656944b120d26c8c44b724cb36dc35df2316674` | clone | — |
| `cobertura.css` | 4.945 | `7749843133a98739ee472d5103b50f5a38d277e25907fda1789449bdf6a881d7` | — | delta |
| `cobertura.js` | 22.834 | `edb6b00452f5b68d3a89c9d6a149419d07c8801b1469db62274650240e1d0dba` | — | delta |

- Captura: Playwright (Chromium headless shell 1243) em `https://dev.criptofarol.com.br` com todas as rotas `/api/**` simuladas (mesmos mocks do `card-1117-asset-selector.spec.ts`), 1440×900 e 390×900, `pt-BR`, tema escuro. Nenhuma chamada real à API.
- Gate: `design_token_gap` = None; `evaluate_clone_gate` = True com `route-landmarks.yaml`; `classify(index.html, /combo/discovery)` = PASS.
- Navegador (rework r1): `python3 -m http.server 18431 --bind 127.0.0.1` em `frontend/public` (encerrado no fim), Playwright Python 1.62 + Chromium 1243 headless, `pt-BR`, tema escuro, as três telas a 1440×900 e 390×844. **207/207 asserts PASS**: corpo servido == disco; sem erro de console nem `pageerror` (fora o `favicon.ico` do servidor local); sem rolagem horizontal na carga, com NVDA, SPY e QQQ abertos e no Decidir vencido; nenhum botão dentro de `<label>` e linha `<div>` com `<label for>`; clique no nome e no resto da linha seleciona e desmarca; SPY "1 lacuna" e 15m "herdada do 5m"; NVDA e SPY com "desde" por timeframe e BTC com início comum; lacuna com "horário de Nova York" e rótulo "Atualizado (Brasília)"; QQQ "já coletado: 1d desde 05 jan. 2023"; AAPL sob demanda com o texto da classe; Esc fecha (foco no botão por mouse, por teclado e dentro da tabela) e devolve o foco; Enter/Space abrem sem selecionar; Demonstração de combo/optimize sem prometer a aba Decidir; no index, evidência e favorito com "amostra do último refresh", "não reproduzível exatamente" a 11 px na evidência e no resultado, e nenhum "amostra mantida".
- Detector `.agents/skills/impeccable/scripts/detect.mjs --json`: só achados do incumbente clonado (fonte Inter, gradiente roxo e cinza sobre cor de `/combo/configure` e `/combo/optimize`, hierarquia plana, travessões do vivo); nenhum no delta.

## Impeccable

Operate, refinamento do seletor vivo do #1117 nas três telas. Tokens do produto. O delta usa a rampa 12/13px, alvos de 32 px no botão "Cobertura" (≥ 24 px) e 44 px nos controles vivos, foco visível, `aria-expanded`/`aria-controls`, `role=status` na coleta em andamento, `--text-tertiary` (#929aa5, 6,9:1) nos rótulos e cores de estado com contraste AA sobre #0b0e11 e #181a20 (âmbar 11:1, azul 10:1, vermelho 7,6:1). A seção de crítica fica para o pai, depois da dupla.

## Design Critique

Com-tela. Teto 1+1+1: autor, dupla A/B e 1 rework (r1, com as decisões de Alan no Design e os achados mecânicos da dupla). Nenhum segundo rework.

- Autor: `design-autor 1118 a1` (isolado). Rework: `design-autor 1118 r1` (isolado).
- Assessment A: `assessment-a 1118 a1` (isolado). Assessment B: `assessment-b 1118 a1` (isolado, detector + navegador).
- Verdict: **PASS**. Tokens: `UI impact: affected` / `live_route: /combo/discovery` / `surface: existing`.
- Proto canônico: https://dev.criptofarol.com.br/prototypes/card-1118-historico-binance/
- Protos extras: https://dev.criptofarol.com.br/prototypes/card-1118-historico-binance/combo.html e https://dev.criptofarol.com.br/prototypes/card-1118-historico-binance/optimize.html
- Snapshots: `.impeccable/critique/1118-card-1118-historico-binance-A.md` e `…-B.md`. O Gist OpenSpec não é a crítica.

- **P0**: nenhum.
- **P1**: nenhum.
- **Juízo, decidido por Alan no Design** ([comentário](https://github.com/oalansilva/crypto/issues/1118#issuecomment-6354593360)):
  - Open Question do autor: até o #1119, ação e ETF só são coletados por consulta direta; análise recusada não coleta, sem teto novo em "Todos do filtro".
  - P2 de A (favorito e refresh diário): o favorito mantém a amostra do último refresh; refazer igual reproduz o número de hoje em `/favorites`.
  - Os dois foram aplicados no r1.
- **P2 mecânicos, corrigidos no r1:**
  - lacunas do SPY contadas em dobro (15m herdado do 5m não soma);
  - resumo da linha separa "1d desde …" de "intraday desde …";
  - fuso rotulado na tabela de Cobertura;
  - QQQ em falha: "já coletado: 1d desde …";
  - peso do texto "não reproduzível exatamente" no Decidir;
  - Esc fecha a tabela de Cobertura e devolve o foco;
  - texto da demonstração em `combo.html` e `optimize.html`;
  - botão "Cobertura" fora do `<label>` da linha.
- **P3 aceitos, para o Apply:**
  - `role=status` reanuncia o progresso a cada filtro ou página;
  - demais motivos de falha de coleta, sem mostrar o 488006 cru;
  - total de páginas no paginador;
  - coluna Ação cortada no Decidir a 1440 px (vem do clone);
  - números e datas do protótipo são amostra;
  - achados do detector (Inter, gradientes, raios e cores fora do `DESIGN.md`) só no CSS vivo clonado; delta (`cobertura.css`, `cobertura.js`) limpo;
  - nomes internos e constantes já listados como mecanismo.
- **Disposition:** o delta visível fica no seletor de ativos das três telas e no Decidir; sem gráfico de ação/ETF, sem pré/pós-mercado e sem botão de coleta (Não entra).

### Proxies

- `design.md` words: 5124 (antes desta seção)
- HTML generated vs copied (`index.html`): 3696 vs 43646
- Spawns: 4
- `proxy modelo: design-autor → Opus 5.5 (claude-opus-5-5)` (a1 e r1)
- `proxy modelo: Assessment A → Opus 5.5 (claude-opus-5-5)`
- `proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5)`

Design Agent verdict: PASS
