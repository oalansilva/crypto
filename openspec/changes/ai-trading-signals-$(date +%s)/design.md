# OpenSpec Design Artifact — AI Trading Signals & Portfolio Optimization

## 1. Conceito & Visão

**Nome:** CryptoMind AI  
**Tagline:** "Inteligência artificial para decisões de trading mais inteligentes"

**Resumo:** Motor de IA que analisa dados de mercado em tempo real, gera sinais de compra/venda e recomenda otimizações de portfólio. Diferencial competitivo: automação completa vs. análise manual predominante em TradingView e CoinGecko.

**Proposta de Valor:**
- Sinais de trading gerados por ML em tempo real
- Otimização de portfólio automática baseada em risco/retorno
- Dashboard unificado com métricas de IA e tradicional
- Histórico de sinais para backtesting

---

## 2. Layout & Estrutura

### 2.1 Arquitetura de Páginas

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: Logo + Navigation + Wallet Status + User Menu           │
├───────────┬─────────────────────────────────────────────────────┤
│           │                                                     │
│  SIDEBAR  │  MAIN CONTENT AREA                                  │
│           │                                                     │
│  - Dashboard│  [Dynamic based on selected view]                 │
│  - Signals  │                                                   │
│  - Portfolio│                                                   │
│  - History  │                                                   │
│  - Settings │                                                   │
│           │                                                     │
└───────────┴─────────────────────────────────────────────────────┘
```

### 2.2 Páginas Principais

#### 2.2.1 Dashboard (Home)
- Resumo de performance da IA
- Top 3 sinais do dia
- Alocação atual do portfólio
- Tendências detectadas

#### 2.2.2 Sinais de Trading
- Lista de sinais ativos (compra/venda/hold)
- Confiança do sinal (0-100%)
- Ativo, preço-alvo, stop-loss
- Filtros: tipo, confiança, timeframe

#### 2.2.3 Portfolio Optimizer
- Alocação atual vs. recomendada
- Simulação de rebalanceamento
- Métricas de risco (Sharpe, Volatilidade, VaR)
- Botão "Aplicar Recomendação"

#### 2.2.4 Histórico de Sinais
- Timeline de sinais passados
- Performance real vs. predita
- Backtesting de estratégias

---

## 3. Componentes de UI

### 3.1 SignalCard
```
┌──────────────────────────────────────┐
│ 🟢 BUY  │  BTC/USDT  │  Conf: 87%   │
│─────────┴────────────┴───────────────│
│ Preço Atual: $67,432                 │
│ Preço-Alvo:   $72,500 (+7.5%)        │
│ Stop-Loss:    $64,200 (-4.8%)        │
│─────────────────────────────────────│
│ Modelo: LSTM + RandomForest Ensemble │
│ Timeframe: 4H                        │
│ Updated: 2 min ago                   │
└──────────────────────────────────────┘
```

**Estados:**
- BUY (verde), SELL (vermelho), HOLD (amarelo)
- Confidence: alta (>75%), média (50-75%), baixa (<50%)
- Loading: skeleton com shimmer
- Error: mensagem com retry

### 3.2 PortfolioChart
- Gráfico de pizza: alocação atual
- Gráfico de barras: alocação recomendada
- Toggle: "Atual vs. Recomendada"
- Tooltip com % e valor em USD

### 3.3 AIInsightBanner
```
┌─────────────────────────────────────────────────────┐
│ 🤖 AI Insight: Bitcoin em tendência de alta.        │
│    Recomendação: Aumentar exposição em 15%.         │
│    [Ver Detalhes]  [Ignorar]                        │
└─────────────────────────────────────────────────────┘
```

### 3.4 MetricCard
- Título + Ícone
- Valor principal (grande)
- Variação (% com cor verde/vermelha)
- Trend sparkline (últimos 7 dias)

### 3.5 ConfidenceGauge
- Gauge semicircular 0-100%
- Cores: vermelho (0-40), amarelo (40-70), verde (70-100)
- Label central com valor

---

## 4. Fluxos de Usuário

### 4.1 Fluxo: Verificar Sinal e Operar
```
1. Usuário acessa "Sinais de Trading"
2. Sistema carrega sinais do dia
3. Usuário filtra por: ativo, tipo, confiança
4. Usuário clica em SignalCard
5. Modal abre com detalhes completos:
   - Gráfico de preço com indicadores
   - Métricas do modelo
   - Histórico de sinais similares
6. Usuário clica "Simular Trade"
7. Modal: valor投入, cálculo de profit/loss
8. Confirmação de execução (mock API)
```

### 4.2 Fluxo: Otimizar Portfólio
```
1. Usuário acessa "Portfolio Optimizer"
2. Sistema carrega alocação atual
3. Sistema calcula alocação ótima (ML)
4. Dashboard mostra: atual vs. recomendada
5. Usuário clica "Aplicar Recomendação"
6. Modal: resumo das mudanças
7. Confirmação → API de rebalanceamento
```

### 4.3 Fluxo: Acompanhar Tendências
```
1. Dashboard mostra AIInsightBanner
2. Usuário clica "Ver Detalhes"
3. Página de tendência abre:
   - Ativo + direção
   - Indicadores que dispararam
   - Sinais relacionados
   - Previsão de preço
```

---

## 5. API Endpoints

### 5.1 Sinais de Trading
```
GET  /api/v1/ai/signals
     Query: ?status=active&confidence_min=70&asset=BTC
     Response: { signals: [...], total, page }

