# Crypto Backtester - Backend API

Backend FastAPI para executar backtests de criptomoedas com persistência no Supabase.

## Banco de dados (SQLite)

O app usa **um único arquivo SQLite** como fonte de verdade: `backend/backtest.db` (definido em `app/database.py` como `DB_PATH`). Todas as migrations e o seed de templates usam esse mesmo caminho; não há mais uso de `backend/data/crypto_backtest.db`.

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
```

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

## 📡 Endpoints

### Health Check
```http
GET /api/health
```

### Presets (Playground)
```http
GET /api/presets
```

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
