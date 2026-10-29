## Why

Hoje o gráfico de cripto lê `market_ohlcv` (PostgreSQL) e as análises leem Parquet alimentado direto pela CCXT: são dois históricos da mesma série, sem regra de sincronização, e a amostra da Descoberta é apagada quando a combinação termina. Esta é a segunda história do épico #1116: o catálogo do #1117 já deixa escolher ação e ETF, mas não existe histórico Binance confiável e reutilizável para essas classes, e as histórias seguintes (#1119 a #1126) dependem dele.

## Problema

Alan pode receber históricos diferentes entre gráfico e análise ou baixar dados repetidos sem saber se o período está completo.

## História

Como usuário, quero consultar um período histórico confiável e reutilizar os dados já coletados para analisar ativos com consistência e sem downloads repetidos.

## Entra

- [ ] **Mesma série em todo lugar:** para o mesmo ativo, timeframe, sessão, ajuste e período, o gráfico e as análises (backtest, combo, otimização e descoberta) recebem os mesmos candles, em cripto, ação ou ETF. Vale também para a cripto de hoje, cujo gráfico e cujas análises leem históricos separados; a troca não perde o histórico de cripto já guardado nem quebra favoritos e resultados existentes.
- [ ] **Sem download repetido:** repetir uma análise no mesmo período usa o que já foi coletado, e atualizar busca só o trecho que falta. Abrir, filtrar ou selecionar o catálogo inteiro não dispara coleta do histórico de todos os ativos.
- [ ] **Período honesto:** toda consulta informa o período pedido e o efetivamente coberto, lacunas, última atualização e se o histórico é insuficiente para o que foi pedido. Falha da Binance (limite de requisições, indisponibilidade, resposta com erro ou formato mudado) aparece como falha ou cobertura incompleta, nunca como lista vazia nem como período completo.
- [ ] **Coleta que retoma:** histórico longo atravessa várias páginas da Binance; coleta interrompida por reinício ou falha passageira continua de onde parou, sem duplicar nem pular candles.
- [ ] **Calendário de bolsa:** ação e ETF respeitam pregão, feriados, fuso de Nova York e horário de verão; mercado fechado não vira lacuna nem candle inventado. Cripto segue 24/7, como hoje.
- [ ] **Amostra estável:** uma execução usa a mesma amostra do início ao fim, mesmo que o histórico seja atualizado ou corrigido, ou o cache refeito, enquanto ela roda. O resultado registra fonte, classe, sessão, ajuste, timeframe, período e versão dos dados.
- [ ] **Correções e eventos corporativos:** split, dividendo ou correção de candle pela Binance passam a valer nas próximas consultas, sem misturar série ajustada e não ajustada e sem mudar uma execução em andamento.
- [ ] **Apagar o cache não perde histórico:** refazer o cache de leitura devolve os mesmos candles; nada se perde do histórico guardado.
- [ ] **Verificação:** BTC/USDT, NVDA e um ETF (SPY ou QQQ) com histórico de mais de uma página; o ETF é verificado por conta própria, não inferido do NVDA. O split de 10 por 1 do NVDA (junho de 2024) aparece sem salto falso de preço, e a virada do horário de verão não cria buraco nem candle a mais. Regressão de cripto: gráfico, backtest, combo, otimização e descoberta seguem funcionando com o histórico que já existe.
- [ ] **Cobertura no seletor:** no seletor de ativos, ação e ETF deixam de aparecer como "não coletado" e passam a mostrar o período coberto, as lacunas e a última atualização do histórico já coletado. Este card não traz tela de gráfico nova para ação e ETF.
- [ ] **Coleta sob demanda:** a coleta de uma ação ou ETF começa quando o ativo é pedido numa consulta ou análise; o que já foi coletado é reaproveitado e só o trecho que falta é buscado. Ativo que ninguém pediu continua sem coleta.
- [ ] **Só pregão regular:** o histórico de ação e ETF cobre só o horário normal de negociação de Nova York; pré e pós-mercado não entram na série.
- [ ] **15 minutos montado do 5 minutos:** em ação e ETF, o candle de 15 minutos é montado a partir dos candles de 5 minutos do mesmo pregão, sem atravessar mercado fechado, e aparece marcado como derivado.
- [ ] **Reprodução enquanto favoritado:** resultado favoritado mantém a sua amostra e pode ser refeito com exatamente os mesmos candles enquanto for favorito. Os demais mantêm a amostra por um prazo fixo; passado o prazo, aparecem como "não reproduzível exatamente".

