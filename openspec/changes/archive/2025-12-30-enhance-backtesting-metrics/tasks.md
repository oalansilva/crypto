# Tasks: Aprimorar Métricas de Backtesting

## Fase 1: Backend - Módulo de Métricas

### 1.1 Estrutura Base
- [ ] Criar diretório `backend/app/metrics/`
- [ ] Criar `__init__.py` com exports
- [ ] Criar `base.py` com classe abstrata `MetricCalculator`

### 1.2 Métricas de Performance
- [ ] Implementar `performance.py`
  - [ ] `calculate_cagr()` - CAGR baseado em período total
  - [ ] `calculate_monthly_return()` - Retorno médio mensal
  - [ ] Testes unitários com dados sintéticos

### 1.3 Métricas de Risco
- [ ] Implementar `risk.py`
  - [ ] `calculate_avg_drawdown()` - Drawdown médio
  - [ ] `calculate_max_dd_duration()` - Tempo máximo em DD (dias)
  - [ ] `calculate_recovery_factor()` - Retorno / Max DD
  - [ ] Testes unitários

### 1.4 Métricas de Retorno Ajustado ao Risco
- [ ] Implementar `risk_adjusted.py`
  - [ ] `calculate_sortino_ratio()` - Penaliza apenas downside
  - [ ] `calculate_calmar_ratio()` - CAGR / Max DD
  - [ ] Testes unitários

### 1.5 Estatísticas de Trades
- [ ] Implementar `trade_stats.py`
  - [ ] `calculate_expectancy()` - Expectativa por trade
  - [ ] `calculate_max_consecutive_wins()` - Maior sequência de ganhos
  - [ ] `calculate_max_consecutive_losses()` - Maior sequência de perdas
  - [ ] `calculate_trade_concentration()` - % lucro dos top trades
  - [ ] Testes unitários

### 1.6 Benchmark
- [ ] Implementar `benchmark.py`
  - [ ] `calculate_buy_and_hold()` - Simular B&H no mesmo período
  - [ ] `calculate_alpha()` - Excesso de retorno vs B&H
  - [ ] `calculate_correlation()` - Correlação com benchmark
  - [ ] `calculate_exposure()` - % tempo posicionado
  - [ ] Testes unitários

### 1.7 Critérios GO/NO-GO
- [ ] Implementar `criteria.py`
  - [ ] `evaluate_go_nogo()` - Retorna dict com status e razões
  - [ ] Critérios configuráveis via constantes
  - [ ] Testes com casos edge (limites exatos)

## Fase 2: Backend - Integração

### 2.1 Schema Updates
- [ ] Atualizar `BacktestMetrics` em `schemas/backtest.py`
  - [ ] Adicionar todos os novos campos de métricas
  - [ ] Adicionar campo `benchmark: BenchmarkMetrics`
  - [ ] Adicionar campo `criteria_result: CriteriaResult`

- [ ] Criar `BenchmarkMetrics` schema
  - [ ] buy_and_hold_return, buy_and_hold_cagr, alpha, correlation, exposure

- [ ] Criar `CriteriaResult` schema
  - [ ] status: "GO" | "NO-GO"
  - [ ] reasons: List[str]
  - [ ] warnings: List[str]

### 2.2 Service Layer
- [ ] Atualizar `backtest_service.py`
  - [ ] Integrar cálculo de todas as métricas após backtest
  - [ ] Calcular benchmark (Buy & Hold) usando mesmos dados
  - [ ] Aplicar critérios GO/NO-GO
  - [ ] Incluir tudo no response

### 2.3 Validação
- [ ] Testes de integração end-to-end
  - [ ] Backtest simples com métricas completas
  - [ ] Verificar cálculo de benchmark
  - [ ] Verificar critérios GO/NO-GO

## Fase 3: Frontend - Visualização

### 3.1 Componentes Base
- [ ] Criar `MetricCard.tsx` - Card reutilizável para métricas
- [ ] Criar `MetricSection.tsx` - Seção colapsável de métricas
- [ ] Criar `GoNoGoIndicator.tsx` - Badge visual de aprovação

### 3.2 Seções de Métricas
- [ ] Criar `PerformanceMetrics.tsx`
  - [ ] Exibir Retorno Total, CAGR, Retorno Mensal
  - [ ] Comparação lado-a-lado com benchmark

- [ ] Criar `RiskMetrics.tsx`
  - [ ] Max DD, DD Médio, Tempo em DD, Recovery Factor
  - [ ] Alertas visuais se MDD > 35%

- [ ] Criar `RiskAdjustedMetrics.tsx`
  - [ ] Sharpe, Sortino, Calmar
  - [ ] Indicadores de qualidade (cores)

- [ ] Criar `TradeStatistics.tsx`
  - [ ] Win Rate, Profit Factor, Expectancy
  - [ ] Sequências de ganhos/perdas
  - [ ] Concentração de lucro

- [ ] Criar `BenchmarkComparison.tsx`
  - [ ] Gráfico comparativo Estratégia vs B&H
  - [ ] Alpha, Correlação, Exposure

### 3.3 Integração na Página de Resultados
- [ ] Atualizar `ResultsPage.tsx` ou componente de resultados
  - [ ] Adicionar `GoNoGoIndicator` no topo
  - [ ] Organizar seções de métricas em tabs ou accordion
  - [ ] Seção "Resumo Executivo" com métricas chave

### 3.4 Alertas e Avisos
- [ ] Implementar sistema de alertas visuais
  - [ ] Alerta vermelho se NO-GO
  - [ ] Avisos amarelos para métricas no limite
  - [ ] Dicas de interpretação (tooltips)

## Fase 4: Documentação e Polimento

### 4.1 Documentação Técnica
- [ ] Documentar fórmulas de cada métrica em `docs/metrics.md`
- [ ] Adicionar exemplos de interpretação
- [ ] Documentar critérios GO/NO-GO e como ajustá-los

### 4.2 Testes
- [ ] Testes unitários para todos os cálculos (>90% coverage)
- [ ] Testes de integração backend
- [ ] Testes E2E frontend (Playwright/Cypress)

### 4.3 Performance
- [ ] Benchmark de performance dos cálculos
- [ ] Otimizar se necessário (caching, vetorização)

### 4.4 UX
- [ ] Adicionar loading states durante cálculos
- [ ] Adicionar tooltips explicativos
- [ ] Testar com usuários e coletar feedback

## Dependências

- **Fase 2** depende de **Fase 1** completa
- **Fase 3** depende de **Fase 2.1** (schemas)
- **Fase 4** pode ser paralela às demais

## Estimativa

- **Fase 1**: 3-4 dias (desenvolvimento + testes)
- **Fase 2**: 1-2 dias (integração)
- **Fase 3**: 2-3 dias (UI components)
- **Fase 4**: 1 dia (docs + polish)

**Total**: ~7-10 dias de desenvolvimento
