# Design — Card #70: [MT-2] Multi-tenant Data Isolation

## Arquitetura

### Princípio

Toda tabela que armazena dados de usuário deve ter uma foreign key `user_id` apontando para `users.id`. Toda query que retorna dados de usuário deve filtrar por `user_id` autenticado.

### user_id Extraction

O `user_id` é extraído do JWT no middleware de autenticação e injetado no request state:

```python
# Request state after auth middleware
request.state.user_id  # UUID do usuário logado
request.state.user_email  # Email do usuário logado
```

### Middleware/Dependency

Criar um dependency `get_current_user_id()` que:
1. Extrai o token do header `Authorization: Bearer <token>`
2. Valida e decodifica o JWT
3. Retorna o `user_id` do payload `sub`
4. Lança 401 se token ausente/inválido

```python
def get_current_user_id(request: Request) -> UUID:
    """Extrai user_id do JWT no request state."""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(401, "Unauthorized")
    return request.state.user_id
```

## Schema de Tabelas

### users (existente — sem alteração)
```
id          uuid (PK)
email       string (único)
password_hash string
name        string
created_at  timestamp
```

### signal_history (ALTERAR)
```
id              string (PK)
user_id         uuid (FK → users.id, indexado)
asset           string
type            string  # BUY, SELL, HOLD
confidence      integer
target_price    float
stop_loss       float
indicators      text (JSON, nullable)
created_at      timestamp
risk_profile    string
status          string  # ativo, disparado, expirado, cancelado
entry_price     float (nullable)
exit_price      float (nullable)
quantity        float (nullable)
pnl             float (nullable)
trigger_price   float (nullable)
updated_at      timestamp (nullable)
archived        string  # yes/no

INDEX: ix_signal_history_user_id ON (user_id)
```

### portfolio_snapshots (ALTERAR)
```
id              integer (PK, autoincrement)
user_id         uuid (FK → users.id, indexado)
recorded_at     timestamp
total_usd       float
btc_value       float
usdt_value      float
eth_value       float
other_usd       float
pnl_today_pct   float (nullable)
drawdown_30d_pct float (nullable)
drawdown_peak_date string (nullable)
btc_change_24h_pct float (nullable)

INDEX: ix_portfolio_snapshots_user_id ON (user_id)
```

### favorite_strategies (ALTERAR)
```
id              integer (PK, autoincrement)
user_id         uuid (FK → users.id, indexado)
name            string
symbol          string
timeframe       string
strategy_name   string
parameters      text (JSON)
metrics         text (JSON, nullable)
created_at      timestamp
notes           string (nullable)
tier            integer (nullable)
start_date      string (nullable)
end_date        string (nullable)
period_type     string (nullable)

INDEX: ix_favorite_strategies_user_id ON (user_id)
```

### monitor_preferences (ALTERAR)
```
user_id         uuid (PK, FK → users.id)
symbol          string (composite PK com user_id, ou remover symbol PK)
in_portfolio    boolean
card_mode       string
price_timeframe string
theme           string
updated_at      timestamp

ALTERAR: symbol VARCHAR remove, user_id vira PK
```

### backtest_runs (ALTERAR)
```
id              uuid (PK)
user_id         uuid (FK → users.id, indexado)
created_at      timestamp
status          string
mode            string
exchange        string
symbol          string
timeframe       string
since           string (nullable)
until           string (nullable)
full_period     boolean
strategies      text (JSON)
params          text (JSON, nullable)
fee             float
slippage        float
cash            float
stop_pct        text (JSON, nullable)
take_pct        text (JSON, nullable)
fill_mode       string
error_message   text (nullable)

INDEX: ix_backtest_runs_user_id ON (user_id)
```

### combo_templates (ALTERAR)
```
id              integer (PK, autoincrement)
user_id         uuid (FK → users.id, indexado)
name            string
description     string (nullable)
is_prebuilt     boolean
is_example      boolean
is_readonly     boolean
template_data   text (JSON)
optimization_schema text (JSON, nullable)
created_at      timestamp
updated_at      timestamp

INDEX: ix_combo_templates_user_id ON (user_id)
```

## Endpoints e Filtragem

### Sinais — `/api/signals`

| Método | Path | Alteração |
|--------|------|-----------|
| GET | /api/signals | Adicionar `WHERE user_id = :user_id` |
| POST | /api/signals | Adicionar `user_id` no INSERT |
| PATCH | /api/signals/{id} | Validar `user_id` do sinal = request.user_id |
| DELETE | /api/signals/{id} | Validar `user_id` do sinal = request.user_id |

### Portfolio — `/api/portfolio`

| Método | Path | Alteração |
|--------|------|-----------|
| GET | /api/portfolio | Filtrar `WHERE user_id = :user_id` |
| POST | /api/portfolio/snapshot | Adicionar `user_id` no INSERT |

