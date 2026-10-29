## 1. Verificações antes do código

- [x] 1.1 Confirmar a taxa da Binance Ações (documentação oficial de Stocks Trading ou `commission` da conta, sem ordem real); registrar no card e fixar `fee` e `fee_confirmed` de ação/ETF (decisão 9)
- [x] 1.2 Medir a profundidade do 5m de NVDA e SPY na Binance (primeiro candle guardado depois de `ensure`); abaixo de 1 ano, comentar no card para Alan antes de seguir (Risks)
- [x] 1.3 Gravar a amostra fixa da regressão cripto (BTC/USDT 1d e 4h, janela fixa) e o resultado com a rotina atual, antes de mudar a saída

## 2. Gap no stop (todas as classes)

- [x] 2.1 Regra do gap em `_legacy_extract_trades_from_signals` e `_fast_extract_trades_from_signals` (long `open ≤ stop` sai em `open`; short espelho), com `exit_reason = "stop_loss_gap"`, `signal_type = "Stop com gap"`, `stop_price`, `gap_pct` e o interruptor `STOP_GAP_EXIT`
- [x] 2.2 Mesma regra nas simulações de 15m (`_legacy`, `_fast` e `_compiled_simulate_execution_with_15m` em `deep_backtest.py` e `combo_acceleration`)
- [x] 2.3 Testes: gap long (95/90), gap short (105/110), toque sem gap igual a hoje, retomada depois de fim de semana, gap num 15m, saída com taxa e slippage
- [x] 2.4 Regressão cripto: rotina nova sobre a amostra de 1.3; trades sem gap idênticos, toda diferença é trade com gap; tabela antes/depois na evidência da demonstração (handoff e card), nunca na UI, que mostra só o número novo (decisão 6 de Alan no Design)

## 3. Precisão efetiva

- [x] 3.1 `extract_trades_with_mode` devolve `execution` (pedida, efetiva, `intraday_missing`, `intraday_reason`, `gap_stops`) em todos os caminhos de queda, sem mudar quando cai
- [x] 3.2 Regra de cobertura: início no primeiro pregão/dia, fim no último, sem pregão inteiro sem 15m; trecho = intervalos sem 15m juntados; testes com NVDA "todo o histórico" e cripto sem 15m no fim da janela
- [x] 3.3 `combo_optimizer.py:2225`: intrabar não depende mais de `ccxt`; `_begin_sample`/`_freeze_intraday` congelam também séries `binance_equity`

## 4. Histórico e tempos de ação/ETF

- [x] 4.1 `derive_blocks(minutes)` no `nyse_calendar` (15m, 1h, 4h) com âncora às 09:30 de Nova York, corte no fechamento e no meio-pregão, bloco incompleto como lacuna herdada
- [x] 4.2 `HistoryService.read` serve 1h e 4h derivados do 5m; cobertura lista "montado do 5m"; `DEFERRED_TIMEFRAMES` sai do adaptador
- [x] 4.3 Testes: pregão cheio (7 candles de 1h, 2 de 4h), meio-pregão de 27 nov. 2026, viradas de 8 mar. e 1 nov. 2026, fim de semana e feriado sem candle, split do NVDA (7–10 jun. 2024) sem salto nem stop falso

## 5. Backtest individual de ação/ETF (API)

- [x] 5.1 `asset_analysis_guard`: aceitar ação/ETF quando o escopo é 1 ativo (`POST /backtest`, ou `POST /optimize` com `run_scope == "single"` e um símbolo, vindo do Combo ou da Otimização); lote (`/backtest/batch`) e Descoberta seguem com `asset_class_not_supported`
- [x] 5.1b Texto novo da recusa (decisão 3): "ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização); o lote vem depois" em `EQUITY_UNSUPPORTED_MESSAGE`, `catalog_symbol_reason`, `DISCOVERY_EQUITY_REASON`, `discovery_service` e, no front, `EQUITY_REASON`/`blockedNotice`; testes que conferem o texto no lote, na seleção mista e na Descoberta
- [x] 5.2 `combo_routes`: `_ensure_crypto_data_source` deixa passar `binance_equity`; 1m/5m de ação/ETF recusados com o motivo
- [x] 5.3 Coleta pela análise: `HistoryService.ensure` só da série do tempo gráfico e do 5m do intrabar, espera do lock, roda no coberto, 422 `history_unavailable` sem nada gravado; teste de que seletor e análise recusada não coletam
- [x] 5.4 Custos por classe (`backtest_execution_costs`), slippage também em `POST /backtest`; `periods_per_year` por classe e tempo gráfico; anos pelo calendário
- [x] 5.5 Respostas com `asset`, `data_provenance`, `execution` e `conventions` (schemas `combo_params.py`)
- [x] 5.6 Testes de contrato: NVDA 1 ativo roda (Combo, Otimização e `POST /backtest`); NVDA + BTC/USDT roda só a cripto; lote e Descoberta recusam com o texto novo; marcado pela Binance recusa; Otimização com NVDA 1h em jan. 2024 sem 5m não roda nada vazio

