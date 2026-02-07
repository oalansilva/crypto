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
O backend vai montar: `${LAB_TRACE_PUBLIC_URL}/{thread_id}`.

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
