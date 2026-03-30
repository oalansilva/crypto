# Proposal — Card #70: [MT-2] Multi-tenant Data Isolation

## Problema

O Card #69 implementou autenticação JWT, mas o sistema ainda expõe dados de todos os usuários indistintamente. Qualquer usuário autenticado consegue ver sinais, portfólio e histórico de outros usuários. É necessário isolar dados por `user_id` para garantir privacy e segurança.

## Solução

Implementar isolamento de dados por `user_id` em todas as tabelas e queries do sistema:

- Adicionar `user_id` como foreign key em todas as tabelas que armazenam dados de usuário
- Modificar todas as queries para filtrar por `user_id` autenticado (extraído do JWT em `/api/auth/me`)
- Garantir que cada usuário só veja seus próprios dados

## User Stories

1. **Isolamento de Sinais** — Como usuário logado, quero ver apenas meus próprios sinais, não os de outros usuários.
2. **Isolamento de Portfólio** — Como usuário logado, quero ver apenas meu próprio portfólio e histórico.
3. **Isolamento de Estratégias** — Como usuário logado, quero ver e editar apenas minhas estratégias favoritas.
4. **Queries Seguras** — Como sistema, quero que todas as queries de dados de usuário filtragem por `user_id`.

## Critérios de Aceitação

- [ ] Todas as tabelas com dados de usuário têm `user_id` (signals, portfolio_snapshots, favorite_strategies, etc.)
- [ ] Todas as queries que retornam dados de usuário filtram por `user_id` autenticado
- [ ] Endpoints de lista retornam apenas dados do usuário logado
- [ ] Endpoints de criação associam o `user_id` do token JWT
- [ ] Endpoints de update/delete validam que o recurso pertence ao usuário logado
- [ ] Erro 403 se usuário tenta acessar recurso de outro usuário

## Escopo

**Inclui:**
- Adicionar `user_id` em: `signal_history`, `portfolio_snapshots`, `favorite_strategies`, `monitor_preferences`, `backtest_runs`, `combo_templates`
- Middleware/decorator para injetar `user_id` em requests
- Filtrar todas as queries por `user_id`
- Validação de ownership em update/delete
- Criar índice em `user_id` em todas as tabelas afetadas

**Não inclui:**
- Implementação de roles/permissões (MT-3)
- Compartilhamento explícito de dados entre usuários
- Migrar dados existentes para novos usuários (sistema novo, sem dados legados)

## Dependências

- Card #69 (multi-tenant-auth-login) ✅ — JWT e autenticação devem estar funcionais antes deste card

## Notas Técnicas

- `user_id` vem do payload JWT (`sub` claim) decoded em `/api/auth/me`
- Todas as tabelas afetadas usam SQLite com SQLAlchemy (mesmo stack do projeto)
- Foreign key: `user_id` → `users.id`
