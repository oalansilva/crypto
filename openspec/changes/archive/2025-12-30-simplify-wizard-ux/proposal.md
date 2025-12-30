# Proposta: Simplificar Wizard de Backtest e Melhorar UX

## Objetivo
Criar uma interface simples e intuitiva para testar **indicadores individuais**, permitindo que o usuário:
1. Selecione um indicador por vez (RSI, SMA, MACD, etc.)
2. Ajuste apenas os parâmetros daquele indicador
3. Execute o backtest e veja os resultados

**Foco**: Testar cada indicador separadamente, não combinar múltiplos indicadores em estratégias complexas.

## Problema Atual

### Interface Muito Complexa
- **StrategyBuilder**: Lista enorme de indicadores (100+) sem organização clara
- **Sobrecarga Visual**: Muitos botões, categorias e opções visíveis simultaneamente
- **Não Usual**: Interface não segue padrões familiares de formulários web
- **Curva de Aprendizado**: Usuário precisa entender toda a estrutura antes de usar

### Feedback do Usuário
> "não gostei dessa interface achei pouco usual"

A interface atual tenta expor toda a flexibilidade do sistema de uma vez, mas isso cria uma experiência intimidadora e confusa.

## Solução Proposta

### 1. Wizard Simplificado (3 Etapas Claras)

#### **Etapa 1: Configuração Básica**
```
┌─────────────────────────────────────┐
│ 1. Configuração do Backtest         │
├─────────────────────────────────────┤
│                                     │
│ Símbolo:     [BTC/USDT ▼]          │
│ Timeframe:   [1d ▼]                │
│ Período:     [Últimos 12 meses ▼]  │
│              ou                     │
│ De:          [01/01/2024]          │
│ Até:         [28/12/2024]          │
│                                     │
│         [Próximo: Estratégia →]    │
└─────────────────────────────────────┘
```

#### **Etapa 2: Selecione um Indicador**
```
┌─────────────────────────────────────┐
│ 2. Escolha o Indicador para Testar  │
├─────────────────────────────────────┤
│                                     │
│ 🔍 Buscar indicador...              │
│                                     │
│ Populares:                          │
│ ┌─────────────────────────────┐    │
│ │ ○ RSI (14)                   │    │
│ │   Reversão por sobrecompra   │    │
│ │                              │    │
│ │ ● SMA Cross (20, 50)         │    │
│ │   Cruzamento de médias       │    │
│ │                              │    │
│ │ ○ MACD (12, 26, 9)           │    │
│ │   Convergência/divergência   │    │
│ │                              │    │
│ │ ○ Bollinger Bands (20, 2.0)  │    │
│ │   Bandas de volatilidade     │    │
│ │                              │    │
│ │ ○ Stochastic (14, 3, 3)      │    │
│ │   Momentum oscilador         │    │
│ └─────────────────────────────┘    │
│                                     │
│ Parâmetros (SMA Cross):             │
│ Período Rápido:  [20]              │
│ Período Lento:   [50]              │
│                                     │
│   [← Voltar]  [Próximo: Risco →]   │
└─────────────────────────────────────┘
```

**Nota**: Cada indicador vem com sua lógica de entrada/saída pré-definida e valores padrão do mercado.

#### **Etapa 3: Gestão de Risco**
```
┌─────────────────────────────────────┐
│ 3. Gestão de Risco                  │
├─────────────────────────────────────┤
│                                     │
│ Capital Inicial:  [$10,000]        │
│ Taxa de Trading:  [0.1%]           │
│                                     │
│ Avançado (Opcional):                │
│ ▼ Mostrar opções avançadas          │
│                                     │
│   [← Voltar]  [▶ Executar Backtest]│
└─────────────────────────────────────┘
```

### 2. Melhorias de UX

#### **Indicadores Populares em Destaque**
- Mostrar apenas 5-10 indicadores mais usados por padrão
- Busca com autocomplete para encontrar outros
- Categorias colapsáveis (não todas abertas)

#### **Presets Inteligentes**
- "Últimos 12 meses", "Últimos 6 meses", "Ano atual"
- Reduz necessidade de selecionar datas manualmente

#### **Feedback Visual Claro**
- Progress bar mostrando etapa atual (1/3, 2/3, 3/3)
- Validação em tempo real (campos obrigatórios)
- Mensagens de erro claras e específicas

#### **Modo Rápido**
- Opção de "Usar configurações padrão" em cada etapa
- Permite executar backtest em 3 cliques

## Comparação: Antes vs. Depois

