# Proposta OpenSpec: Interface Unificada de Backtest

**Recurso**: Otimização e Comparação Multi-Estratégia em Grid
**Status**: PROPOSTO
**Autor**: User Request
**Data**: 2025-12-29

## Objetivo
Criar uma interface unificada onde o usuário pode **otimizar e comparar múltiplas estratégias simultaneamente** em um grid visual, permitindo identificar rapidamente qual estratégia e quais parâmetros funcionam melhor para um determinado mercado e período.

## Motivação
O fluxo atual força o usuário a escolher entre:
1. **Backtest único**: Testar uma estratégia com parâmetros fixos
2. **Otimização**: Encontrar melhores parâmetros para UMA estratégia
3. **Comparação**: Comparar múltiplas estratégias com parâmetros fixos

**Problema**: Não é possível responder à pergunta mais importante:
> "Qual estratégia E quais parâmetros funcionam melhor para BTC/USDT nos últimos 90 dias?"

**Solução Proposta**: Interface unificada que permite:
- ✅ Selecionar múltiplas estratégias (SMA, RSI, MACD, etc.)
- ✅ Definir ranges de otimização para cada estratégia
- ✅ Executar grid search para todas simultaneamente
- ✅ Visualizar resultados em grid comparativo
- ✅ Identificar vencedores por estratégia e por parâmetros

## Experiência Proposta (Fluxo do Usuário)

### 1. Seleção de Estratégias (Multi-Select)

**Interface de Seleção**:
```
┌─────────────────────────────────────┐
│ Selecione Estratégias para Testar  │
├─────────────────────────────────────┤
│ [✓] SMA Crossover                   │
│ [✓] RSI Reversal                    │
│ [✓] MACD Trend                      │
│ [ ] Bollinger Bands                 │
│ [ ] Stochastic                      │
└─────────────────────────────────────┘
```

- Usuário seleciona **múltiplas estratégias** via checkboxes
- Cada estratégia selecionada aparece em uma aba/card abaixo

### 2. Configuração de Parâmetros por Estratégia

**Abas/Cards Expansíveis**:
```
┌─ SMA Crossover ──────────────────┐
│ Length:  [20] - [50]  Step: [5]  │ ← Range para otimização
│ Stop:    [1%] - [5%]  Step: [1%] │
└──────────────────────────────────┘

┌─ RSI Reversal ───────────────────┐
│ Length:  [14] (fixo)             │ ← Valor fixo (sem otimização)
│ Oversold: [20] - [35] Step: [5]  │
│ Overbought: [65] - [80] Step: [5]│
└──────────────────────────────────┘
```

**Comportamento**:
- Por padrão, todos os parâmetros são **ranges** (modo otimização)
- Usuário pode "fixar" um parâmetro clicando em "🔒 Fixar"
- Badge mostra: "🔍 SMA: 18 combinações | RSI: 12 combinações | Total: 30 execuções"

### 3. Execução em Batch

**Progresso em Tempo Real**:
```
Executando Grid Search Multi-Estratégia
━━━━━━━━━━━━━━━━━━━━━━━━ 15/30 (50%)

✓ SMA (Length=20, Stop=1%) - Retorno: 12.5%
✓ SMA (Length=20, Stop=2%) - Retorno: 15.3%
⏳ SMA (Length=25, Stop=1%) - Executando...
⏳ RSI (Length=14, Oversold=20) - Na fila...
```

### 4. Resultados em Grid Comparativo

**Visualização Principal: Grid de Estratégias**

```
┌──────────────────────────────────────────────────────────┐
│                  Comparação de Estratégias               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  🥇 SMA (L=25, S=2%)    17.04%  $1,704  ⭐⭐⭐⭐⭐      │
│  🥈 RSI (L=14, OS=25)   15.21%  $1,521  ⭐⭐⭐⭐        │
│  🥉 MACD (F=12, S=26)   12.38%  $1,238  ⭐⭐⭐          │
│                                                          │
│  [Ver Detalhes] [Executar Vencedor] [Exportar]          │
└──────────────────────────────────────────────────────────┘
```

