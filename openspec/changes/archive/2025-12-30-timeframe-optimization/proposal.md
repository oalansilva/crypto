# OpenSpec: Timeframe Optimization

**Status**: Proposed  
**Created**: 2025-12-29  
**Author**: System

---

## Objetivo

Permitir que o **timeframe** seja tratado como um parâmetro otimizável na grid search, assim como stop loss, take profit e parâmetros de indicadores. Isso permite descobrir qual timeframe produz os melhores resultados para uma estratégia específica.

---

## Motivação

### Problema Atual
- Usuário precisa executar otimizações separadas para cada timeframe
- Não há forma de comparar resultados entre timeframes de forma unificada
- Processo manual e demorado para encontrar o timeframe ideal

### Solução Proposta
- Tratar timeframe como parâmetro otimizável
- Permitir seleção de múltiplos timeframes no wizard
- Sistema testa todas as combinações: estratégias × timeframes × parâmetros
- Resultados mostram qual timeframe performou melhor

---

## Experiência do Usuário

### Wizard de Configuração

**Antes:**
```
Timeframes: [1d] ← Seleção única ou múltipla (mas não otimizável)
```

**Depois:**
```
Timeframes para Otimização:
☑ 15m  ☑ 1h  ☑ 4h  ☑ 1d  ☐ 3d  ☐ 1w

💡 Sistema testará todas as combinações de timeframes selecionados
```

### Resultados

**Tabela "Top 10 Combinações":**
```
| Rank | Timeframe | Retorno % | Lucro $ | LENGTH | STOP % | Win Rate |
|------|-----------|-----------|---------|--------|--------|----------|
| #1   | 4h        | 5.23%     | $523.45 | 20     | 2.0%   | 65.2%    |
| #2   | 1d        | 4.87%     | $487.12 | 25     | 2.5%   | 62.1%    |
| #3   | 1h        | 3.45%     | $345.67 | 15     | 1.5%   | 58.3%    |
```

**Insight Visual:**
- Gráfico de barras: Retorno % por Timeframe
- Heatmap: Timeframe × Parâmetro → Retorno

---

## Especificação Técnica

### Backend Changes

#### 1. Schema Updates

**Arquivo**: `backend/app/schemas/backtest.py`

```python
class BacktestRunCreate(BaseModel):
    mode: Literal["run", "compare", "optimize"]
    exchange: str = "binance"
    symbol: str
    
    # NEW: timeframe can be single value or list for optimization
    timeframe: Union[str, List[str]]  # Single or multiple
    
    # DEPRECATED: timeframes field (kept for backward compatibility)
    timeframes: Optional[list[str]] = None
    
    since: str
    until: Optional[str] = None
    strategies: list[Union[str, dict]]
    params: Optional[dict] = None
    fee: float = 0.001
    slippage: float = 0.0005
    cash: float = 10000
    stop_pct: Optional[Union[float, RangeParam, dict]] = None
    take_pct: Optional[Union[float, RangeParam, dict]] = None
    fill_mode: Literal["close", "next_open"] = "close"
```

#### 2. Service Layer Logic

**Arquivo**: `backend/app/services/backtest_service.py`

```python
def _run_single_strategy_optimization(self, config: dict, progress_callback=None, df=None) -> dict:
    # ...existing code...
    
    # NEW: Expand timeframe if it's a list
    timeframe_list = []
    if isinstance(config.get('timeframe'), list):
        timeframe_list = config['timeframe']
    else:
        timeframe_list = [config['timeframe']]
    
    # NEW: Add timeframe to global grid
    if len(timeframe_list) > 1:
        global_grid['timeframe'] = timeframe_list
    
    # Generate parameter grid (existing logic)
    # ...
    
    # NEW: For each combination, fetch data for the specific timeframe
    for i, comb in enumerate(combinations):
        # Reconstruct params dict
        current_global = {}
        current_strat = {}
        
        for idx, key in enumerate(all_keys):
            val = comb[idx]
            if key in global_keys:
                current_global[key] = val
            else:
                current_strat[key] = val
        
        # NEW: Get timeframe for this combination
        current_timeframe = current_global.get('timeframe', config['timeframe'])
        
        # NEW: Fetch data for this specific timeframe
        if df is None or current_timeframe != config.get('_cached_timeframe'):
            df_current = self.loader.fetch_data(symbol, current_timeframe, since, until)
            if len(df_current) > 20000:
                df_current = df_current.tail(20000)
        else:
            df_current = df
        
        # Execute Backtest with current_timeframe data
        strategy = self._get_strategy(strategy_config, current_strat)
        signals = strategy.generate_signals(df_current)
        # ...rest of backtest logic...
        
        # Save result with timeframe in params
        opt_results.append({
            'params': {**current_global, **current_strat, 'timeframe': current_timeframe},
            'metrics': {...}
        })
```

#### 3. Response Structure

```json
{
  "mode": "optimize",
  "dataset": {
    "timeframes_tested": ["15m", "1h", "4h", "1d"],
    "symbol": "BTC/USDT",
    "since": "2024-01-01",
    "until": "2024-12-31"
  },
  "optimization_results": [
    {
      "params": {
        "timeframe": "4h",
        "length": 20,
        "stop_pct": 0.02
      },
      "metrics": {
        "total_pnl_pct": 0.0523,
        "win_rate": 0.652
      }
    }
  ],
  "best_result": {
    "params": {"timeframe": "4h", "length": 20, "stop_pct": 0.02},
    "metrics": {...}
  }
}
```

