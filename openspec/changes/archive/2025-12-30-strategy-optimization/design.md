# Design: Otimização de Estratégias

## Estruturas de Dados

### Requisição API (`BacktestRunCreate`)
Extensões para suportar faixas:
```python
# Em vez de float/int simples, permitir:
class RangeParam(BaseModel):
    min: float
    max: float
    step: float

# No dicionário params:
"params": {
    "length": {"min": 10, "max": 20, "step": 1},
    "stop_loss": {"min": 0.01, "max": 0.05, "step": 0.001}
}
```

### Resposta API (`BacktestResult`)
Estrutura para resultados de otimização:
```json
{
  "mode": "optimize",
  "optimization_results": [
    {
      "params": {"length": 10, "stop_loss": 0.01},
      "metrics": {"total_return": 0.15, "sharpe": 1.2, ...}
    },
    ...
  ],
  "best_result": { ... }
}
```

## Lógica Backend (`backtest_service.py`)

1. **Parser**: Detectar se `params` contém dicionários de faixas.
2. **Gerador**: Usar `itertools.product` para gerar todos os conjuntos de parâmetros concretos.
3. **Loop de Execução**:
    ```python
    results = []
    for params in combinations:
        # Executar lógica padrão de backtest
        metrics = run_backtester(df, strategy, params)
        results.append({params, metrics})
    ```
4. **Otimização**:
    - Pré-carregar Dataframe UMA VEZ (não baixar para cada execução).
    - Reutilizar o dataframe `df` para todas as iterações.
    - Isso será muito rápido já que a busca de dados é o gargalo.

## Frontend UI

### Componente `RangeInput`
Linha simples:
`[ Rótulo ] [ Entrada Mín ] [ Entrada Máx ] [ Entrada Passo ]`

### Componente `OptimizationVisualizer`
- Usar `recharts` ScatterChart (Gráfico de Dispersão).
- Eixo X: Parâmetro 1 (ex: Stop Loss).
- Eixo Y: Lucro Líquido.
- Eixo Z / Cor: Parâmetro 2 (se existir).

## Tarefas
Ver `tasks.md`.