> **Decisões de Alan no Design (23/10/2026)** ([comentário no card](https://github.com/oalansilva/crypto/issues/1118#issuecomment-6354593360)):
> 1. **Coleta de ação/ETF até o #1119: só pela consulta.** Análise recusada não coleta; sem teto novo em "Todos do filtro". O rótulo "sob demanda" explica que a coleta começa quando a análise aceitar a classe.
> 2. **Favorito mantém a amostra do último refresh.** Cada atualização diária do favorito troca a amostra guardada; refazer igual reproduz o número que aparece hoje em `/favorites`. A amostra da promoção deixa de ser a referência.

## Não entra

- Escolher estratégia, benchmark ou executar ordens.
- Retirar provedores legados antes da migração de consumidores.
- Rodar backtest, combo, otimização ou descoberta com ação ou ETF: chega no #1119 e nas histórias seguintes. Aqui o histórico dessas classes fica pronto, consultável e com cobertura informada.
- Remover Stooq, Yahoo e Alpha Vantage: fica no #1126.
- Gráfico de candles de ação e ETF: aqui o histórico dessas classes aparece só como cobertura no seletor.
- Pré e pós-mercado de ação e ETF.
- Coleta em segundo plano de favoritos e lote diário do catálogo inteiro.
- Refazer com exatamente os mesmos candles um resultado não favoritado depois do prazo.

## What Changes

- Uma autoridade só para os candles: `market_ohlcv` (PostgreSQL/Timescale) passa a guardar séries identificadas por ativo, fonte, sessão, ajuste e timeframe, com versão. Gráfico e análises leem pelo mesmo serviço de histórico. A política de retenção de 2 anos sai dessa tabela, porque ela vira o histórico guardado.
- O Parquet das análises deixa de baixar da CCXT por conta própria: vira cache de leitura derivado do PostgreSQL, com versão no nome, e pode ser apagado e refeito.
- Adaptador Binance de ações e ETFs pela rota pública do gráfico, com validação de formato, erro de negócio em HTTP 200, limite de requisições compartilhado entre workers, paginação que retoma e calendário da bolsa de Nova York.
- Amostra de execução guardada por manifesto e segmentos com SHA-256, reaproveitados entre execuções. Favorito guarda a amostra do último refresh diário (o refresh que já existe troca a amostra); os demais resultados, e a amostra trocada, ficam 30 dias e depois são marcados "não reproduzível exatamente".
- Seletor de ativos mostra cobertura (período, lacunas, última atualização, coleta em andamento, falha e 15m derivado). Decidir da Descoberta mostra até quando a amostra fica guardada.
- Migração: a história de cripto já guardada em Parquet e em `market_ohlcv` é consolidada no PostgreSQL antes de virar a chave; favoritos e resultados antigos ficam como estão. Provedores legados continuam no código (#1126).

## Capabilities

### New Capabilities

- `market-history`: série identificada, autoridade única, consulta com cobertura honesta, coleta sob demanda que retoma, calendário de bolsa, pregão regular, 15m derivado, versão e correções, cache reconstruível.
- `binance-equity-history`: adaptador do histórico de ações e ETFs da Binance (rota do gráfico), validação, erros de negócio, limites e paginação.
- `execution-data-snapshot`: amostra estável por execução, registro de proveniência, retenção por favorito (amostra do último refresh) e por prazo, rótulo "não reproduzível exatamente".
- `asset-history-coverage`: cobertura do histórico no seletor de ativos e o estado da amostra no Decidir.

### Modified Capabilities

- `ohlcv-storage`: identidade da série no lugar de `(symbol, timeframe, candle_time)`; a retenção de 2 anos deixa de apagar histórico.
- `market-candles`: a leitura canônica do gráfico passa pelo mesmo serviço de histórico das análises.
- `data-caching`: o Parquet deixa de baixar da exchange e vira cache derivado e versionado.

## Impact

- Backend: `backend/app/services/ohlcv_storage.py`, `canonical_candle_service.py`, `ohlcv_backfill_service.py`, `market_data_providers.py` (novo adaptador, sem retirar Stooq/Yahoo/Alpha Vantage), `discovery_inputs.py`, `discovery_recovery.py`, `favorite_backtest_refresh_service.py`, `combo_optimizer.py`, `sequential_optimizer.py`, `asset_catalog_service.py`, `backend/app/api.py` (`/market/candles`), `src/data/incremental_loader.py`, `backend/app/database.py` e uma revisão Alembic.
- Frontend: `frontend/src/components/AssetPicker.tsx` e `.css`, `frontend/src/lib/assetSelection.ts`, `frontend/src/pages/DiscoveryPage.tsx` (Decidir).
- Dados: `market_ohlcv` ganha identidade de série e perde a retenção de 2 anos; nova tabela de séries e de manifestos de amostra; diretório de segmentos de amostra; o cache Parquet atual é migrado e depois refeito.
- Dependência nova de calendário de bolsa (`exchange_calendars`).
- Rotas BAPI de ações não têm contrato público: o adaptador fica isolado e falha de forma visível.