---

### Frontend Changes

#### 1. Wizard Update

**Arquivo**: `frontend/src/components/SimpleBacktestWizard.tsx`

```tsx
// Update timeframe selection to support optimization mode
const [selectedTimeframes, setSelectedTimeframes] = useState<string[]>(['1d'])

// In the UI, show hint when multiple timeframes selected
{selectedTimeframes.length > 1 && (
    <div className="mt-2 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
        <p className="text-xs text-blue-400">
            💡 {selectedTimeframes.length} timeframes selecionados. 
            Sistema testará todas as combinações.
        </p>
    </div>
)}

// In handleSubmit, pass timeframes as optimization parameter
const config: BacktestRunCreate = {
    mode: 'optimize',
    timeframe: selectedTimeframes.length === 1 ? selectedTimeframes[0] : selectedTimeframes,
    // ...rest of config
}
```

#### 2. Results Display

**Arquivo**: `frontend/src/components/results/OptimizationResults.tsx`

- Timeframe column already implemented ✅
- Add visual grouping by timeframe (optional enhancement)
- Add timeframe filter dropdown

---

## Estimativa de Combinações

### Exemplo 1: Single Strategy
- Timeframes: 4 (15m, 1h, 4h, 1d)
- LENGTH: 6 valores (20, 25, 30, 35, 40, 45)
- STOP: 5 valores (1%, 1.5%, 2%, 2.5%, 3%)

**Total**: 4 × 6 × 5 = **120 combinações**

### Exemplo 2: Multi-Strategy
- Estratégias: 3 (SMA, RSI, MACD)
- Timeframes: 4
- Parâmetros médios: 30 combinações por estratégia

**Total**: 3 × 4 × 30 = **360 combinações**

---

## Riscos e Mitigações

### 🚨 Risco: Explosão Combinatória
**Problema**: Muitos timeframes × muitos parâmetros = milhares de combinações  
**Mitigação**:
- Limite máximo: 500 combinações totais
- Warning no UI quando > 200 combinações
- Sugestão de reduzir ranges ou timeframes

### 🚨 Risco: Performance - Múltiplos Downloads
**Problema**: Cada timeframe requer download de dados  
**Mitigação**:
- Cache de dados por timeframe
- Download paralelo (se possível)
- Truncar datasets grandes (já implementado)

### 🚨 Risco: Comparação Injusta
**Problema**: Timeframes diferentes têm número diferente de candles  
**Mitigação**:
- Normalizar período de teste (mesmo range de datas)
- Mostrar número de trades e candles por resultado
- Documentar que comparação é relativa

---

## Implementação Faseada

### Fase 1: Backend Core (2-3h)
- [x] Atualizar schema para aceitar `timeframe: Union[str, List[str]]`
- [ ] Modificar `_run_single_strategy_optimization()` para iterar timeframes
- [ ] Adicionar timeframe ao grid de parâmetros
- [ ] Incluir timeframe nos resultados (`params.timeframe`)

### Fase 2: Frontend Integration (1-2h)
- [ ] Atualizar wizard para enviar lista de timeframes
- [ ] Adicionar hint visual de combinações
- [ ] Validação: máximo 500 combinações

### Fase 3: Results Enhancement (1h)
- [ ] Filtro por timeframe nos resultados
- [ ] Gráfico de barras: Retorno por Timeframe
- [ ] Agrupamento visual por timeframe (opcional)

### Fase 4: Testing & Polish (1h)
- [ ] Testar com 2 timeframes
- [ ] Testar com 4 timeframes
- [ ] Verificar performance
- [ ] Documentação

**Tempo Total Estimado**: 5-7 horas

---

## Benefícios

✅ **Descoberta Automática**: Sistema encontra o timeframe ideal  
✅ **Economia de Tempo**: Uma execução vs múltiplas manuais  
✅ **Comparação Justa**: Todos os timeframes testados nas mesmas condições  
✅ **Insights Visuais**: Gráficos mostram performance por timeframe  
✅ **Flexibilidade**: Funciona com single e multi-strategy  

---

## Exemplo de Uso

```python
# Configuração
{
  "mode": "optimize",
  "symbol": "BTC/USDT",
  "timeframe": ["1h", "4h", "1d"],  # ← Múltiplos timeframes
  "strategies": [{"name": "sma"}],
  "params": {
    "sma": {
      "length": {"min": 20, "max": 30, "step": 5}
    }
  },
  "stop_pct": {"min": 0.01, "max": 0.03, "step": 0.01}
}

# Resultado
Best: Timeframe=4h, LENGTH=25, STOP=2% → +5.23% retorno
```

---

## Decisões de Design

1. **Timeframe no global_grid**: Tratado como parâmetro global (como stop/take)
2. **Download por demanda**: Dados baixados apenas quando necessário
3. **Backward compatibility**: Campo `timeframes` mantido para compatibilidade
4. **UI hint**: Mostrar número de combinações antes de executar
5. **Limite hard**: 500 combinações máximo para evitar timeouts

---

## Próximos Passos

1. ✅ Criar este OpenSpec
2. ⏳ Revisar e aprovar proposta
3. ⏳ Implementar Fase 1 (Backend)
4. ⏳ Implementar Fase 2 (Frontend)
5. ⏳ Testar e validar
6. ⏳ Deploy e documentação
