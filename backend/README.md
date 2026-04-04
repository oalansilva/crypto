# Crypto Backtester - Backend API

Backend FastAPI para executar backtests de criptomoedas com persistência no Supabase.

## Banco de dados (PostgreSQL)

O backend agora exige PostgreSQL para o banco principal e para o workflow registry. O projeto `crypto` e o projeto `kanban` também devem ter bancos de workflow próprios em PostgreSQL.

## 📋 Pré-requisitos

- Python 3.11+
- Conta no Supabase (gratuita)
- Dependências do projeto principal já instaladas

## 🚀 Setup

### 1. Criar Projeto no Supabase

1. Acesse [supabase.com](https://supabase.com) e crie uma conta
2. Crie um novo projeto
3. Anote a **URL** e a **Service Role Key** (Settings > API)

### 2. Aplicar Schema SQL

No Supabase Dashboard:
1. Vá em **SQL Editor**
2. Copie o conteúdo de `backend/supabase_schema.sql`
3. Execute o SQL

Isso criará as tabelas:
- `backtest_runs` - Histórico de execuções
- `backtest_results` - Resultados detalhados

### 3. Configurar Variáveis de Ambiente

```bash
cd backend
cp .env.example .env
```

Edite `.env` e preencha:
```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua-service-role-key-aqui
DATABASE_URL=postgresql+psycopg2://crypto_app:senha@127.0.0.1:5432/crypto_app
WORKFLOW_DB_ENABLED=1
WORKFLOW_DATABASE_URL=postgresql+psycopg2://workflow_registry:senha@127.0.0.1:5432/workflow_registry
CRYPTO_DATABASE_URL=postgresql+psycopg2://crypto_app:senha@127.0.0.1:5432/crypto_app
CRYPTO_WORKFLOW_DATABASE_URL=postgresql+psycopg2://workflow_crypto:senha@127.0.0.1:5432/workflow_crypto
```

Para migrar dados legados de SQLite e do workflow compartilhado:
```bash
./.venv/bin/python backend/scripts/migrate_projects_to_postgres.py
```

O projeto Kanban foi separado para [kanban/](/root/.openclaw/workspace/kanban) e não sobe a partir deste backend.

⚠️ **IMPORTANTE**: Nunca commite o arquivo `.env` com suas credenciais!

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 5. Rodar o Servidor

```bash
# Modo desenvolvimento (auto-reload)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ou usando o script direto
python app/main.py
```

Servidor rodando em: http://localhost:8000

Documentação interativa: http://localhost:8000/docs

## Strategy Lab — Tracing/Studio (dev)

O Strategy Lab expõe runs em `POST /api/lab/run` e `GET /api/lab/runs/{run_id}`.

Para habilitar metadados de tracing (dev-only):
- Envie `debug_trace=true` no `POST /api/lab/run`.
- O `GET /api/lab/runs/{run_id}` retorna um objeto `trace` com:
  - `enabled`, `provider`, `thread_id`, `trace_id`
  - `trace_url` (opcional)

Para que o backend gere um link clicável (`trace_url`), configure uma destas env vars:
- `LAB_TRACE_PUBLIC_URL` (preferido)
- `TRACE_PUBLIC_URL`

Exemplo:
```bash
export LAB_TRACE_PUBLIC_URL="http://localhost:2024"
```
O backend monta: `${LAB_TRACE_PUBLIC_URL}/{thread_id}`.

## 📡 Endpoints

### Health Check
```http
GET /api/health
```

### Presets (Playground)
```http
GET /api/presets
```

### Combo Backtest (`ccxt` default, `stooq` for US stocks EOD)
```http
POST /api/combos/backtest
Content-Type: application/json

{
  "template_name": "multi_ma_crossover",
  "symbol": "AAPL",
  "timeframe": "1d",
  "data_source": "stooq",
  "start_date": "2024-01-01",
  "end_date": "2025-12-31",
  "parameters": {}
}
```

Notas:
- `data_source` é opcional. Sem ele, o backend mantém o caminho crypto existente (`ccxt`).
- `data_source=stooq` aceita apenas `timeframe=1d` (EOD).
- O campo `parameters` da resposta inclui `data_source`; ao salvar em favoritos, o monitor reutiliza essa origem.

### Executar Backtest (Single)
```http
POST /api/backtest/run
Content-Type: application/json

{
  "mode": "run",
  "symbol": "BTC/USDT",
  "timeframe": "4h",
  "since": "2023-01-01 00:00:00",
  "strategies": ["sma_cross"],
  "params": {
    "sma_cross": {"fast": 20, "slow": 50}
  }
}
```

### Comparar Estratégias
```http
POST /api/backtest/compare
Content-Type: application/json

{
  "mode": "compare",
  "symbol": "BTC/USDT",
  "timeframe": "4h",
  "since": "2023-01-01 00:00:00",
  "strategies": ["sma_cross", "rsi_reversal", "bb_meanrev"],
  "cash": 10000,
  "stop_pct": 0.03,
  "take_pct": 0.06
}
```

### Verificar Status (Polling)
```http
GET /api/backtest/status/{run_id}
```

### Obter Resultado
```http
GET /api/backtest/result/{run_id}
```

### Listar Histórico
```http
GET /api/backtest/runs?limit=50&offset=0
```

### Deletar Run
```http
DELETE /api/backtest/runs/{run_id}
```

## 🔄 Fluxo de Execução

1. **POST** `/api/backtest/compare` → Retorna `run_id` imediatamente
2. Backend cria registro com `status=PENDING`
3. Job em background inicia (`status=RUNNING`)
4. **Poll** `/api/backtest/status/{run_id}` até `status=DONE`
5. **GET** `/api/backtest/result/{run_id}` para obter resultado completo

## 📦 Estrutura do Resultado

```json
{
  "run_id": "uuid",
  "mode": "compare",
  "dataset": {
    "exchange": "binance",
    "symbol": "BTC/USDT",
    "timeframe": "4h",
    "candle_count": 6555
  },
  "candles": [
    {"timestamp_utc": "...", "open": 16617, "high": 16799, ...}
  ],
  "results": {
    "sma_cross": {
      "metrics": {
        "total_return_pct": 0.142,
        "max_drawdown_pct": -0.076,
        "sharpe": 0.014,
        "num_trades": 72,
        "win_rate": 0.388
      },
      "trades": [...],
      "equity": [...],
      "markers": [...]
    }
  },
  "benchmark": {
    "return_pct": 0.52,
    "equity": [...]
  }
}
```

## 🛠️ Desenvolvimento

### Estrutura de Pastas
```
backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── api.py            # Endpoints
│   ├── config.py         # Settings
│   ├── supabase_client.py
│   ├── schemas/          # Pydantic models
│   ├── services/         # Business logic
│   │   ├── backtest_service.py
│   │   ├── preset_service.py
│   │   └── run_repository.py
│   └── workers/          # Background jobs
│       └── runner.py
├── supabase_schema.sql
├── requirements.txt
└── .env.example
```

### Adicionar Nova Estratégia

1. Implemente a estratégia em `src/strategy/`
2. Registre em `backtest_service.py`:
```python
STRATEGY_MAP = {
    'sma_cross': SMACrossStrategy,
    'rsi_reversal': RSIReversalStrategy,
    'bb_meanrev': BBMeanReversionStrategy,
    'nova_estrategia': NovaEstrategia  # Adicione aqui
}
```

## 🔒 Segurança

- ✅ Service Role Key **APENAS** no backend
- ✅ CORS configurado para localhost (dev)
- ✅ Validação de inputs via Pydantic
- ✅ Limite de 20k candles por request

Para produção:
- Configure CORS para seu domínio
- Use HTTPS
- Adicione rate limiting
- Considere implementar autenticação

## 🐛 Troubleshooting

**Erro: "No module named 'src'"**
- Certifique-se de rodar o backend a partir da raiz do projeto

**Erro: "Connection refused" no Supabase**
- Verifique se `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` estão corretos
- Confirme que o SQL foi executado

**Backtest fica em PENDING**
- Verifique logs do servidor
- Confirme que o background worker está rodando

## 📝 Próximos Passos

- [ ] Frontend React (Fase 2)
- [ ] Testes automatizados
- [ ] Deploy (Railway, Render, etc.)
- [ ] Autenticação (Supabase Auth + RLS)