**Drill-Down por Estratégia**:
- Clique em uma estratégia → Mostra gráfico de dispersão de SUAS combinações
- Tabela "Top 10 Combinações" específica daquela estratégia
- Gráfico de candles com trades da melhor combinação

**Comparação Visual**:
- Gráfico de barras: Retorno % por estratégia (melhor combinação de cada)
- Scatter plot: Retorno vs Risk para todas as combinações de todas as estratégias
- Heatmap: Parâmetro X vs Parâmetro Y colorido por retorno

### 5. Ações Rápidas

**Botões de Ação**:
1. **"Executar Vencedor"**: Roda backtest detalhado da melhor combinação
2. **"Comparar Top 3"**: Visualização lado a lado das 3 melhores
3. **"Exportar Grid"**: CSV com todas as combinações e resultados
4. **"Salvar Configuração"**: Salva setup para reutilizar

## Deltas de Especificação

### Frontend

#### Componentes Novos
1. **`StrategySelector`** - Seleção multi-estratégia
   - Checkboxes para cada estratégia disponível
   - Contador de estratégias selecionadas
   - Validação: mínimo 1, máximo 5 estratégias

2. **`StrategyConfigCard`** - Configuração por estratégia
   - Card expansível para cada estratégia selecionada
   - Campos de parâmetros com ranges por padrão
   - Toggle "🔒 Fixar" para converter range → valor único
   - Badge de combinações por estratégia

3. **`MultiStrategyBadge`** - Indicador global
   - Mostra total de combinações por estratégia
   - Total geral de execuções
   - Aviso se > 200 execuções totais

4. **`StrategyGridResults`** - Grid comparativo
   - Tabela com ranking de estratégias
   - Melhor combinação de cada estratégia
   - Drill-down para ver todas as combinações
   - Gráficos comparativos (barras, scatter, heatmap)

#### Componentes Modificados
1. **`SimpleBacktestWizard`**
   - Adiciona `StrategySelector` no topo
   - Renderiza `StrategyConfigCard` para cada estratégia selecionada
   - Remove seleção de modo (sempre otimização multi-estratégia)

2. **`ResultsPage`**
   - Renderiza `StrategyGridResults` como visualização principal
   - Drill-down para `OptimizationResults` de cada estratégia
   - Botões de ação: "Executar Vencedor", "Comparar Top 3", "Exportar"

### Backend

#### Schemas
```python
class StrategyConfig(BaseModel):
    """Configuração de uma estratégia para otimização"""
    name: str  # 'sma', 'rsi', 'macd', etc.
    params: Dict[str, ParameterValue]

class ParameterValue(BaseModel):
    """Valor de parâmetro - pode ser escalar ou range"""
    value: Optional[float] = None  # Valor fixo
    min: Optional[float] = None    # Range mínimo
    max: Optional[float] = None    # Range máximo  
    step: Optional[float] = None   # Passo do range
    
    @property
    def is_range(self) -> bool:
        return self.min is not None and self.max is not None

class MultiStrategyOptimizationRequest(BaseModel):
    """Request para otimização multi-estratégia"""
    market: MarketConfig
    strategies: List[StrategyConfig]  # Múltiplas estratégias
    global_params: Dict[str, ParameterValue]  # Stop/Take compartilhados
```

#### Lógica de Execução
```python
def run_multi_strategy_optimization(
    config: MultiStrategyOptimizationRequest
) -> MultiStrategyOptimizationResult:
    """
    Executa grid search para múltiplas estratégias
    Retorna resultados agregados e por estratégia
    """
    all_results = []
    
    for strategy_config in config.strategies:
        # Combina params globais + params da estratégia
        merged_params = {**config.global_params, **strategy_config.params}
        
        # Executa otimização para esta estratégia
        strategy_results = _run_optimization(
            strategy=strategy_config.name,
            params=merged_params,
            market=config.market
        )
        
        all_results.append({
            'strategy': strategy_config.name,
            'results': strategy_results,
            'best': max(strategy_results, key=lambda x: x['total_pnl'])
        })
    
    return MultiStrategyOptimizationResult(
        strategies=all_results,
        overall_best=max(all_results, key=lambda x: x['best']['total_pnl'])
    )
```

