# OpenSpec Tasks — AI Trading Signals & Portfolio Optimization

## Card #51 — CryptoMind AI Implementation Tasks

**Projeto:** CryptoTracker  
**Owner:** DEV Agent  
**PO Review:** ✅ Aprovado  
**Design:** ✅ Aprovado  
**Alan Approval:** ⏳ Pendente  

---

## 1. Tarefas de Infraestrutura

### 1.1 Setup de Ambiente

- [ ] Configurar ambiente Python 3.11+ com virtualenv
- [ ] Instalar dependências: scikit-learn, TensorFlow/PyTorch, pandas, numpy
- [ ] Configurar Redis para cache de sinais
- [ ] Setup TimescaleDB para dados temporais
- [ ] Configurar PostgreSQL para dados estruturados
- [ ] Obter credenciais CoinGecko Pro API
- [ ] Obter credenciais Binance API (backup)

### 1.2 Backend Setup

- [ ] Criar projeto FastAPI com estrutura modular
- [ ] Implementar conexão com Redis
- [ ] Implementar conexão com TimescaleDB
- [ ] Implementar conexão com PostgreSQL
- [ ] Configurar ambiente `.env` com todas as variáveis
- [ ] Setup logging estruturado

---

## 2. Tarefas de Backend — API

### 2.1 Signals API

- [ ] `GET /api/v1/ai/signals` — listar sinais com filtros
- [ ] `GET /api/v1/ai/signals/:id` — detalhe de um sinal
- [ ] `POST /api/v1/ai/signals/:id/simulate` — simular trade
- [ ] Implementar paginação
- [ ] Implementar filtros: status, confidence_min, asset

### 2.2 Portfolio API

- [ ] `GET /api/v1/ai/portfolio/allocation` — alocação atual vs. recomendada
- [ ] `GET /api/v1/ai/portfolio/rebalance` — calcular rebalanceamento
- [ ] `GET /api/v1/ai/portfolio/metrics` — métricas de risco

### 2.3 Trends API

- [ ] `GET /api/v1/ai/trends` — listar tendências detectadas
- [ ] `GET /api/v1/ai/trends/:asset/history` — histórico de previsões

### 2.4 Dashboard API

- [ ] `GET /api/v1/ai/dashboard/summary` — resumo consolidado

---

## 3. Tarefas de Backend — ML Engine

### 3.1 Data Pipeline

- [ ] Implementar fetcher de dados CoinGecko (preços, volume)
- [ ] Implementar fetcher de dados Binance (backup)
- [ ] Implementar normalização de dados
- [ ] Implementar cache Redis para dados frequentes
- [ ] Criar schema no TimescaleDB para price history

### 3.2 Signal Generation Model

- [ ] Implementar modelo LSTM para previsão de preço
- [ ] Implementar modelo RandomForest para classificação BUY/SELL/HOLD
- [ ] Implementar ensemble (LSTM + RF)
- [ ] Calcular confiança do sinal (0-100%)
- [ ] Implementar indicadores: RSI, MACD, Bollinger Bands
- [ ] Definir threshold mínimo de confiança (sugestão: 70%)

### 3.3 Portfolio Optimization Model

- [ ] Implementar cálculo de Sharpe Ratio
- [ ] Implementar cálculo de Volatilidade
- [ ] Implementar VaR (Value at Risk) 95%
- [ ] Implementar Max Drawdown
- [ ] Implementar otimizador de alocação (Markowitz ou similar)
- [ ] Suporte a perfis: conservative, moderate, aggressive

### 3.4 Trend Detection

- [ ] Implementar detector de tendência (bullish/bearish/neutral)
- [ ] Calcular strength da tendência (0-100%)
- [ ] Identificar indicadores que dispararam

---

## 4. Tarefas de Frontend — Core

### 4.1 Setup

- [ ] Setup React 18 + TypeScript
- [ ] Configurar Tailwind CSS
- [ ] Instalar shadcn/ui
- [ ] Configurar TanStack Query para estado de servidor
- [ ] Setup Recharts para gráficos
- [ ] Setup TradingView Lightweight Charts

### 4.2 Layout Base

- [ ] Header com Logo + Navigation + Wallet Status + User Menu
- [ ] Sidebar com navegação: Dashboard, Signals, Portfolio, History, Settings
- [ ] Layout responsivo

### 4.3 Dashboard Page

- [ ] Resumo de performance da IA (cards)
- [ ] Top 3 sinais do dia
- [ ] Alocação atual do portfólio (PortfolioChart)
- [ ] AIInsightBanner com tendência
- [ ] Métricas: daily, weekly, monthly performance

### 4.4 Signals Page

- [ ] Lista de SignalCards
- [ ] Filtros: tipo, confiança, timeframe, ativo
- [ ] SignalCard component com estados (BUY/SELL/HOLD)
- [ ] ConfidenceGauge component
- [ ] Modal de detalhes do sinal
- [ ] Simulação de trade

### 4.5 Portfolio Page

- [ ] PortfolioChart (pizza: atual, barras: recomendada)
- [ ] Toggle "Atual vs. Recomendada"
- [ ] Métricas de risco (MetricCard)
- [ ] Botão "Aplicar Recomendação"
- [ ] Modal de confirmação de rebalanceamento

