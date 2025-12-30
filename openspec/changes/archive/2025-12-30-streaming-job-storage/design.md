# Design: Streaming Storage para Jobs de Otimização

## 1. Visão Geral

Substituir o armazenamento monolítico de resultados em JSON por um sistema híbrido:
- **Metadados do Job**: JSON pequeno (<5KB)
- **Resultados**: SQLite database com paginação

## 2. Arquitetura de Dados

### 2.1. Estrutura de Arquivos

```
backend/data/jobs/
├── job_abc123.json          # Metadados (5KB)
├── job_def456.json          # Metadados (5KB)
├── results.db               # SQLite database (todos os resultados)
└── *.corrupted              # Arquivos antigos corrompidos
```

### 2.2. Schema SQLite

```sql
-- Tabela principal de resultados
CREATE TABLE optimization_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    result_index INTEGER NOT NULL,
    params_json TEXT NOT NULL,      -- JSON serializado
    metrics_json TEXT NOT NULL,     -- JSON serializado
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_job_id ON optimization_results(job_id);
CREATE INDEX idx_job_created ON optimization_results(job_id, created_at DESC);
CREATE UNIQUE INDEX idx_job_result ON optimization_results(job_id, result_index);

-- Tabela de metadados de jobs (opcional, para queries rápidas)
CREATE TABLE job_metadata (
    job_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    total_combinations INTEGER,
    completed_combinations INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 2.3. Formato JSON de Metadados

```json
{
  "job_id": "abc-123",
  "status": "RUNNING",
  "created_at": "2025-12-29T18:00:00",
  "updated_at": "2025-12-29T18:10:00",
  "config": {
    "mode": "optimize",
    "strategies": ["rsi"],
    "timeframe": ["1h", "4h"],
    "params": {...}
  },
  "progress": {
    "current": 1500,
    "total": 3157,
    "percentage": 47.5
  },
  "best_result": {
    "params": {...},
    "metrics": {...}
  }
}
```

**Nota**: Campo `results` removido! Agora está no SQLite.

## 3. Componentes Afetados

### 3.1. `JobManager` (Refatoração Completa)

#### Novos Métodos

```python
class JobManager:
    def __init__(self):
        self.DATA_DIR = Path("data/jobs")
        self.db_path = self.DATA_DIR / "results.db"
        self._init_database()
    
    def _init_database(self):
        """Inicializa SQLite database com schema"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""CREATE TABLE IF NOT EXISTS ...""")
        conn.close()
    
    def save_result(self, job_id: str, result: Dict, index: int):
        """Salva um único resultado no SQLite"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO optimization_results 
            (job_id, result_index, params_json, metrics_json)
            VALUES (?, ?, ?, ?)
        """, (job_id, index, json.dumps(result['params']), 
              json.dumps(result['metrics'])))
        conn.commit()
        conn.close()
    
    def get_results(self, job_id: str, page: int = 1, limit: int = 50) -> Dict:
        """Busca resultados paginados"""
        offset = (page - 1) * limit
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT params_json, metrics_json 
            FROM optimization_results
            WHERE job_id = ?
            ORDER BY result_index
            LIMIT ? OFFSET ?
        """, (job_id, limit, offset))
        
        results = []
        for row in cursor:
            results.append({
                'params': json.loads(row[0]),
                'metrics': json.loads(row[1])
            })
        
        # Count total
        total = conn.execute(
            "SELECT COUNT(*) FROM optimization_results WHERE job_id = ?",
            (job_id,)
        ).fetchone()[0]
        
        conn.close()
        return {
            'results': results,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }
```

### 3.2. `BacktestService` (Mudança Mínima)

```python
# ANTES
self.job_manager.save_state(job_id, {
    'results': opt_results,  # Lista gigante
    'status': 'RUNNING'
})

# DEPOIS
# Salvar resultado individual
self.job_manager.save_result(job_id, result, index=i)

# Salvar apenas metadados
self.job_manager.save_state(job_id, {
    'status': 'RUNNING',
    'progress': {'current': i, 'total': total}
})
```

### 3.3. API Endpoints (Novos)

```python
@router.get("/backtest/jobs/{job_id}/results")
async def get_job_results(
    job_id: UUID,
    page: int = 1,
    limit: int = 50
):
    """Get paginated results for a job"""
    job_manager = JobManager()
    return job_manager.get_results(str(job_id), page, limit)
```

### 3.4. Frontend (Mudança Mínima)

```typescript
// ANTES
const response = await fetch(`/api/backtest/jobs/${jobId}`)
const job = await response.json()
const results = job.results // Tudo de uma vez

// DEPOIS
const response = await fetch(`/api/backtest/jobs/${jobId}/results?page=1&limit=50`)
const data = await response.json()
const results = data.results
const pagination = data.pagination
```

## 4. Fluxo de Dados

### 4.1. Durante Otimização

```
BacktestService
    ↓ (a cada iteração)
JobManager.save_result(job_id, result, index)
    ↓
SQLite INSERT
    ↓ (a cada 50 iterações)
JobManager.save_state(job_id, metadata)
    ↓
JSON file write (5KB)
```

### 4.2. Listagem de Jobs

```
Frontend → GET /api/backtest/jobs
    ↓
JobManager.list_jobs()
    ↓
Read JSON files (rápido, <5KB cada)
    ↓
Return [{job_id, status, progress}, ...]
```

### 4.3. Visualização de Resultados

```
Frontend → GET /api/backtest/jobs/{id}/results?page=1
    ↓
JobManager.get_results(job_id, page=1, limit=50)
    ↓
SQLite SELECT com LIMIT/OFFSET
    ↓
Return {results: [...], pagination: {...}}
```

## 5. Migração de Dados Antigos

### Estratégia: Read-Only Compatibility

```python
def get_results(self, job_id: str, page: int = 1, limit: int = 50):
    # Tentar SQLite primeiro
    results = self._get_from_sqlite(job_id, page, limit)
    if results:
        return results
    
    # Fallback: Ler do JSON antigo (se existir)
    state = self.load_state(job_id)
    if state and 'results' in state:
        # Paginar manualmente
        all_results = state['results']
        start = (page - 1) * limit
        end = start + limit
        return {
            'results': all_results[start:end],
            'pagination': {...}
        }
    
    return {'results': [], 'pagination': {...}}
```

## 6. Performance

### Benchmarks Esperados

| Operação | Antes | Depois |
|----------|-------|--------|
| Salvar 1 resultado | 50ms (rewrite JSON) | 1ms (INSERT) |
| Listar jobs | 2-5s (read 200KB) | 50ms (read 5KB) |
| Buscar 50 resultados | N/A | 10ms (SELECT) |
| Uso de memória | 200MB+ | <10MB |

### Otimizações SQLite

```python
# Ativar WAL mode para melhor concorrência
conn.execute("PRAGMA journal_mode=WAL")

# Aumentar cache
conn.execute("PRAGMA cache_size=10000")

# Batch inserts
conn.executemany("""INSERT INTO ...""", batch_data)
conn.commit()
```

## 7. Testes

### 7.1. Testes Unitários

```python
def test_save_and_retrieve_results():
    jm = JobManager()
    jm.save_result("job1", {"params": {...}, "metrics": {...}}, 0)
    results = jm.get_results("job1", page=1, limit=10)
    assert len(results['results']) == 1

def test_pagination():
    # Salvar 100 resultados
    for i in range(100):
        jm.save_result("job1", {...}, i)
    
    # Buscar página 2
    page2 = jm.get_results("job1", page=2, limit=50)
    assert len(page2['results']) == 50
    assert page2['pagination']['total'] == 100
```

### 7.2. Testes de Integração

- Otimização com 1000 combinações
- Pause/Resume durante otimização
- Consulta de resultados durante execução
- Verificar zero corrupção após 100 otimizações

## 8. Rollback Plan

Se houver problemas críticos:

1. Reverter código do `JobManager`
2. Manter `results.db` (não deletar)
3. Frontend continua funcionando com JSON antigo
4. Investigar e corrigir
5. Re-deploy quando estável
