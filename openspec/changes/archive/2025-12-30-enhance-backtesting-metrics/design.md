# Design: Aprimorar Métricas de Backtesting

## Visão Arquitetural

### Princípios de Design

1. **Modularidade**: Cada categoria de métrica em seu próprio módulo
2. **Testabilidade**: Funções puras, fáceis de testar
3. **Extensibilidade**: Fácil adicionar novas métricas no futuro
4. **Performance**: Cálculos eficientes usando NumPy/Pandas
5. **Clareza**: Código autodocumentado com type hints

### Estrutura de Módulos

```
backend/app/metrics/
├── __init__.py           # Exports públicos
├── base.py               # Classes base e interfaces
├── performance.py        # CAGR, retorno mensal
├── risk.py               # Drawdown, recovery
├── risk_adjusted.py      # Sharpe, Sortino, Calmar
├── trade_stats.py        # Expectancy, sequências
├── benchmark.py          # Buy & Hold, Alpha
└── criteria.py           # GO/NO-GO validation
```

## Decisões Técnicas

### 1. Cálculo de Métricas

**Decisão**: Calcular todas as métricas após a conclusão do backtest, em um único passo.

**Alternativas Consideradas**:
- Calcular incrementalmente durante o backtest
- Calcular sob demanda (lazy)

**Justificativa**:
- Simplicidade: Um único ponto de cálculo
- Performance: Operações vetorizadas são rápidas
- Manutenibilidade: Fácil debugar e testar

### 2. Benchmark (Buy & Hold)

**Decisão**: Calcular Buy & Hold usando os mesmos dados do backtest.

**Implementação**:
```python
def calculate_buy_and_hold(prices: pd.Series, initial_capital: float) -> dict:
    """
    Simula comprar no primeiro preço e vender no último.
    """
    entry_price = prices.iloc[0]
    exit_price = prices.iloc[-1]
    shares = initial_capital / entry_price
    final_value = shares * exit_price
    return_pct = (final_value - initial_capital) / initial_capital
    
    # Calcular CAGR
    days = (prices.index[-1] - prices.index[0]).days
    years = days / 365.25
    cagr = (final_value / initial_capital) ** (1 / years) - 1
    
    return {
        'return_pct': return_pct,
        'cagr': cagr,
        'final_value': final_value
    }
```

### 3. Critérios GO/NO-GO

**Decisão**: Critérios configuráveis via constantes, mas com defaults sensatos para crypto swing trading.

**Configuração**:
```python
# criteria.py
DEFAULT_CRITERIA = {
    'min_cagr_vs_bh': 0.0,  # Deve superar B&H
    'max_drawdown_pct': 35.0,
    'min_calmar_ratio': 1.0,
    'min_profit_factor': 1.3,
    'min_expectancy': 0.0,
    'min_trades': 100,
    'max_sharpe_threshold': 0.8,  # NO-GO se < 0.8
    'critical_drawdown': 45.0,  # NO-GO automático
}
```

**Lógica**:
```python
def evaluate_go_nogo(metrics: BacktestMetrics, criteria: dict = None) -> CriteriaResult:
    criteria = criteria or DEFAULT_CRITERIA
    reasons = []
    warnings = []
    
    # Verificações críticas (NO-GO)
    if metrics.max_drawdown > criteria['critical_drawdown']:
        reasons.append(f"Max Drawdown crítico: {metrics.max_drawdown:.1f}% > {criteria['critical_drawdown']}%")
    
    if metrics.sharpe_ratio < criteria['max_sharpe_threshold']:
        reasons.append(f"Sharpe muito baixo: {metrics.sharpe_ratio:.2f} < {criteria['max_sharpe_threshold']}")
    
    # Verificações de qualidade (GO)
    if metrics.cagr <= metrics.benchmark.buy_and_hold_cagr:
        reasons.append("CAGR não supera Buy & Hold")
    
    # ... mais verificações
    
    status = "GO" if len(reasons) == 0 else "NO-GO"
    return CriteriaResult(status=status, reasons=reasons, warnings=warnings)
```

### 4. Schemas

**Expansão de `BacktestMetrics`**:
```python
class BacktestMetrics(BaseModel):
    # Existentes
    total_return_pct: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    win_rate: float
    total_trades: int
    
    # Novos - Performance
    cagr: float
    monthly_return_avg: float
    
    # Novos - Risco
    avg_drawdown: float
    max_dd_duration_days: int
    recovery_factor: float
    
    # Novos - Risk-Adjusted
    sortino_ratio: float
    calmar_ratio: float
    
    # Novos - Trade Stats
    expectancy: float
    max_consecutive_wins: int
    max_consecutive_losses: int
    trade_concentration_top_10_pct: float
    
    # Novos - Costs
    total_fees_paid: float
    total_slippage: float
    net_return_pct: float
    
    # Benchmark
    benchmark: BenchmarkMetrics
    
    # Critérios
    criteria_result: CriteriaResult
```

## Padrões de Implementação

### Cálculo de Métricas

Todas as funções de cálculo seguem o padrão:

```python
def calculate_metric(
    equity_curve: pd.Series,
    trades: List[Trade],
    **kwargs
) -> float:
    """
    Calcula [nome da métrica].
    
    Args:
        equity_curve: Série temporal do valor da conta
        trades: Lista de trades executados
        **kwargs: Parâmetros adicionais
    
    Returns:
        Valor da métrica
        
    Raises:
        ValueError: Se dados insuficientes
    """
    # Validação
    if len(equity_curve) < 2:
        raise ValueError("Equity curve muito curta")
    
    # Cálculo
    result = ...
    
    return result
```