GET  /api/v1/ai/signals/:id
     Response: { signal, related_signals, model_info }

POST /api/v1/ai/signals/:id/simulate
     Body: { amount, side }
     Response: { simulation, expected_result }
```

### 5.2 Portfolio
```
GET  /api/v1/ai/portfolio/allocation
     Response: { current: [...], recommended: [...], metrics }

GET  /api/v1/ai/portfolio/rebalance
     Body: { target_allocation }
     Response: { trades_needed, estimated_cost, new_metrics }

GET  /api/v1/ai/portfolio/metrics
     Response: { sharpe_ratio, volatility, var_95, max_drawdown }
```

### 5.3 Tendências
```
GET  /api/v1/ai/trends
     Query: ?asset=BTC&timeframe=4h
     Response: { trends: [...], detected_at }

GET  /api/v1/ai/trends/:asset/history
     Response: { price_predictions: [...], actual: [...] }
```

### 5.4 Dashboard
```
GET  /api/v1/ai/dashboard/summary
     Response: { 
       top_signals: [...], 
       portfolio_summary: {...}, 
       daily_insight: {...},
       performance: { daily, weekly, monthly }
     }
```

---

## 6. Modelo de Dados

### 6.1 Signal
```typescript
interface Signal {
  id: string;
  asset: string;           // "BTC/USDT"
  type: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;      // 0-100
  current_price: number;
  target_price: number;
  stop_loss: number;
  timeframe: string;       // "4H", "1D"
  model: string;           // "LSTM+RF Ensemble"
  indicators: string[];    // ["RSI", "MACD", "BB"]
  created_at: string;
  updated_at: string;
  status: 'active' | 'triggered' | 'expired';
}
```

### 6.2 Portfolio
```typescript
interface Portfolio {
  id: string;
  user_id: string;
  positions: Position[];
  total_value_usd: number;
  last_rebalanced: string;
  risk_profile: 'conservative' | 'moderate' | 'aggressive';
}

interface Position {
  asset: string;
  amount: number;
  value_usd: number;
  allocation_percent: number;
  current_price: number;
  pnl_24h: number;
}

interface RecommendedAllocation {
  asset: string;
  current_percent: number;
  recommended_percent: number;
  action: 'BUY' | 'SELL' | 'HOLD';
  amount: number;
}
```

### 6.3 Trend
```typescript
interface Trend {
  id: string;
  asset: string;
  direction: 'bullish' | 'bearish' | 'neutral';
  strength: number;        // 0-100
  indicators_triggered: string[];
  predicted_move: number; // % expected
  timeframe: string;
  detected_at: string;
}
```

---

## 7. Protótipo

### Link do Protótipo (Figma/Similar)
> **Protótipo interativo:** https://www.figma.com/proto/placeholder-cryptomind-ai

*(Nota: Em produção, exportar Figma Embedded ou usar Observable/Streamlit para demo interativo)*

### Protótipo Low-Fidelity (HTML/CSS/JS)
Local: `openspec/changes/ai-trading-signals-1774561466/prototype/`

O protótipo básico inclui:
- Dashboard com cards de sinais
- SignalCard interativo
- Simulação de portfolio
- AIInsightBanner

### Screenshots do Protótipo

#### Dashboard View
![Dashboard](prototype/screenshots/dashboard.png)

#### Signal Detail Modal
![Signal Modal](prototype/screenshots/signal-modal.png)

---

## 8. Stack Técnica (Recomendada)

### Frontend
- **Framework:** React 18 + TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **Charts:** Recharts / TradingView Lightweight Charts
- **State:** Zustand / TanStack Query

### Backend
- **API:** FastAPI (Python) ou Node.js + Express
- **ML Engine:** Python (scikit-learn, TensorFlow/PyTorch)
- **Real-time:** WebSocket para sinais ao vivo
- **Cache:** Redis para sinais frequentes

### Data
- **Price Data:** CoinGecko Pro / Binance API
- **Historical:** TimescaleDB / InfluxDB
- **Signals Storage:** PostgreSQL

---

## 9. Métricas de Sucesso

| Métrica | Target | Medição |
|---------|--------|---------|
| Sinais gerados/dia | 50+ | Contagem |
| Acurácia de sinais | >65% | Backtest |
| Tempo de resposta | <200ms | APM |
| Engajamento | 3+ views/sinal | Analytics |
| Portfolio optimization | 10% mais retorno | Comparativo |

---

## 10. Roadmap de Implementação

| Fase | Escopo | Prioridade |
|------|--------|------------|
| MVP | Dashboard + SignalCard + API básica | Alta |
| v1.1 | Portfolio Optimizer + Rebalance | Alta |
| v1.2 | Histórico + Backtesting | Média |
| v2.0 | WebSocket temps real + Notificações | Média |

---

## 11. Riscos & Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Sinais imprecisos | Alta | Alto | Confiança mínima 70%, disclaimer |
| Overfitting do modelo | Alta | Alto | Validação cruzada, regime de teste |
| Latência de dados | Média | Médio | Cache agressivo, múltiplas fontes |
| Manipulação de mercado | Baixa | Alto | Disclaimer, não é advice financeiro |

---

*Design artifact criado em: 2026-03-26 21:44 UTC*  
*DESIGN Agent — CryptoTracker Project*
