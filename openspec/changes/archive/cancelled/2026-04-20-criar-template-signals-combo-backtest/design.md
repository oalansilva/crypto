# Design Spec: Template de Sinais para Backtesting no Combo

**Card:** #65  
**change_id:** `criar-template-signals-combo-backtest`  
**Estágio:** DESIGN  
**Dependência:** Card #53 (sinais BUY/SELL/HOLD com RSI+MACD+Bollinger) | Sistema Combo existente

---

## 1. Conceito

Criar um **template "RSI+MACD+Bollinger Signals"** no sistema Combo existente que usa a lógica de `_build_signal` (já implementada em `binance_service.py`) para fazer **backtest histórico**.

O sistema Combo já possui:
- `/combo/select` — seleção de template
- `/combo/configure` — configuração de parâmetros
- `/combo/results` — exibição de resultados

O objetivo é **reaproveitar** esse fluxo, criando um template que executa a lógica de sinais em dados históricos ao invés de dados em tempo real.

---

## 2. Arquitetura de Integração

### 2.1 Reaproveitamento de `_build_signal`

A função `_build_signal` em `binance_service.py` já calcula:
- RSI (Relative Strength Index)
- MACD (sentiment: bullish/bearish/neutral)
- Bollinger Bands (upper, middle, lower)
- BUY/SELL/HOLD score baseado nos 3 indicadores
- `target_price` e `stop_loss` baseados no `RiskProfile`

**Para backtesting**, não precisamos modificar `_build_signal`. Precisamos de:

1. Um **novo template** no sistema Combo que define `entry_logic`/`exit_logic` usando os indicadores RSI/MACD/BB
2. Um **BacktestService** que itera sobre candles históricos e aplica `_build_signal` em cada candle
3. **Simulação de trades**: para cada candle onde `_build_signal` retorna BUY, simula entrada em `close`. Usa `target_price` e `stop_loss` do sinal para simular saída

### 2.2 Fluxo: Select → Configure → Run Backtest → Results

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  /combo/select  │ ──▶ │ /combo/configure│ ──▶ │  Run Backtest   │ ──▶ │ /combo/results  │
│  (escolhe       │     │  (parâmetros:   │     │  (aplica        │     │  (exibe: win    │
│   "Signals")    │     │   asset, days,  │     │   _build_signal │     │   rate, profit,  │
│                 │     │   risk_profile) │     │   em candles    │     │   drawdown)     │
│                 │     │                 │     │   históricos)    │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 2.3 Fluxo de Dados no Backtest

```
1. Fetch candles históricos (OpenAPI Binance v3/klines)
2. Para cada candle (exceto o último):
   a. Passar candles até esse ponto para _build_signal()
   b. Se sinal = BUY → registrar entrada (entry_price = close desse candle)
   c. Acompanhar trade até target_price ou stop_loss
   d. Calcular P&L
3. Agregar métricas: win rate, total profit, max drawdown, etc.
```

---

## 3. Parâmetros do Template

### 3.1 Parâmetros exposés no Configure

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `asset` | string | BTCUSDT | Par desejado (ex: BTCUSDT, ETHUSDT) |
| `days` | int | 365 | Período em dias para backtest |
| `risk_profile` | enum | moderate | conservative / moderate / aggressive |
| `initial_capital` | float | 100 | Capital inicial em USD |

### 3.2 Parâmetros Internos (do Template)

Os parâmetros RSI/MACD/BB são **fixos** no template (hardcoded via `_PROFILE_SETTINGS`):

```python
# RiskProfile.conservative
buy_rsi: 32.0,  sell_rsi: 68.0,  target_pct: 3%,  stop_pct: 1.5%

# RiskProfile.moderate
buy_rsi: 38.0,  sell_rsi: 64.0,  target_pct: 5%,  stop_pct: 2.5%

# RiskProfile.aggressive
buy_rsi: 45.0,  sell_rsi: 58.0,  target_pct: 8%,  stop_pct: 4.0%
```

---

## 4. Métricas no Results

### 4.1 Métricas Principais

| Métrica | Descrição |
|---------|-----------|
| `win_rate` | % de trades winners (target atingido antes do stop) |
| `total_trades` | Número total de trades simulados |
| `total_profit_pct` | Profit total em % sobre capital inicial |
| `total_profit_usd` | Profit total em USD |
| `max_drawdown` | Maior drawdown durante o período |
| `avg_trade_duration` | Duração média de um trade em dias |
| `best_trade_pct` | Melhor trade em % |
| `worst_trade_pct` | Pior trade em % |

### 4.2 Detalhamento de Trades

Cada trade no array `trades` deve conter:

