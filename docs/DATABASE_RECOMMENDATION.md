# Recomendação de Banco de Dados - Crypto Ant

## 🎯 Recomendação Principal: **PostgreSQL (Neon ou Supabase)**

### Por que PostgreSQL?

#### ✅ **Vantagens para seu projeto:**

1. **JSONB Nativo** - Perfeito para seus dados
   - Seus modelos usam muito JSON (`template_data`, `metrics`, `result_json`)
   - PostgreSQL tem suporte nativo a JSONB com índices GIN
   - Queries eficientes em campos JSON
   - Validação de schema JSON opcional

2. **Performance com Dados Históricos**
   - Backtests geram muitos dados históricos
   - PostgreSQL escala bem com grandes volumes
   - Particionamento de tabelas para dados antigos
   - Índices eficientes para queries complexas

3. **Recursos Avançados**
   - Full-text search (útil para buscar estratégias)
   - Window functions (análises de métricas)
   - CTEs e queries complexas
   - Suporte a arrays e tipos customizados

4. **Compatibilidade com SQLAlchemy**
   - Seu código já usa SQLAlchemy
   - Migração simples (já tem suporte no código)
   - Tipos nativos (UUID, JSONB, TIMESTAMPTZ)

### Opções de Hosting

#### 🥇 **Neon (Recomendado)**
- **Serverless PostgreSQL** - escala automaticamente
- **Branching** - ambientes de dev/staging isolados
- **Scale-to-zero** - paga apenas pelo uso
- **Backup automático** - point-in-time recovery
- **Free tier generoso** - 0.5GB storage, 1 projeto
- **Ideal para**: Desenvolvimento e produção

**Setup:**
```bash
# 1. Criar conta em neon.tech
# 2. Criar projeto
# 3. Copiar connection string
# 4. Adicionar ao .env:
DATABASE_URL=postgresql://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require
```

#### 🥈 **Supabase**
- **PostgreSQL gerenciado** + extras
- **Auth integrado** (se precisar no futuro)
- **Real-time subscriptions** (útil para monitoramento)
- **Storage** para arquivos grandes
- **Dashboard visual** para gerenciar dados
- **Ideal para**: Quando precisar de features extras além do DB

**Setup:**
```bash
# 1. Criar projeto em supabase.com
# 2. Settings > Database > Connection string
# 3. Adicionar ao .env:
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres
```

#### 🥉 **PostgreSQL Self-hosted**
- **Controle total** sobre configuração
- **Custo fixo** (VPS/Droplet)
- **Ideal para**: Quando você tem expertise em DevOps

**Opções:**
- DigitalOcean Managed Database ($15/mês)
- AWS RDS PostgreSQL
- Railway.app ($5/mês)
- Render.com ($7/mês)

---

## 📊 Comparação Detalhada

| Característica | SQLite (Atual) | PostgreSQL (Neon) | Supabase |
|----------------|----------------|-------------------|----------|
| **JSON Support** | Text (sem índices) | JSONB (com índices) | JSONB (com índices) |
| **Concorrência** | Single writer | Multi-writer | Multi-writer |
| **Escalabilidade** | Limitada | Excelente | Excelente |
| **Queries Complexas** | Limitadas | Completas | Completas |
| **Backup** | Manual | Automático | Automático |
| **Custo** | Grátis | Free tier + pago | Free tier + pago |
| **Setup** | Zero | 5 minutos | 5 minutos |
| **Migração** | - | Fácil | Fácil |

---

## 🚀 Plano de Migração

### Fase 1: Preparação (1-2 horas)

1. **Criar conta no Neon**
   ```bash
   # Visite: https://neon.tech
   # Crie um projeto
   # Copie a connection string
   ```

2. **Atualizar .env**
   ```env
   DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require
   ```

3. **Atualizar models.py** (opcional - melhorias)
   ```python
   # Usar tipos nativos do PostgreSQL
   from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ
   
   # Em vez de JSONType customizado:
   template_data = Column(JSONB, nullable=False)  # Índices GIN automáticos
   ```

### Fase 2: Migração de Dados (30 min)