## 6. Favoritos

- [x] 6.1 `POST /api/favorites/` recusa ação/ETF com 422 `asset_class_not_favoritable` e nada gravado; teste com SPY e com BTC/USDT (sem mudança)
- [x] 6.2 Conferir que o refresh diário dos favoritos de cripto usa a rotina nova e guarda o número anterior no histórico de runs

## 7. Frontend (seguir o protótipo)

- [x] 7.1 `ComboResultsPage`: bloco "Dados e execução" (proveniência, faixa de precisão nos 4 estados com o título pelo tempo gráfico, nota de coleta parcial, 8 fatos, convenções com "Preços ajustados" em ação e ETF) depois do resumo, oculto em resultado sem `execution`; chip de classe; abaixo de 768 px recolhido com resumo (precisão e avisos) e botão `aria-expanded` de 44 px, aberto no desktop (decisão 19); componente reusável pela Otimização
- [x] 7.2 `StrategyTradesTable`: `currency` em todas as colunas de dinheiro (cripto USDT, ação/ETF USD); data e hora de Nova York com fuso no 15m/1h/4h de ação/ETF, só data no 1d (decisão 18); "Stop com gap" com stop e abertura na tabela e no cartão móvel
- [x] 7.3 Favoritar recusado: botão `aria-disabled` focável, `aria-describedby`, motivo escrito, `role=status` ao ativar, sem modal; cripto como hoje
- [x] 7.4 `ComboConfigurePage` + `assetSelection`: plano por classe (1 ação/ETF roda; mista roda só a cripto com o porquê novo e 1m/5m disponíveis), `run_scope: "single"`, abrir o resultado sem salvar nem checar `/favorites/exists`, fonte com contraste AA, nota de classe, texto sob demanda, 1m/5m indisponíveis com dica, dica do Deep Backtest, aviso de 5m antes de rodar sem trocar o valor, linha de coleta ao rodar, alerta de coleta falha
- [x] 7.4b `ComboOptimizePage`: 1 ação/ETF roda com `run_scope: "single"` e mostra o resultado ao lado com "Dados e execução"; período fixo visível; nota de classe e texto sob demanda novos; 1m/5m/30m indisponíveis com ação; aviso antes de rodar quando o 5m não cobre a janela fixa; linha de coleta; recusa do lote e da mista com o texto novo
- [x] 7.4c Descoberta: só o texto da recusa muda (5.1b); conferir o aviso vivo com ação/ETF selecionado
- [x] 7.5 Playwright com a API simulada: NVDA (precisão diária e trecho, USD, só data, gap, favorito recusado por clique e por teclado, coleta parcial, recolhido no celular), SPY short intrabar com hora de Nova York, BTC/USDT regressão com lista em USDT e favorito vivo, Combo (1 ação, mista, só ações, 5m pelo caminho real, coleta), Otimização (1 ação em 1d, 1h sem 5m, mista), a 1440 e a 390 px, sem rolagem horizontal
- [x] 7.6 Comparar as telas entregues com `frontend/public/prototypes/card-1119-backtest-acoes-etfs/` (layout, estados, a11y, responsivo) e registrar elementos seguidos e desvios no handoff

## 8. Fechamento

- [x] 8.1 `openspec validate card-1119-backtest-acoes-etfs` e testes focados do backend e do frontend verdes
- [x] 8.2 Evidência no card: taxa confirmada (1.1), profundidade do 5m (1.2), tabela antes/depois da cripto (2.4, só na evidência) e os cenários de demonstração do Entra