```json
{
  "entry_time": "2025-01-15T08:00:00Z",
  "entry_price": 42000.0,
  "exit_time": "2025-01-16T14:00:00Z",
  "exit_price": 43260.0,
  "exit_reason": "target", // "target" | "stop" | "end_of_data"
  "profit_pct": 3.0,
  "profit_usd": 3.0,
  "signal_confidence": 78,
  "indicators": {
    "RSI": 35.0,
    "MACD": "bullish",
    "BollingerBands": { "upper": 44000, "middle": 42000, "lower": 40000 }
  }
}
```

### 4.3 Dados para Gráfico

O results **reaproveita** a UI existente do Combo (`ComboResultsPage`) que já suporta:
- Candlestick chart com trades marcados
- Equity curve
- Métricas summaries

---

## 5. Integração Backend

### 5.1 Novo Template

Criar entrada no banco SQLite (`combo_templates`):

```json
{
  "name": "rsi_macd_bollinger_signals",
  "description": "Estratégia de sinais RSI + MACD + Bollinger Bands (Card #65)",
  "indicators": [
    { "type": "rsi", "params": {} },
    { "type": "macd", "params": {} },
    { "type": "bollinger_bands", "params": {} }
  ],
  "entry_logic": "signal_type == 'BUY'",
  "exit_logic": "price >= target_price OR price <= stop_loss",
  "stop_loss": { "default": 0.025 },
  "optimization_schema": null
}
```

### 5.2 Serviço de Backtest de Sinais

Criar `app/services/signals_backtest_service.py`:

```python
async def run_signals_backtest(
    *,
    symbol: str,
    days: int,
    risk_profile: RiskProfile,
    initial_capital: float = 100.0,
) -> SignalsBacktestResponse:
    # 1. Fetch candles históricos da Binance
    # 2. Para cada posição, chamar _build_signal()
    # 3. Simular trades (entry/exit com target/stop)
    # 4. Calcular métricas
    # 5. Retornar SignalsBacktestResponse
```

### 5.3 Schema de Request/Response

```python
class SignalsBacktestRequest(BaseModel):
    symbol: str
    days: int = 365
    risk_profile: RiskProfile = RiskProfile.moderate
    initial_capital: float = 100.0

class SignalsBacktestResponse(BaseModel):
    symbol: str
    risk_profile: RiskProfile
    metrics: SignalsBacktestMetrics
    trades: List[Trade]
    candles: List[Candle]  # para gráfico
```

### 5.4 Endpoint

```
POST /api/combos/signals-backtest
```

Reaproveita o padrão existente de `ComboBacktestRequest/Response`.

---

## 6. Integração Frontend

### 6.1 Reaproveitamento de UI

O frontend **não precisa de novas páginas**. O fluxo existente do Combo é reaproveitado:

1. `/combo/select` — usuário escolhe template "RSI+MACD+Bollinger Signals"
2. `/combo/configure` — parâmetros: asset, days, risk_profile, initial_capital
3. `/combo/results` — exibe métricas e trades (mesmo componente de Results)

### 6.2 Parâmetros no Configure

A página `ComboConfigurePage` já suporta parâmetros custom via `parameters: Dict[str, Any]`. Precisamos:

1. Definir os parâmetros no template (dias, risk_profile)
2. O frontend envia esses parâmetros no POST de backtest

---

## 7. Decisões de Design

| Decisão | Justificativa |
|---------|---------------|
| Reaproveitar `_build_signal` | Evita duplicação de lógica RSI/MACD/BB |
| Não criar novas páginas frontend | Sistema Combo já tem select/configure/results |
| Parâmetros RSI/MACD/BB fixos | Já calibrados em _PROFILE_SETTINGS |
| Métricas similares ao Combo | UI de Results já espera essas métricas |
| Período default 365 dias | Boa amostragem (1 ano de candles horários) |

---

## 8. O que NÃO está no escopo

- Otimização de parâmetros RSI/MACD/BB (isso seria uma extensão futura)
- Suporte a SELL signals para short (por enquanto só usa BUY para long)
- Alertas em tempo real
- Integração com Telegram ou outras notificações

---

## 9. Diagrama de Sequência

```
┌──────────┐     ┌──────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  Select  │     │ Configure│     │ signals_backtest_   │     │    Results       │
│  Page    │     │  Page    │     │ service             │     │    Page          │
└────┬─────┘     └────┬─────┘     └──────────┬──────────┘     └────────▲─────────┘
     │                │                      │                         │
     │ select template│                      │                         │
     │───────────────▶│                      │                         │
     │                │                      │                         │
     │                │ run backtest POST    │                         │
     │                │─────────────────────▶│                         │
     │                │                      │                         │
     │                │                      │ 1. fetch historical     │
     │                │                      │    candles              │
     │                │                      │ 2. iterate candles      │
     │                │                      │ 3. call _build_signal   │
     │                │                      │ 4. simulate trades      │
     │                │                      │ 5. calculate metrics    │
     │                │                      │                         │
     │                │     response ◀────────┘                         │
     │                │                      │                         │
     │                │ show results ─────────┤                         │
     │                │                      │                         │
```