### Testes

Cada métrica tem testes com:
1. **Caso normal**: Dados realistas
2. **Casos extremos**: Todos ganhos, todas perdas, zero trades
3. **Validação matemática**: Comparação com cálculo manual

```python
def test_calculate_cagr():
    # Caso normal: 100% retorno em 1 ano = 100% CAGR
    equity = pd.Series([10000, 20000], index=pd.date_range('2023-01-01', periods=2, freq='365D'))
    cagr = calculate_cagr(equity)
    assert abs(cagr - 1.0) < 0.01
    
    # Caso 2 anos: 100% retorno em 2 anos ≈ 41.4% CAGR
    equity = pd.Series([10000, 20000], index=pd.date_range('2023-01-01', periods=2, freq='730D'))
    cagr = calculate_cagr(equity)
    assert abs(cagr - 0.414) < 0.01
```

## Integração com Sistema Existente

### Fluxo de Dados

```
1. Backtest executa → Gera equity_curve e trades
2. BacktestService chama MetricsCalculator
3. MetricsCalculator:
   a. Calcula métricas de performance
   b. Calcula métricas de risco
   c. Calcula risk-adjusted
   d. Calcula trade stats
   e. Calcula benchmark (B&H)
   f. Aplica critérios GO/NO-GO
4. Retorna BacktestMetrics completo
5. Frontend renderiza seções de métricas
```

### Suporte à Decisão do Usuário

**Problema**: Usuário tem múltiplas estratégias/configurações e precisa escolher a melhor.

**Solução**: Interface organizada que responde perguntas-chave:

#### 1. "Qual estratégia é mais lucrativa?"
- **Métrica**: CAGR (não apenas retorno total)
- **Visualização**: Ranking de estratégias por CAGR
- **Comparação**: CAGR vs Buy & Hold

#### 2. "Qual estratégia é mais segura?"
- **Métricas**: Max DD, Calmar Ratio
- **Visualização**: Gráfico de risco vs retorno
- **Alerta**: Destaque para estratégias com DD > 35%

#### 3. "Qual compensa melhor o risco?"
- **Métricas**: Sharpe, Sortino, Calmar
- **Visualização**: Tabela comparativa de ratios
- **Recomendação**: Destaque para Calmar ≥ 1.5 (excelente)

#### 4. "Qual é mais confiável?"
- **Métricas**: Profit Factor, Expectancy, Concentração
- **Visualização**: Distribuição de trades
- **Alerta**: Aviso se lucro concentrado em poucos trades

#### 5. "Vale a pena usar essa estratégia?"
- **Critério**: GO/NO-GO automatizado
- **Visualização**: Badge verde/vermelho no topo
- **Ação**: Botão "Usar em Produção" habilitado apenas se GO

### Layout da Página de Resultados

```
┌─────────────────────────────────────────────┐
│  ✓ ESTRATÉGIA APROVADA (GO)                 │ ← Badge destacado
│  Supera B&H | Risco aceitável | Confiável   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  📊 RESUMO EXECUTIVO                        │
│  ┌──────────┬──────────┬──────────┐         │
│  │ CAGR     │ Max DD   │ Calmar   │         │
│  │ 45%  ✓   │ 28%  ✓   │ 1.6  ✓   │         │
│  └──────────┴──────────┴──────────┘         │
└─────────────────────────────────────────────┘

▼ Performance (expandido por padrão)
  - Retorno Total, CAGR, Retorno Mensal
  - Comparação com Buy & Hold

▶ Risco (colapsado)
  - Max DD, DD Médio, Tempo em DD, Recovery

▶ Retorno Ajustado ao Risco (colapsado)
  - Sharpe, Sortino, Calmar

▶ Estatísticas de Trades (colapsado)
  - Win Rate, PF, Expectancy, Sequências

▶ Benchmark (colapsado)
  - Gráfico comparativo, Alpha, Correlação
```

### Compatibilidade

- Métricas existentes continuam funcionando
- Novas métricas são opcionais (podem ser None se dados insuficientes)
- Frontend degrada gracefully se métricas não disponíveis

## Considerações de Performance

### Otimizações

1. **Vetorização**: Usar NumPy para cálculos em arrays
2. **Caching**: Resultados intermediários (ex: drawdown series)
3. **Lazy Evaluation**: Calcular apenas métricas solicitadas (futuro)

### Benchmarks Esperados

- Cálculo completo de métricas: < 100ms para 10k candles
- Overhead total no backtest: < 5%

## Extensibilidade Futura

### Métricas Adicionais (v1.1)

Estrutura permite adicionar facilmente:
- Ulcer Index
- Information Ratio
- Omega Ratio
- Custom metrics definidas pelo usuário

### Configuração de Critérios

Futuro: Permitir usuário configurar seus próprios critérios GO/NO-GO via UI.

## Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Cálculos incorretos | Alto | Testes extensivos, validação manual |
| Performance degradada | Médio | Benchmarks, otimizações |
| UI confusa | Médio | UX testing, tooltips, documentação |
| Critérios muito rígidos | Baixo | Configuráveis, defaults conservadores |

## Decisões Pendentes

1. **Formato de Exportação**: CSV, JSON, ou ambos?
2. **Histórico de Métricas**: Salvar métricas de backtests anteriores para comparação?
3. **Alertas**: Email/notificação quando estratégia passa critérios GO?

Essas decisões podem ser tomadas durante a implementação com feedback do usuário.