### Antes (Atual)
- ❌ 100+ indicadores visíveis simultaneamente
- ❌ Interface não familiar (sidebar + grid + tabs)
- ❌ Muitas decisões para tomar de uma vez
- ❌ Difícil encontrar o que precisa
- ❌ Estratégias prontas limitadas (apenas 3)

### Depois (Proposto)
- ✅ Wizard linear de 3 etapas
- ✅ Busca inteligente de indicadores
- ✅ Uma decisão por vez
- ✅ Indicadores populares em destaque
- ✅ Apenas estratégias personalizadas (flexibilidade total)
- ✅ Valores padrão do mercado pré-configurados

## Valores Padrão Baseados no Mercado

### Parâmetros de Indicadores (Padrões da Indústria)

#### **Médias Móveis**
- SMA Rápida: **20 períodos** (padrão TradingView)
- SMA Lenta: **50 períodos** (padrão institucional)
- EMA Rápida: **12 períodos** (MACD padrão)
- EMA Lenta: **26 períodos** (MACD padrão)

#### **Osciladores**
- RSI: **14 períodos** (padrão Wilder)
  - Oversold: **30** (conservador para crypto)
  - Overbought: **70** (conservador para crypto)
- MACD: **12, 26, 9** (padrão universal)
- Stochastic: **14, 3, 3** (padrão George Lane)

#### **Volatilidade**
- Bollinger Bands: **20 períodos, 2.0 desvios** (padrão John Bollinger)
- ATR: **14 períodos** (padrão Wilder)

#### **Volume**
- Volume SMA: **20 períodos** (padrão mercado)

### Parâmetros de Backtest

#### **Período de Teste**
- Padrão: **Últimos 12 meses** (1 ano completo)
- Mínimo recomendado: 6 meses
- Ideal: 2-3 anos (múltiplos ciclos de mercado)

#### **Gestão de Risco**
- Capital Inicial: **$10,000** (valor educacional padrão)
- Taxa de Trading: **0.1%** (média Binance/Coinbase)
- Slippage: **0.05%** (conservador para crypto)
- Stop Loss: **2%** (padrão day trading)
- Take Profit: **5%** (ratio 1:2.5)

#### **Timeframes Recomendados**
- **Day Trading**: 15m, 30m, 1h
- **Swing Trading**: 4h, 1d (padrão)
- **Position Trading**: 1d, 3d, 1w

### Justificativa dos Valores

Esses valores são baseados em:
1. **Literatura Técnica**: Livros clássicos (Wilder, Bollinger, Murphy)
2. **Plataformas Populares**: TradingView, MetaTrader, Binance
3. **Estudos Empíricos**: Pesquisas acadêmicas sobre eficácia
4. **Consenso da Comunidade**: Valores mais usados por traders profissionais

### Implementação no Código

```typescript
// Valores padrão para indicadores
const INDICATOR_DEFAULTS = {
  sma: { fast: 20, slow: 50 },
  ema: { fast: 12, slow: 26 },
  rsi: { period: 14, oversold: 30, overbought: 70 },
  macd: { fast: 12, slow: 26, signal: 9 },
  bollinger: { period: 20, std: 2.0 },
  atr: { period: 14 },
  stochastic: { k: 14, d: 3, smooth: 3 }
}

// Valores padrão para backtest
const BACKTEST_DEFAULTS = {
  capital: 10000,
  fee: 0.001,        // 0.1%
  slippage: 0.0005,  // 0.05%
  stopLoss: 0.02,    // 2%
  takeProfit: 0.05,  // 5%
  timeframe: '1d',
  period: 'last_12_months'
}
```

## Implementação

### Frontend
1. **Simplificar BacktestWizard.tsx**:
   - Remover complexidade visual
   - Focar em campos essenciais
   - Adicionar presets de período

2. **Refatorar StrategyBuilder.tsx**:
   - Modal em vez de tela cheia
   - Busca com autocomplete
   - Mostrar apenas indicadores selecionados
   - Categorias colapsadas por padrão

3. **Adicionar Componentes de Ajuda**:
   - Tooltips explicativos
   - Exemplos de condições
   - Link para documentação

### Backend
- Nenhuma mudança necessária
- API já suporta todas as funcionalidades

## Verificação

- [ ] Usuário consegue criar backtest em ≤ 5 cliques
- [ ] Interface parece familiar e intuitiva
- [ ] Busca de indicadores funciona corretamente
- [ ] Presets de período funcionam
- [ ] Validação de campos é clara

## Próximos Passos

1. Aprovar proposta
2. Implementar wizard simplificado
3. Refatorar StrategyBuilder para modal
4. Adicionar presets e busca
5. Testar com usuário real
