# Aprimorar Métricas de Backtesting (MVP Profissional)

## Contexto

O backtester atual fornece métricas básicas, mas não responde às perguntas fundamentais que um trader precisa saber antes de arriscar capital real:

1. **"Essa estratégia é melhor do que não fazer nada?"**
2. **"Ela compensa o risco que assume?"**
3. **"Ela é repetível?"**

Esta mudança implementa um conjunto completo de métricas profissionais que transformam o backtester em uma ferramenta de validação robusta, incluindo critérios automatizados de aprovação (GO/NO-GO).

## Objetivo

Implementar métricas obrigatórias e opcionais que permitam avaliar estratégias de forma profissional, comparando-as com benchmarks e aplicando critérios objetivos de aprovação.

## Escopo

### Backend
- **Módulo de Métricas**: `backend/app/metrics/` (novo)
  - `performance.py`: CAGR, retorno médio mensal
  - `risk.py`: Max Drawdown, Drawdown médio, tempo em drawdown
  - `risk_adjusted.py`: Sharpe, Sortino, Calmar ratios
  - `trade_stats.py`: Profit Factor, Expectancy, sequências
  - `benchmark.py`: Buy & Hold, Alpha, correlação
  - `criteria.py`: Validação GO/NO-GO automatizada

- **Service Layer**: `backend/app/services/backtest_service.py`
  - Integração do cálculo de todas as métricas
  - Cálculo de benchmark (Buy & Hold)
  - Aplicação de critérios GO/NO-GO

- **Schema**: `backend/app/schemas/backtest.py`
  - Expansão de `BacktestMetrics` com todas as novas métricas
  - Novo schema `BacktestCriteria` para GO/NO-GO

### Frontend
- **Results Display**: `frontend/src/components/results/`
  - **Integração com página existente**: Todas as métricas serão exibidas quando o usuário clica em "Ver Resultados"
  - Seções organizadas por categoria de métrica (colapsáveis para não sobrecarregar)
  - Indicador visual GO/NO-GO no topo da página
  - Comparação lado-a-lado com benchmark
  - Alertas para métricas fora dos limites aceitáveis
  - **Objetivo**: Ajudar o usuário a escolher a melhor estratégia com dados objetivos

### Fluxo do Usuário
1. Usuário executa backtest (único ou otimização)
2. Clica em "Ver Resultados"
3. **Vê imediatamente**:
   - Badge GO/NO-GO no topo (decisão rápida)
   - Métricas essenciais em cards destacados
   - Seções expandíveis com métricas detalhadas
   - Comparação com Buy & Hold
   - Recomendações baseadas nos critérios

## Métricas a Implementar

### 1️⃣ Performance (Obrigatórias)
- ✅ Retorno Total (%) - *já existe*
- 🆕 CAGR (%) - Compound Annual Growth Rate
- 🆕 Retorno Médio Mensal (%)

### 2️⃣ Risco (Obrigatórias - Não-negociáveis)
- ✅ Max Drawdown (%) - *já existe*
- 🆕 Drawdown Médio (%)
- 🆕 Tempo Máximo em Drawdown (dias)
- 🆕 Recovery Factor (Retorno / Max DD)

### 3️⃣ Retorno Ajustado ao Risco (Obrigatórias)
- ✅ Sharpe Ratio - *já existe*
- 🆕 Sortino Ratio (penaliza apenas volatilidade negativa)
- 🆕 Calmar Ratio (CAGR / Max DD) ⭐ **Excelente para swing**

### 4️⃣ Trades & Probabilidade (Obrigatórias)
- ✅ Total de Trades - *já existe*
- ✅ Win Rate (%) - *já existe*
- ✅ Profit Factor - *já existe*
- 🆕 Expectancy por Trade ($)
- 🆕 Maior Sequência de Perdas
- 🆕 Maior Sequência de Ganhos

### 5️⃣ Custos & Realismo (Obrigatórias)
- ✅ Taxas Totais Pagas - *já existe*
- 🆕 Slippage Total (%)
- 🆕 Retorno Líquido (%) - após todos os custos

### 6️⃣ Benchmark (Obrigatório)
- 🆕 Buy & Hold Retorno (%)
- 🆕 Buy & Hold CAGR (%)
- 🆕 Excesso de Retorno (Alpha) - Estratégia vs B&H
- 🆕 Correlação com Benchmark
- 🆕 Percentual do Tempo Posicionado (Exposure %)

### 7️⃣ Critérios GO/NO-GO (Automatizado)

**✅ GO se:**
- CAGR > Buy & Hold
- Max Drawdown ≤ 35%
- Calmar Ratio ≥ 1.0
- Profit Factor ≥ 1.3
- Expectancy > 0
- Total de Trades ≥ 100

**❌ NO-GO se:**
- Lucro concentrado em 1-2 trades
- Sharpe Ratio < 0.8
- Max Drawdown > 45%

## Métricas Opcionais (Versão 1.1 - Futuro)
- Ulcer Index
- Expectancy ajustada por volatilidade
- Information Ratio
- Omega Ratio

## Benefícios

1. **Decisões Objetivas**: Critérios claros de aprovação/rejeição
2. **Comparação Justa**: Benchmark automático (Buy & Hold)
3. **Gestão de Risco**: Métricas de drawdown e recuperação
4. **Realismo**: Custos e slippage sempre visíveis
5. **Profissionalismo**: Métricas padrão da indústria

## Impacto

- **Usuários**: Confiança para colocar estratégias em produção
- **Código**: Módulo de métricas reutilizável e testável
- **UI**: Interface clara e informativa com alertas visuais

## Dependências

- Nenhuma mudança de infraestrutura necessária
- Compatível com sistema atual de backtesting
- Métricas calculadas após execução do backtest

## Riscos

- **Complexidade**: Muitas métricas podem confundir usuários iniciantes
  - *Mitigação*: Organizar em seções colapsáveis, destacar as essenciais
  
- **Performance**: Cálculo de métricas adicionais pode aumentar tempo de processamento
  - *Mitigação*: Cálculos são leves (operações matemáticas simples sobre arrays)

## Próximos Passos

1. Criar specs detalhadas para cada categoria de métrica
2. Implementar módulo de métricas no backend
3. Atualizar schemas e service layer
4. Criar componentes de visualização no frontend
5. Adicionar testes unitários para cada métrica
6. Documentar fórmulas e interpretação de cada métrica
