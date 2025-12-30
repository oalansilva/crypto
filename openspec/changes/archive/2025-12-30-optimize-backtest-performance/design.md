# Design OpenSpec: Otimização de Performance do Backtest

## 1. Mudanças na Arquitetura

### A. Modelo de Processamento Paralelo
O loop síncrono em `BacktestService._run_single_strategy_optimization` será substituído por um `ProcessPoolExecutor`.
Devido ao GIL do Python, threads são ineficazes para backtests intensivos em CPU. Processos são necessários.

**Desafios no Windows:**
*   `multiprocessing` cria novos processos sem `fork`. Cópia completa de memória ocorre.
*   Objetos passados para workers devem ser serializáveis (picklable).
*   Estado global não é compartilhado.

**Solução:**
1.  Extrair `evaluate_combination(config, combination, df)` como uma **função de nível superior** em um módulo separado (ex: `backend/app/workers/optimization.py`) para evitar problemas de pickle.
2.  Passar dados (`df`) de forma eficiente. Como `df` pode ser grande, podemos usar memória compartilhada ou simplesmente confiar em passá-lo uma vez por chunk se possível. Para a V1, passaremos como argumento.

### B. Estratégia de Cache de Sinais
Dentro do processo worker, implementaremos cache.
Como processos `multiprocessing` são persistentes no pool:
*   Usar `@functools.lru_cache` no método `generate_signals` ou uma variável local no módulo do worker.
*   Dividir a execução do Backtest em duas fases:
    1.  `prepare_data(df, strategy_params)` -> retorna `df_with_signals` (Em Cache)
    2.  `execute_backtest(df_with_signals, execution_params)` -> retorna `metrics` (Rápido)

### C. Otimização de Armazenamento
Em vez de acumular `opt_results = []` na memória:
1.  Criar um banco de dados SQLite dedicado `backend/data/jobs/{job_id}.db` ou um arquivo `.jsonl`.
2.  O processo principal coleta resultados dos futures e os grava no arquivo via stream.
3.  O checkpoint JSON final conterá apenas metadados e sumário, referenciando o arquivo de resultados externo.

## 2. Design de Componentes

### `backend/app/workers/optimization_worker.py`
Novo módulo contendo a lógica do worker.
```python
# Pseudo-código
def init_worker(shared_df):
    global _worker_df
    _worker_df = shared_df

def process_chunk(combinations):
    results = []
    for comb in combinations:
        # Verificar cache para sinais
        # Executar backtest
        results.append(metrics)
    return results
```

### Modificações em `BacktestService.py`
*   `JobManager` permanece como coordenador.
*   Inicializar `ProcessPoolExecutor`.
*   Agrupar combinações em chunks (ex: 100).
*   Submeter chunks ao executor.
*   Iterar `as_completed(futures)`.
*   Atualizar progresso e salvar resultados parciais.

## 3. Fluxo de Dados
1.  **Requisição**: Usuário inicia otimização.
2.  **JobManager**: Cria `job_id` adequado.
3.  **BacktestService**:
    *   Carrega dados.
    *   Gera 10.000 combinações.
    *   Divide em 100 chunks de 100.
    *   Inicia 8 workers (dependendo da CPU).
4.  **Workers**:
    *   Recebem chunk.
    *   Executam backtests.
    *   Retornam lista de 100 resultados.
5.  **Processo Principal**:
    *   Recebe 100 resultados.
    *   Anexa ao `results.jsonl`.
    *   Atualiza % de Progresso no DB.
    *   Verifica sinal de Pausa.

## 4. Riscos e Mitigações
*   **Uso de Memória**: Múltiplos processos com cópias de `df` podem causar OOM (Out Of Memory).
    *   *Mitigação*: Limitar `max_workers`. Truncar `df` se for massivo.
*   **Complexidade de Pausa/Retomada**: Pausar um pool é difícil.
    *   *Mitigação*: Verificamos pausa apenas *entre* chunks. Uma solicitação de pausa pode levar alguns segundos para reagir (até os chunks atuais terminarem). Isso é aceitável.
