---
description: Implementar um Backtester de Cripto Spot completo com CCXT, múltiplas estratégias e CLI.
---

# Backtester de Cripto Spot

## Objetivo
Criar uma ferramenta de backtesting em Python para negociação de criptomoedas no mercado spot (apenas long/compra). A ferramenta deve suportar busca de dados via CCXT, múltiplos timeframes, três estratégias específicas de swing trade e capacidades detalhadas de relatório e comparação.

## Requisitos

### Fonte de Dados
- **CCXT**: Buscar dados OHLCV da Binance (spot) sem necessidade de chave de API.
- **Paginação**: Gerenciar `since`, `until`, `limit` e rate limits para coletar todo o histórico solicitado.
- **Cache**: Cache local em CSV ou Parquet, chaveado por exchange, símbolo, timeframe, início e fim.
- **DataFrame Padrão**: `timestamp_utc`, `open`, `high`, `low`, `close`, `volume`.

### Motor de Backtest (Backtester Engine)
- **Tipo**: Spot / Long-only (sem short, sem margem, sem alavancagem).
- **Carteira**: Rastrear saldo em USDT (quote) e posição em BTC (base).
- **Regras de Ordens**: 
    - Só compra se tiver saldo em caixa.
    - Só vende se tiver posição no ativo.
- **Custos**: 
    - Taxa (Fee): 0.1% (padrão).
    - Slippage: 0.05% (padrão).
- **Dimensionamento de Posição (Position Sizing)**: Porcentagem do caixa disponível (padrão 20% por entrada).
- **Execução**: No fechamento do candle (`close`) por padrão. Opção `--fill next_open` para executar na abertura do próximo candle.

### Estratégias (Swing Trade)
Deve implementar 3 estratégias com parâmetros configuráveis:

1. **SMA Cross (Cruzamento de Médias)**:
    - **Compra**: SMA(rápida) cruza acima da SMA(lenta).
    - **Venda**: SMA(rápida) cruza abaixo da SMA(lenta).
    - **Parâmetros**: fast=20, slow=50 (padrão).
2. **RSI Reversal (Reversão de RSI)**:
    - **Compra**: RSI cruza acima de 30 (nível de sobrevenda).
    - **Venda**: RSI cruza abaixo de 70 (nível de sobrecompra).
    - **Parâmetros**: period=14, oversold=30, overbought=70.
3. **Bollinger Bands Mean Reversion (Retorno à Média)**:
    - **Compra**: Preço de fechamento abaixo da Banda Inferior.
    - **Venda**: Preço de fechamento acima da Banda Média (ou Superior).
    - **Parâmetros**: period=20, std=2.0, exit_mode='mid' (padrão).

### Gerenciamento de Risco
- **Stop Loss**: Porcentagem opcional (ex: 3%).
- **Take Profit**: Porcentagem opcional (ex: 6%).

### Interface de Linha de Comando (CLI)
- `run`: Executa backtest para 1 estratégia e 1 timeframe.
- `batch`: Executa para 1 estratégia e lista de timeframes.
- `compare`: Compara múltiplas estratégias e/ou múltiplos timeframes. Gera relatório comparativo e ranking.

### Relatórios e Métricas
- **Métricas**: Retorno Total (%), Max Drawdown (%), CAGR, Win Rate (%), Fator de Lucro, Sharpe Ratio simplificado.
- **Visualização**: Curva de capital (Equity curve) e Gráfico de Drawdown.
- **Saída**: Tabela comparativa e (opcionalmente) CSV de resumo.

### Arquitetura do Projeto
- `data/ccxt_loader.py`: Carregamento e cache de dados.
- `strategy/base.py`: Classe base abstrata.
- `strategy/sma_cross.py`, `strategy/rsi_reversal.py`, `strategy/bb_meanrev.py`: Implementações.
- `engine/backtester.py`: Lógica de execução e portfólio.
- `broker/execution.py`: Simulação de ordens.
- `report/metrics.py`, `report/plots.py`, `report/summary.py`: Análise.
- `cli.py`: Entrada da aplicação.
- `tests/`: Testes unitários e de integração.

## Testes (Origatório)
- Mínimo de 6 testes pytest cobrindo:
    - Aplicação de taxas e slippage.
    - Lógica de compra (não comprar sem saldo).
    - Lógica de venda (não vender sem posição).
    - Geração de sinais SMA.
    - Cálculo de Max Drawdown.
