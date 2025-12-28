# Crypto Spot Backtester

Ferramenta de backtesting para criptomoedas no mercado spot (long-only) com suporte a múltiplas estratégias de swing trade.

## Características

- **Fonte de Dados**: CCXT (Binance) com cache local
- **Estratégias**: SMA Cross, RSI Reversal, Bollinger Bands Mean Reversion
- **Engine**: Simulação spot/long-only com fees, slippage e position sizing
- **CLI**: Comandos `run`, `batch` e `compare`
- **Métricas**: Sharpe, Drawdown, CAGR, Win Rate, Profit Factor

## Instalação

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Uso

### Executar uma estratégia
```bash
python cli.py run --strategy sma_cross --symbol BTC/USDT --timeframe 4h --since 2023-01-01
```

### Comparar estratégias
```bash
python cli.py compare --strategies sma_cross,rsi_reversal,bb_meanrev --timeframe 4h --since 2023-01-01
```

### Múltiplos timeframes
```bash
python cli.py batch --strategy rsi_reversal --timeframes 1h,4h,1d --since 2024-01-01
```

## Estrutura

```
crypto/
├── cli.py              # Entry point
├── src/
│   ├── data/           # Data fetching
│   ├── engine/         # Backtester
│   ├── strategy/       # Strategies
│   └── report/         # Metrics & plots
└── tests/              # Unit tests
```

## Testes

```bash
pytest tests/
```

## Como Adicionar uma Nova Estratégia

1. Crie um arquivo em `src/strategy/` (ex: `macd.py`)
2. Herde de `Strategy` e implemente `generate_signals(df)`
3. Registre em `cli.py` no dict `STRATEGIES`