1. **Exportar dados do SQLite**
   ```python
   # Script de migração
   python scripts/migrate_sqlite_to_postgres.py
   ```

2. **Validar integridade**
   ```python
   # Comparar contagens
   python scripts/validate_migration.py
   ```

### Fase 3: Otimizações (opcional)

1. **Índices JSONB**
   ```sql
   -- Buscar templates por parâmetros específicos
   CREATE INDEX idx_template_data_params 
   ON combo_templates USING GIN (template_data);
   ```

2. **Particionamento** (para dados históricos)
   ```sql
   -- Particionar backtest_results por ano
   CREATE TABLE backtest_results_2025 
   PARTITION OF backtest_results 
   FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
   ```

---

## 💡 Benefícios Imediatos

### 1. **Queries JSON Mais Rápidas**
```python
# Antes (SQLite - scan completo):
templates = db.query(ComboTemplate).filter(
    ComboTemplate.template_data['ema_short'].astext == '20'
).all()

# Depois (PostgreSQL - índice GIN):
templates = db.query(ComboTemplate).filter(
    ComboTemplate.template_data['ema_short'].astext == '20'
).all()  # Usa índice!
```

### 2. **Queries Complexas**
```sql
-- Encontrar estratégias com melhor Sharpe ratio
SELECT 
    name,
    metrics->>'sharpe_ratio' as sharpe,
    metrics->>'total_return' as return
FROM favorite_strategies
WHERE (metrics->>'sharpe_ratio')::float > 1.5
ORDER BY (metrics->>'total_return')::float DESC
LIMIT 10;
```

### 3. **Full-Text Search**
```sql
-- Buscar estratégias por nome/descrição
SELECT * FROM combo_templates
WHERE to_tsvector('portuguese', name || ' ' || description) 
      @@ to_tsquery('portuguese', 'crossover & média');
```

---

## ⚠️ Quando NÃO Migrar

**Mantenha SQLite se:**
- ✅ Projeto é apenas local/pessoal
- ✅ Não precisa de múltiplos usuários simultâneos
- ✅ Volume de dados é pequeno (< 1GB)
- ✅ Não precisa de queries complexas em JSON

**Migre para PostgreSQL se:**
- ✅ Planeja deploy em produção
- ✅ Múltiplos usuários simultâneos
- ✅ Volume de dados crescente
- ✅ Precisa de queries eficientes em JSON
- ✅ Quer backups automáticos

---

## 🎯 Recomendação Final

**Para seu projeto de backtesting crypto:**

1. **Desenvolvimento Local**: Continue com SQLite (rápido, simples)
2. **Produção/Staging**: **Neon PostgreSQL** (serverless, fácil, grátis para começar)

**Por quê Neon?**
- ✅ Setup em 5 minutos
- ✅ Free tier generoso (0.5GB)
- ✅ Scale-to-zero (economiza quando não usa)
- ✅ Branching (dev/staging/prod isolados)
- ✅ Backup automático
- ✅ Performance excelente

**Custo estimado:**
- Free tier: Até 0.5GB (suficiente para começar)
- Paid: ~$19/mês para 10GB (quando crescer)

---

## 📝 Próximos Passos

1. **Testar Neon localmente**
   ```bash
   # Criar projeto no Neon
   # Adicionar DATABASE_URL ao .env
   # Rodar migrations
   python backend/init_db.py
   ```

2. **Migrar dados existentes** (se houver)
   ```bash
   python scripts/migrate_to_postgres.py
   ```

3. **Validar performance**
   ```bash
   # Comparar queries antes/depois
   python scripts/benchmark_queries.py
   ```

---

## 🔗 Links Úteis

- **Neon**: https://neon.tech
- **Supabase**: https://supabase.com
- **PostgreSQL JSONB Docs**: https://www.postgresql.org/docs/current/datatype-json.html
- **SQLAlchemy + PostgreSQL**: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html

---

**Conclusão**: Para um projeto de backtesting que usa muito JSON e pode crescer, **PostgreSQL (Neon)** é a melhor escolha. Oferece performance, escalabilidade e recursos avançados sem complexidade de gerenciamento.