### Database
- Adicionar campo `strategies: List[str]` em `backtest_runs`
- Armazenar resultados por estratégia em `optimization_results`
- Novo índice: `(run_id, strategy_name)` para queries eficientes

## Benefícios

### Para o Usuário
✅ **Resposta completa**: Descobre qual estratégia E quais parâmetros funcionam melhor
✅ **Economia de tempo**: Testa múltiplas estratégias em uma única execução
✅ **Comparação visual**: Grid comparativo facilita identificação de vencedores
✅ **Flexibilidade**: Pode otimizar todas ou fixar parâmetros específicos
✅ **Descoberta**: Pode encontrar estratégias inesperadas que funcionam bem

### Para o Sistema
✅ **Execução eficiente**: Batch processing de múltiplas estratégias
✅ **Reutilização de dados**: Candles carregados uma vez para todas as estratégias
✅ **Escalabilidade**: Arquitetura preparada para paralelização futura
✅ **Insights ricos**: Dados agregados permitem análises mais profundas

## Riscos e Mitigação

### Risco 1: Complexidade da UI
- **Problema**: Muitos toggles podem confundir usuários iniciantes
- **Mitigação**: 
  - Tooltips explicativos em cada toggle
  - Tutorial interativo na primeira vez
  - Valores padrão sensatos (toggles OFF)

### Risco 2: Performance
- **Problema**: Usuário pode acidentalmente criar 1000+ combinações
- **Mitigação**:
  - Limite hard-coded de 200 combinações
  - Aviso visual quando > 50 combinações
  - Botão "Reduzir Passos" para ajustar automaticamente

### Risco 3: Compatibilidade
- **Problema**: Quebrar fluxos existentes
- **Mitigação**:
  - Manter endpoints atuais funcionando
  - Migração gradual (feature flag)
  - Testes de regressão

## Fases de Implementação

### Fase 1: Backend Multi-Estratégia (2-3 dias)
- [ ] Criar `StrategyConfig` e `MultiStrategyOptimizationRequest` schemas
- [ ] Implementar `run_multi_strategy_optimization()` 
- [ ] Atualizar database schema para suportar múltiplas estratégias
- [ ] Endpoint `/api/backtest/multi-optimize`
- [ ] Testes unitários e de integração

### Fase 2: Frontend - Seleção e Configuração (2-3 dias)
- [ ] Criar `StrategySelector` component
- [ ] Criar `StrategyConfigCard` component
- [ ] Criar `MultiStrategyBadge` component
- [ ] Atualizar `SimpleBacktestWizard` para multi-estratégia
- [ ] Testes de componentes

### Fase 3: Frontend - Resultados em Grid (2-3 dias)
- [ ] Criar `StrategyGridResults` component
  - [ ] Tabela de ranking
  - [ ] Gráfico de barras comparativo
  - [ ] Scatter plot multi-estratégia
  - [ ] Drill-down por estratégia
- [ ] Botões de ação rápida
- [ ] Testes E2E

### Fase 4: Polish e Otimizações (1-2 dias)
- [ ] Paralelização de execuções (se possível)
- [ ] Cache de resultados intermediários
- [ ] Export CSV/JSON multi-estratégia
- [ ] Documentação e tutoriais

## Critérios de Sucesso
- ✅ Usuário pode selecionar 2-5 estratégias simultaneamente
- ✅ Cada estratégia pode ter parâmetros independentes (ranges ou fixos)
- ✅ Grid comparativo mostra claramente qual estratégia venceu
- ✅ Drill-down funciona para ver detalhes de cada estratégia
- ✅ Performance aceitável para até 200 combinações totais
- ✅ Export funciona para todas as estratégias e combinações
