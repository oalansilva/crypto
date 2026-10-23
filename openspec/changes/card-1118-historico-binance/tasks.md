## 1. Medida e esquema

- [x] 1.1 Medir `market_ohlcv` (linhas e bytes por timeframe e fonte, jobs Timescale ativos) e o cache Parquet em DEV e PROD; registrar no card antes de migrar
- [x] 1.2 Revisão Alembic: `market_series`, hypertable nova com chave `(series_id, candle_time)`, `market_series_fetch`, `market_series_coverage`, `execution_data_snapshots`, `favorite_strategies.snapshot_id` e colunas de proveniência em `discovery_results`
- [x] 1.3 Remover a política de retenção de 2 anos de `market_ohlcv` (manter compressão aos 30 dias) e ajustar `database.py`
- [x] 1.4 Adicionar `exchange_calendars` ao `backend/requirements.txt`

## 2. Adaptador Binance de ações e ETFs

- [x] 2.1 `BinanceEquityProvider` com paginação retroativa (`limit=1000`, `endTime=min(t)-1`), validação de página, `BinanceBusinessError` (488006 em HTTP 200), "formato mudou" e confirmação de página vazia
- [x] 2.2 Verificar contra a Binance o parâmetro de sessão regular e se o 1D bate com o pregão regular (20 pregões de NVDA e SPY); registrar a evidência no card e parar com P0 se o 1D não bater
- [x] 2.3 Verificar `ADJUSTED`: split do NVDA (7–10 jun. 2024) e ex-dividendos de SPY em 2025; fixar o rótulo do ajuste
- [x] 2.4 Limitador compartilhado no PostgreSQL (2 req/s, 2 séries simultâneas, `Retry-After`, circuito de 5 min) e testes com 429, 418, 5xx e 488006
- [x] 2.5 Registrar o adaptador na fábrica de `market_data_providers.py` sem retirar CCXT, Stooq, Yahoo nem Alpha Vantage

## 3. Serviço de histórico

- [x] 3.1 `HistoryService.read`/`ensure` com cobertura (pedido, coberto, lacunas, atualização, versão, nativo/derivado, insuficiente)
- [x] 3.2 Coleta retomável: cursor por série, upsert e avanço do cursor na mesma transação, lock consultivo por série, espera de até 30 s para o segundo pedido
- [x] 3.3 Calendário XNYS: filtro do pregão regular, lacunas só dentro do pregão, testes de feriado, meio-pregão e as duas viradas de horário de verão (78 candles de 5m por pregão)
- [x] 3.4 15m derivado do 5m na leitura (blocos de 09:30, sem atravessar o fechamento, bloco incompleto como lacuna herdada do 5m e fora da contagem do resumo, versão da regra)
- [x] 3.5 Versão: comparação da janela rebuscada, recoleta em tabela de preparo, troca numa transação e `data_version + 1`
- [x] 3.6 Cache Parquet derivado por série e versão, escrita atômica, teto de 3 GiB e teste "apagar e refazer devolve os mesmos candles sem chamar a Binance"
- [x] 3.7 `GET /market/history` autenticado para qualquer classe; `/market/candles` lê pelo serviço e devolve a cobertura (continua só cripto)
- [x] 3.8 Até o #1119, só `GET /market/history` chama `ensure` para ação/ETF: a recusa `asset_class_not_supported` acontece antes de qualquer `ensure` (decisão de Alan de 23/10/2026); teste com "Todos do filtro" em ETFs + Iniciar

## 4. Consumidores e migração da cripto

- [x] 4.1 Escritor canônico de cripto grava nas séries `binance_spot`
- [x] 4.2 `IncrementalLoader`, `combo_optimizer`, `sequential_optimizer` e `discovery_inputs` leem pelo `HistoryService` atrás de `MARKET_HISTORY_UNIFIED`
- [x] 4.3 Script de migração: copiar `market_ohlcv`, importar do Parquet só o que falta, registrar divergências, conferir por série e trocar os nomes
- [x] 4.4 Teste de paridade: gráfico e backtest de BTC/USDT 1h e 4h recebem candles idênticos na mesma versão
- [x] 4.5 Regressão de cripto com o histórico existente: gráfico, backtest, combo, otimização e descoberta; favoritos e resultados antigos abrem com os mesmos números

## 5. Amostra de execução

- [x] 5.1 Segmentos mensais com SHA-256 e manifesto por execução; `FrozenProvider` lê segmentos e confere o hash
- [x] 5.2 Descoberta usa o manifesto no lugar do spool `inputs-*`; `inputs_cleaned` passa a soltar a referência, não apagar bytes
- [x] 5.3 Backtest, combo e otimização congelam a amostra no início; teste "cache refeito durante a execução não muda o resultado"
- [x] 5.4 Proveniência no resultado (fonte, classe, sessão, ajuste, origem do timeframe, períodos, versão, `snapshot_id`)
- [x] 5.5 Favorito fixa a amostra (cópia na promoção, até o primeiro refresh); desfavoritar ou trocar a amostra dá 30 dias a partir desse momento; job diário apaga manifestos vencidos e segmentos sem referência
- [x] 5.6 Refresh diário (`favorite_backtest_refresh_service.refresh_favorite`, mesmo loop do `runtime_worker`): `_prepare_market_data` via `HistoryService.ensure`; amostra congelada no início do `run_optimization`; no commit que grava `favorite.metrics`, trocar `favorite_strategies.snapshot_id`, gravar `auto_backtest_runs.snapshot_id` e soltar a amostra anterior com 30 dias; falha não troca nada e solta o manifesto da tentativa; favorito antigo ganha amostra no primeiro refresh
- [x] 5.7 Reproduzir um favorito depois de um refresh com o manifesto e comparar candles e métricas com o número de `/favorites`; resultado vencido responde "não reproduzível exatamente"

## 6. Tela

- [x] 6.1 `asset_catalog_service.serialize_item` lê `market_series_coverage` e devolve os estados e a lista por timeframe
- [x] 6.2 `AssetPicker.tsx`, `AssetPicker.css` e `assetSelection.ts`: fato de histórico ("desde" por timeframe, lacunas só de séries nativas, sob demanda por classe, "já coletado:"), linha `<div>` com `<label for>` e botão "Cobertura" fora do label, Esc fecha e devolve o foco, tabela por timeframe com fuso nas lacunas e no rótulo da atualização, como no protótipo, nas três telas e na variante estreita
- [x] 6.3 `DiscoveryPage.tsx` (Decidir): proveniência da série e estado da amostra na evidência e nos resultados, a 11 px; favorito diz que Favoritos guarda a amostra do último refresh
- [x] 6.4 Testes `tsx --test` dos textos e e2e Playwright (`card-1118-*.spec.ts`) a 1440 e 390 px: estados, teclado (Enter, Space, Esc), abrir sem marcar, sem rolagem horizontal, Decidir guardada e vencida, favorito

## 7. Verificação final

- [x] 7.1 BTC/USDT, NVDA e SPY ou QQQ com mais de uma página: sem duplicata, cobertura correta; ETF verificado por conta própria
- [x] 7.2 NVDA sem salto no split de jun. 2024; virada do horário de verão sem buraco nem candle a mais
- [x] 7.3 Repetir a mesma consulta sem candle novo não pede páginas antigas; selecionar "Todos do filtro" em ETFs, e tentar iniciar a análise recusada, não coleta nada
- [x] 7.4 `openspec validate card-1118-historico-binance --strict` e testes focados verdes
