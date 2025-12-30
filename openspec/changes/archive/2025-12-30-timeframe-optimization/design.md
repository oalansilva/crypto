# Design: Timeframe Optimization

## Arquitetura

### Fluxo de Dados

```mermaid
graph TD
    A[User selects multiple timeframes] --> B[Frontend: SimpleBacktestWizard]
    B --> C[Payload: timeframe = ['1h', '4h', '1d']]
    C --> D[Backend: _run_single_strategy_optimization]
    D --> E{Timeframe is list?}
    E -->|Yes| F[Add to global_grid]
    E -->|No| G[Use single timeframe]
    F --> H[Generate combinations: TF × Params]
    G --> H
    H --> I[For each combination]
    I --> J[Fetch data for specific timeframe]
    J --> K[Run backtest]
    K --> L[Store result with timeframe in params]
    L --> M{More combinations?}
    M -->|Yes| I
    M -->|No| N[Return aggregated results]
    N --> O[Frontend: OptimizationResults]
    O --> P[Display table with Timeframe column]
```

---

## Componentes Afetados

### Backend

#### 1. `BacktestRunCreate` Schema
```python
# Before
timeframe: str

# After
timeframe: Union[str, List[str]]
```

**Validação**:
- Se lista: mínimo 1, máximo 6 timeframes
- Valores válidos: ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '3d', '1w', '1M']

#### 2. `BacktestService._run_single_strategy_optimization()`

**Mudanças**:
1. Detectar se `timeframe` é lista
2. Se sim, adicionar ao `global_grid`
3. Para cada combinação, extrair timeframe específico
4. Fetch data para esse timeframe
5. Incluir timeframe nos `params` do resultado

**Pseudo-código**:
```python
def _run_single_strategy_optimization(config, progress_callback=None, df=None):
    # Extract timeframe(s)
    timeframe_input = config.get('timeframe')
    timeframe_list = timeframe_input if isinstance(timeframe_input, list) else [timeframe_input]
    
    # Build global grid
    global_grid = {}
    if len(timeframe_list) > 1:
        global_grid['timeframe'] = timeframe_list
    
    # Add stop/take to global grid (existing logic)
    # ...
    
    # Build strategy grid (existing logic)
    # ...
    
    # Generate combinations
    all_keys = list(global_grid.keys()) + list(strat_grid.keys())
    all_values = list(global_grid.values()) + list(strat_grid.values())
    combinations = list(itertools.product(*all_values))
    
    # Cache for downloaded data
    data_cache = {}
    
    # Execute combinations
    for comb in combinations:
        # Map values to keys
        params_dict = dict(zip(all_keys, comb))
        
        # Extract timeframe for this combination
        current_tf = params_dict.get('timeframe', timeframe_list[0])
        
        # Fetch or retrieve cached data
        if current_tf not in data_cache:
            data_cache[current_tf] = self.loader.fetch_data(symbol, current_tf, since, until)
        
        df_current = data_cache[current_tf]
        
        # Run backtest with current timeframe data
        # ...
        
        # Store result with timeframe
        opt_results.append({
            'params': {**params_dict},  # Already includes 'timeframe'
            'metrics': {...}
        })
```

#### 3. Data Caching Strategy

**Problema**: Baixar dados para cada timeframe é custoso

**Solução**: Cache local durante execução
```python
data_cache = {}  # {timeframe: DataFrame}

for combination in combinations:
    tf = combination['timeframe']
    if tf not in data_cache:
        data_cache[tf] = self.loader.fetch_data(symbol, tf, since, until)
    df = data_cache[tf]
```

**Benefício**: Cada timeframe é baixado apenas uma vez por otimização

---

### Frontend

#### 1. `SimpleBacktestWizard.tsx`

**Estado atual**:
```tsx
const [selectedTimeframes, setSelectedTimeframes] = useState<string[]>(['1d'])
```

**Mudança no `handleSubmit`**:
```tsx
const config: BacktestRunCreate = {
    mode: 'optimize',
    // If single timeframe, send as string; if multiple, send as array
    timeframe: selectedTimeframes.length === 1 
        ? selectedTimeframes[0] 
        : selectedTimeframes,
    // ...
}
```

**UI Enhancement**: Mostrar contador de combinações
```tsx
const estimateCombinations = () => {
    let count = selectedTimeframes.length
    
    // Multiply by strategy param combinations
    selectedIndicators.forEach(ind => {
        const params = strategiesParams[ind] || {}
        let paramCombos = 1
        Object.values(params).forEach(val => {
            if (typeof val === 'object' && 'min' in val) {
                const steps = Math.floor((val.max - val.min) / val.step) + 1
                paramCombos *= steps
            }
        })
        count *= paramCombos
    })
    
    // Multiply by global params (stop/take)
    if (stopPct && typeof stopPct === 'object') {
        const steps = Math.floor((stopPct.max - stopPct.min) / stopPct.step) + 1
        count *= steps
    }
    
    return count
}

// Display warning if > 200
{estimateCombinations() > 200 && (
    <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
        <p className="text-sm text-yellow-400">
            ⚠️ {estimateCombinations()} combinações estimadas. 
            Considere reduzir ranges ou timeframes.
        </p>
    </div>
)}
```