### Favoritos — `/api/favorites`

| Método | Path | Alteração |
|--------|------|-----------|
| GET | /api/favorites | Filtrar `WHERE user_id = :user_id` |
| POST | /api/favorites | Adicionar `user_id` no INSERT |
| PATCH | /api/favorites/{id} | Validar ownership |
| DELETE | /api/favorites/{id} | Validar ownership |

### Monitor Preferences — `/api/monitor-preferences`

| Método | Path | Alteração |
|--------|------|-----------|
| GET | /api/monitor-preferences | Retornar prefs do `user_id` |
| PUT | /api/monitor-preferences | UPSERT com `user_id` |

### Backtest — `/api/backtest`

| Método | Path | Alteração |
|--------|------|-----------|
| GET | /api/backtest | Filtrar `WHERE user_id = :user_id` |
| POST | /api/backtest | Adicionar `user_id` no INSERT |

### Combo Templates — `/api/combo`

| Método | Path | Alteração |
|--------|------|-----------|
| GET | /api/combo/templates | Filtrar `WHERE user_id = :user_id` |
| POST | /api/combo/templates | Adicionar `user_id` no INSERT |
| PUT | /api/combo/templates/{id} | Validar ownership |
| DELETE | /api/combo/templates/{id} | Validar ownership |

## Validação de Ownership

Para operações de update/delete, validar que o recurso pertence ao usuário:

```python
def validate_ownership(db: Session, resource_user_id: UUID, request_user_id: UUID):
    if resource_user_id != request_user_id:
        raise HTTPException(403, "Forbidden: resource belongs to another user")
```

## Fluxo de Dados

### Criação de Recurso
```
Usuário (JWT) → POST /api/resource
              → Middleware extrai user_id do JWT
              → Route handler obtém user_id via get_current_user_id()
              → INSERT com user_id
              ← 201 {created resource}
```

### Busca de Recursos
```
Usuário (JWT) → GET /api/resources
              → Route handler obtém user_id via get_current_user_id()
              → SELECT WHERE user_id = :user_id
              ← 200 {list of user's resources}
```

### Acesso a Recurso Específico
```
Usuário (JWT) → GET /api/resources/{id}
              → Route handler obtém user_id via get_current_user_id()
              → SELECT WHERE id = :id AND user_id = :user_id
              → Se não encontrado: 404 (ou 403 se existe mas é de outro)
              ← 200 {resource}
```

## Índices

Todas as tabelas com `user_id` devem ter índice:

```sql
CREATE INDEX ix_<table>_user_id ON <table> (user_id);
```

Índices compostos quando aplicável:

```sql
-- signal_history
CREATE INDEX ix_signal_history_user_id ON signal_history (user_id);
CREATE INDEX ix_signal_history_user_id_created ON signal_history (user_id, created_at DESC);

-- portfolio_snapshots
CREATE INDEX ix_portfolio_snapshots_user_id ON portfolio_snapshots (user_id);
CREATE INDEX ix_portfolio_snapshots_user_id_recorded ON portfolio_snapshots (user_id, recorded_at DESC);

-- favorite_strategies
CREATE INDEX ix_favorite_strategies_user_id ON favorite_strategies (user_id);
```

## Migração de Schema

Usar SQLAlchemy migrations (se houver) ou ALTER TABLE direto:

```sql
-- signal_history
ALTER TABLE signal_history ADD COLUMN user_id VARCHAR(36);
CREATE INDEX ix_signal_history_user_id ON signal_history (user_id);

-- portfolio_snapshots
ALTER TABLE portfolio_snapshots ADD COLUMN user_id VARCHAR(36);
CREATE INDEX ix_portfolio_snapshots_user_id ON portfolio_snapshots (user_id);

-- favorite_strategies
ALTER TABLE favorite_strategies ADD COLUMN user_id VARCHAR(36);
CREATE INDEX ix_favorite_strategies_user_id ON favorite_strategies (user_id);

-- monitor_preferences (reestruturar PK)
-- Precisa recriar a tabela ou usar migration

-- backtest_runs
ALTER TABLE backtest_runs ADD COLUMN user_id VARCHAR(36);
CREATE INDEX ix_backtest_runs_user_id ON backtest_runs (user_id);

-- combo_templates
ALTER TABLE combo_templates ADD COLUMN user_id VARCHAR(36);
CREATE INDEX ix_combo_templates_user_id ON combo_templates (user_id);
```

## Stack

- SQLAlchemy ORM com SQLite
- FastAPI dependency injection para `user_id`
- UUID como user_id (vem do JWT `sub` claim)
- bcrypt + JWT (do Card #69)