### 4.6 History Page

- [ ] Timeline de sinais passados
- [ ] Performance real vs. predita
- [ ] Gráfico comparativo

---

## 5. Tarefas de Frontend — Componentes

### 5.1 SignalCard

- [ ] Estados visuais: BUY (verde), SELL (vermelho), HOLD (amarelo)
- [ ] Níveis de confiança: alta (>75%), média (50-75%), baixa (<50%)
- [ ] Loading state com skeleton + shimmer
- [ ] Error state com retry button
- [ ] Exibição: ativo, preço atual, preço-alvo, stop-loss, timeframe, modelo

### 5.2 PortfolioChart

- [ ] Gráfico de pizza (alocação atual)
- [ ] Gráfico de barras (alocação recomendada)
- [ ] Tooltip com % e valor USD
- [ ] Animação de transição

### 5.3 AIInsightBanner

- [ ] Layout com ícone + texto
- [ ] Botões "Ver Detalhes" e "Ignorar"
- [ ] Animação de entrada

### 5.4 MetricCard

- [ ] Título + ícone
- [ ] Valor principal grande
- [ ] Variação percentual (verde/vermelho)
- [ ] Sparkline (últimos 7 dias)

### 5.5 ConfidenceGauge

- [ ] Gauge semicircular 0-100%
- [ ] Cores: vermelho (0-40), amarelo (40-70), verde (70-100)
- [ ] Label central com valor numérico

---

## 6. Tarefas de UX/UI

### 6.1 Disclaimer Legal

- [ ] Adicionar disclaimer em todas as páginas de sinais: "Não é advice financeiro"
- [ ] Modal de confirmação antes de usar sinais para decisão
- [ ] Tooltip explicando como os sinais são gerados

### 6.2 Estados e Edge Cases

- [ ] Empty state: sem sinais disponíveis
- [ ] Loading state: skeleton em todos os componentes
- [ ] Error state: mensagem + retry para cada API
- [ ] Timeout state: API lenta (>2s)
- [ ] Offline state: sem conexão

---

## 7. Tarefas de Testes

### 7.1 Backend Tests

- [ ] Unit tests para modelos ML
- [ ] Integration tests com APIs CoinGecko/Binance (mock)
- [ ] API endpoint tests
- [ ] Load tests para latência <200ms

### 7.2 Frontend Tests

- [ ] Component tests para SignalCard
- [ ] Component tests para PortfolioChart
- [ ] Integration tests para fluxos principais
- [ ] Visual regression tests

### 7.3 E2E Tests (Playwright)

- [ ] Fluxo: ver sinal → filtrar → abrir detalhe → simular
- [ ] Fluxo: ver portfólio → comparar alocações → aplicar recomendação
- [ ] Smoke tests para todas as páginas

---

## 8. Tarefas de Deploy

### 8.1 Backend

- [ ] Dockerizar aplicação FastAPI
- [ ] Configurar CI/CD (GitHub Actions)
- [ ] Deploy em staging
- [ ] Deploy em produção

### 8.2 Frontend

- [ ] Build de produção
- [ ] Deploy em CDN (Vercel/Cloudflare)
- [ ] Configurar environment variables

---

## 9. Checklist de Homologação

### Funcionalidades

- [ ] Dashboard carrega com resumo de IA
- [ ] SignalCard exibe corretamente BUY/SELL/HOLD
- [ ] ConfidenceGauge mostra nível correto
- [ ] Filtros de sinais funcionam
- [ ] Portfolio Optimizer calcula alocação
- [ ] Métricas de risco são exibidas
- [ ] AIInsightBanner aparece com tendência
- [ ] Disclaimer é exibido antes de usar sinais

### Performance

- [ ] Tempo de resposta API <200ms
- [ ] Frontend carrega em <3s
- [ ] Sem Memory leaks em uso prolongado

### Acessibilidade

- [ ] Contraste de cores adequado
- [ ] Navegação por teclado funciona
- [ ] Screen reader friendly

---

## 10. Estimativa de Esforço

| Fase | Tarefas | Estimativa |
|------|---------|------------|
| Infra + Backend Core | Setup + APIs | 16h |
| ML Engine | Models + Training | 16h |
| Frontend Core | Pages + Layout | 12h |
| Frontend Components | SignalCard, etc | 8h |
| Tests + QA | Unit + E2E | 8h |
| Deploy + Fixes | Staging + Prod | 4h |
| **Total MVP** | | **64h** |

---

## 11. Dependências Entre Tarefas

```
[Infra Setup] → [Backend APIs] → [ML Engine] → [Frontend]
                      ↓
              [Frontend APIs]
                      
[Frontend] + [ML Engine] → [Integration Tests]
                            ↓
                      [E2E Tests] → [Deploy]
```

---

## 12. Notas para DEV

1. **Começar por**: Infra + Backend APIs (paralelo com ML Engine)
2. **Disclaimer obrigatório**: implementar em todas as telas de sinais
3. **Confiança mínima**: 70% para exibir sinal na lista
4. **Mock data**: usar dados mock enquanto API real não está pronta
5. **Cache Redis**: implementar desde o início para performance

---

*Tasks criadas pelo PO Agent em: 2026-03-26 21:59 UTC*  
*Card #51 — CryptoTracker Project*