#### 2. `OptimizationResults.tsx`

**Já implementado**: Coluna Timeframe ✅

**Enhancement opcional**: Filtro por timeframe
```tsx
const [selectedTF, setSelectedTF] = useState<string | null>(null)

const filteredResults = selectedTF 
    ? results.filter(r => r.params.timeframe === selectedTF)
    : results

// UI
<select onChange={(e) => setSelectedTF(e.target.value || null)}>
    <option value="">Todos os Timeframes</option>
    {uniqueTimeframes.map(tf => (
        <option key={tf} value={tf}>{tf}</option>
    ))}
</select>
```

---

## Estruturas de Dados

### Request Payload

```typescript
interface BacktestRunCreate {
    mode: 'optimize'
    symbol: string
    timeframe: string | string[]  // ← NEW: Can be array
    since: string
    until?: string
    strategies: Array<string | StrategyConfig>
    params?: Record<string, Record<string, any>>
    stop_pct?: number | RangeParam
    take_pct?: number | RangeParam
}
```

### Response Structure

```typescript
interface OptimizationResult {
    mode: 'optimize'
    dataset: {
        symbol: string
        timeframes_tested: string[]  // ← NEW
        since: string
        until: string
    }
    optimization_results: Array<{
        params: {
            timeframe: string  // ← NEW: Always present
            [key: string]: any
        }
        metrics: {
            total_pnl: number
            total_pnl_pct: number
            win_rate: number
            total_trades: number
        }
    }>
    best_result: {
        params: {
            timeframe: string
            [key: string]: any
        }
        metrics: {...}
    }
}
```

---

## Considerações de Performance

### Benchmark Estimado

**Cenário**: 
- Timeframes: 4 (1h, 4h, 1d, 3d)
- Parâmetros: 30 combinações
- Total: 120 combinações

**Tempo estimado**:
- Download de dados: 4 × 2s = 8s
- Backtest por combinação: 0.5s
- Total: 8s + (120 × 0.5s) = **68 segundos**

**Otimização**:
- Cache de dados: Reduz download para 8s total
- Truncar datasets: Já implementado (20k candles max)
- Paralelização futura: Possível com threading

---

## Validações

### Frontend
1. Mínimo 1 timeframe selecionado
2. Máximo 6 timeframes
3. Combinações totais ≤ 500
4. Warning se > 200 combinações

### Backend
1. Validar timeframe values (lista permitida)
2. Rejeitar se combinações > 500
3. Timeout de 5 minutos por otimização

---

## Testes

### Unit Tests

```python
def test_timeframe_optimization_single():
    config = {
        'timeframe': '1d',
        'strategies': [{'name': 'sma'}],
        'params': {'sma': {'length': {'min': 20, 'max': 30, 'step': 5}}}
    }
    result = service._run_single_strategy_optimization(config)
    assert all(r['params']['timeframe'] == '1d' for r in result['optimization_results'])

def test_timeframe_optimization_multiple():
    config = {
        'timeframe': ['1h', '4h', '1d'],
        'strategies': [{'name': 'sma'}],
        'params': {'sma': {'length': {'min': 20, 'max': 30, 'step': 10}}}
    }
    result = service._run_single_strategy_optimization(config)
    
    # Should have 3 timeframes × 2 lengths = 6 results
    assert len(result['optimization_results']) == 6
    
    # Check timeframes are present
    timeframes = {r['params']['timeframe'] for r in result['optimization_results']}
    assert timeframes == {'1h', '4h', '1d'}
```

### Integration Tests

1. **Test: 2 timeframes, 1 strategy**
   - Verify all combinations tested
   - Verify timeframe in results

2. **Test: 4 timeframes, 2 strategies (multi-strategy)**
   - Verify correct aggregation
   - Verify best overall includes timeframe

3. **Test: Performance with 100+ combinations**
   - Verify completion within timeout
   - Verify data caching works

---

## Rollout Plan

### Phase 1: Backend (Isolated)
- Implement timeframe as list support
- Add to global_grid
- Test with unit tests
- **No frontend changes yet**

### Phase 2: Frontend Integration
- Update wizard to send array
- Add combination counter
- Add warnings

### Phase 3: Results Enhancement
- Timeframe filter
- Visual grouping
- Performance charts

### Phase 4: Production
- Deploy backend
- Deploy frontend
- Monitor performance
- Gather user feedback

---

## Backward Compatibility

### Existing Behavior Preserved

**Single timeframe (string)**:
```json
{"timeframe": "1d"}
```
→ Works exactly as before

**Multiple timeframes (array)**:
```json
{"timeframe": ["1h", "4h"]}
```
→ New optimization behavior

### Migration Path

No migration needed - fully backward compatible.
