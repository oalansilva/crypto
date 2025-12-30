# Proposta OpenSpec: Streaming Storage para Jobs de Otimização

**Status**: PROPOSTO  
**Autor**: Antigravity AI  
**Criado**: 2025-12-29

## 1. Descrição do Problema

### Problema Atual
O `JobManager` salva **todos os resultados** de otimização em um único arquivo JSON monolítico:

```json
{
  "job_id": "abc-123",
  "status": "RUNNING",
  "results": [
    {"params": {...}, "metrics": {...}},  // Resultado 1
    {"params": {...}, "metrics": {...}},  // Resultado 2
    ...
    {"params": {...}, "metrics": {...}}   // Resultado 3157
  ]
}
```

**Consequências:**
- ❌ Arquivos crescem para **200KB+** em otimizações grandes
- ❌ **Race Condition**: Frontend lê enquanto backend escreve → corrupção de JSON
- ❌ **Timeout/500 Error**: Endpoint `/api/backtest/jobs` trava ao ler arquivos gigantes
- ❌ **Alto uso de memória**: Carregar 3000+ resultados na RAM
- ❌ **Sem paginação**: Frontend recebe tudo de uma vez

### Evidências
- Arquivo `job_da378303...json`: **199.4 KB** (movido para quarentena)
- Arquivo `job_fd652217...json`: **60.46 KB** (movido para quarentena)
- Logs mostram: `"Extra data: line 32366"` (JSON corrompido)

## 2. Objetivo

Implementar **Streaming Storage** usando SQLite para armazenar resultados de otimização separadamente do estado do job.

**Metas:**
- ✅ Arquivos de estado pequenos (<5KB)
- ✅ Leitura/escrita rápida
- ✅ Sem corrupção (transações ACID)
- ✅ Paginação nativa
- ✅ Suporte a milhões de resultados

## 3. Escopo

### In-Scope
- `JobManager`: Refatorar para usar SQLite
- `BacktestService`: Salvar resultados via JobManager
- API: Endpoint paginado `/api/backtest/jobs/{id}/results?page=1&limit=50`
- Frontend: Atualizar para buscar resultados paginados

### Out-of-Scope
- Migração de jobs antigos (manter compatibilidade read-only)
- Otimização de queries SQLite (usar índices básicos apenas)

## 4. Solução Proposta

### Arquitetura

```
┌─────────────────────────────────────────┐
│ Job Metadata (JSON - Pequeno)           │
│ data/jobs/job_abc123.json               │
│ {                                       │
│   "job_id": "abc123",                   │
│   "status": "RUNNING",                  │
│   "progress": {"current": 1500, ...}    │
│ }                                       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Results Database (SQLite)               │
│ data/jobs/results.db                    │
│                                         │
│ Table: optimization_results             │
│ ┌──────────┬─────────┬────────┬───────┐│
│ │ job_id   │ idx     │ params │metrics││
│ ├──────────┼─────────┼────────┼───────┤│
│ │ abc123   │ 0       │ {...}  │ {...} ││
│ │ abc123   │ 1       │ {...}  │ {...} ││
│ │ abc123   │ 2       │ {...}  │ {...} ││
│ └──────────┴─────────┴────────┴───────┘│
└─────────────────────────────────────────┘
```

### Schema SQLite

```sql
CREATE TABLE optimization_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    result_index INTEGER NOT NULL,
    params_json TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, result_index)
);

CREATE INDEX idx_job_id ON optimization_results(job_id);
CREATE INDEX idx_job_created ON optimization_results(job_id, created_at);
```

## 5. Benefícios

| Métrica | Antes | Depois |
|---------|-------|--------|
| Tamanho arquivo estado | 200KB | <5KB |
| Tempo leitura `/jobs` | 2-5s (timeout) | <100ms |
| Uso memória | 200MB+ | <10MB |
| Corrupção de dados | Frequente | Zero (ACID) |
| Paginação | Não | Sim (50/página) |

## 6. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| SQLite lock contention | Baixa | Médio | WAL mode + timeout |
| Migração de dados antigos | Alta | Baixo | Manter compatibilidade read-only |
| Performance em milhões de rows | Baixa | Médio | Índices + LIMIT queries |

## 7. Critérios de Sucesso

- [ ] Otimização com 10k combinações completa sem erro 500
- [ ] Endpoint `/api/backtest/jobs` responde em <200ms
- [ ] Frontend carrega histórico sem travar
- [ ] Pause/Resume funciona corretamente
- [ ] Zero corrupção de dados após 100 otimizações
