# Tasks — Card #70: [MT-2] Multi-tenant Data Isolation

## 1. Adicionar `user_id` às tabelas

- [ ] 1.1 Adicionar `user_id` em `signal_history` (SQLAlchemy model + migration)
- [ ] 1.2 Adicionar `user_id` em `portfolio_snapshots` (SQLAlchemy model + migration)
- [ ] 1.3 Adicionar `user_id` em `favorite_strategies` (SQLAlchemy model + migration)
- [ ] 1.4 Adicionar `user_id` em `monitor_preferences` (reestruturar PK)
- [ ] 1.5 Adicionar `user_id` em `backtest_runs` (SQLAlchemy model + migration)
- [ ] 1.6 Adicionar `user_id` em `combo_templates` (SQLAlchemy model + migration)
- [ ] 1.7 Criar índices em `user_id` em todas as tabelas afetadas

## 2. Criar dependency `get_current_user_id()`

- [ ] 2.1 Criar dependency que extrai `user_id` do JWT no request state
- [ ] 2.2 Documentar uso nos endpoints

## 3. Isolar Signals (`/api/signals`)

- [ ] 3.1 GET /api/signals — filtrar por `user_id`
- [ ] 3.2 POST /api/signals — adicionar `user_id` no INSERT
- [ ] 3.3 PATCH /api/signals/{id} — validar ownership
- [ ] 3.4 DELETE /api/signals/{id} — validar ownership

## 4. Isolar Portfolio (`/api/portfolio`)

- [ ] 4.1 GET /api/portfolio — filtrar snapshots por `user_id`
- [ ] 4.2 POST /api/portfolio/snapshot — adicionar `user_id` no INSERT

## 5. Isolar Favoritos (`/api/favorites`)

- [ ] 5.1 GET /api/favorites — filtrar por `user_id`
- [ ] 5.2 POST /api/favorites — adicionar `user_id` no INSERT
- [ ] 5.3 PUT /api/favorites/{id} — validar ownership
- [ ] 5.4 DELETE /api/favorites/{id} — validar ownership

## 6. Isolar Monitor Preferences (`/api/monitor-preferences`)

- [ ] 6.1 GET /api/monitor-preferences — retornar prefs do `user_id`
- [ ] 6.2 PUT /api/monitor-preferences — UPSERT com `user_id`

## 7. Isolar Backtest (`/api/backtest`)

- [ ] 7.1 GET /api/backtest — filtrar por `user_id`
- [ ] 7.2 POST /api/backtest — adicionar `user_id` no INSERT

## 8. Isolar Combo Templates (`/api/combo`)

- [ ] 8.1 GET /api/combo/templates — filtrar por `user_id`
- [ ] 8.2 POST /api/combo/templates — adicionar `user_id` no INSERT
- [ ] 8.3 PUT /api/combo/templates/{id} — validar ownership
- [ ] 8.4 DELETE /api/combo/templates/{id} — validar ownership

## 9. Validação e Testes

- [ ] 9.1 Verificar que GET sem token retorna 401
- [ ] 9.2 Verificar que GET retorna apenas dados do usuário logado
- [ ] 9.3 Verificar que POST cria recurso com `user_id` correto
- [ ] 9.4 Verificar que PATCH/DELETE em recurso de outro usuário retorna 403
- [ ] 9.5 Verificar que não há vazamento de dados entre usuários

## 10. Documentação

- [ ] 10.1 Atualizar OpenAPI/spec com informação de isolamento
- [ ] 10.2 Documentar a regra: todas as tabelas de dados de usuário têm `user_id`
