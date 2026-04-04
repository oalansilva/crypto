# Tasks: Separar Kanban do Crypto

## Task List

### T0: Isolamento de Projeto no Runtime (FR-0)

- [ ] **T0.1** - Estender `wf_projects` com metadados próprios
  - Campos: `root_directory`, `frontend_url`, `backend_url`, `workflow_database_url`, `tech_stack`
  - Arquivos: `backend/app/workflow_models.py`, `backend/app/workflow_database.py`

- [ ] **T0.2** - Expor metadados nas APIs de projeto
  - `GET /api/workflow/projects`
  - `POST /api/workflow/projects`
  - Arquivo: `backend/app/routes/workflow.py`

- [ ] **T0.3** - Seedar projetos independentes padrão
  - Garantir `crypto` e `kanban` como slugs distintos
  - Arquivo: `backend/app/main.py`

- [ ] **T0.4** - Cobrir com testes de integração
  - Validar cadastro/listagem de projetos com diretórios/URLs/banco independentes
  - Arquivo: `backend/tests/integration/test_workflow_projects.py`

- [ ] **T0.5** - Remover SQLite do runtime
  - Exigir Postgres no banco principal, no registry e no workflow DB de cada projeto
  - Arquivos: `backend/app/database.py`, `backend/app/workflow_database.py`, `start.sh`, `backend/.env.example`

- [ ] **T0.6** - Migrar dados legados para os novos bancos
  - Copiar `backtest.db` para `CRYPTO_DATABASE_URL`
  - Distribuir workflow legado por `project_slug` para os novos bancos de workflow por projeto
  - Arquivo: `backend/scripts/migrate_projects_to_postgres.py`

- [ ] **T0.7** - Separar operação por projeto no bootstrap
  - `start.sh` e `stop.sh` devem aceitar `crypto`, `kanban` e `all`
  - Cada projeto com logs, pid files e portas independentes

### T1: URL Sync para Projeto (FR-1)

- [ ] **T1.1** - Adicionar `project` query param na URL do kanban
  - Arquivo: `frontend/src/pages/KanbanPage.tsx`
  - Usar `useSearchParams` ou `useNavigate` + `useLocation`
  - Inicializar `selectedProject` a partir da URL (com fallback 'crypto')
  - Trocar projeto → atualiza URL via `navigate`

- [ ] **T1.2** - Sincronizar selector com mudança de URL
  - Se URL muda (browser back/forward), atualizar `selectedProject`

- [ ] **T1.3** - Testar refresh com `?project=trading-bot`
  - Validar que projeto correto carrega

---

### T2: localStorage Persistence (FR-2)

- [ ] **T2.1** - Ler localStorage ao inicializar KanbanPage
  - Chave: `kanban_selected_project`
  - Se valor existe e é projeto válido, usar como default do useState

- [ ] **T2.2** - Escrever localStorage ao trocar projeto
  - `localStorage.setItem('kanban_selected_project', selectedProject)`
  - Fazer no `onProjectChange` callback

- [ ] **T2.3** - Tratar edge case: projeto deletado
  - Se localStorage tem slug que não existe mais, fallback para 'crypto'

---

### T3: Corrigir Cache Invalidation Bug (FR-3)

- [ ] **T3.1** - Corrigir `createChange` mutation
  - Query key: `['kanban', 'changes', selectedProject]`
  - `onSuccess` invalidate com queryKey correto

- [ ] **T3.2** - Corrigir `updateSelectedChange` mutation
  - Same fix: invalidate `['kanban', 'changes', selectedProject]`

- [ ] **T3.3** - Corrigir `moveChange` mutation
  - Same fix: invalidate `['kanban', 'changes', selectedProject]`

- [ ] **T3.4** - Corrigir `archiveChange` mutation
  - Same fix: invalidate `['kanban', 'changes', selectedProject]`

---

### T4: HomePage Deshardcoded (FR-4)

- [ ] **T4.1** - Substituir hardcoded `project_slug=crypto` por leitura de localStorage
  - Arquivo: `frontend/src/pages/HomePage.tsx` linha 284
  - Usar `localStorage.getItem('kanban_selected_project') || 'crypto'`

- [ ] **T4.2** - Substituir hardcoded `projects/crypto` no detail fetch
  - Arquivo: `frontend/src/pages/HomePage.tsx` linha 296
  - Usar mesma lógica de projeto selecionado

---

### T5: Validação QA

- [ ] **T5.1** - URL: refresh com `?project=trading-bot` mantém projeto selecionado
- [ ] **T5.2** - URL: copiar URL e abrir em nova aba mantém projeto
- [ ] **T5.3** - URL: browser back/forward funciona corretamente
- [ ] **T5.4** - localStorage: fecho aba e abro nova → projeto mantido
- [ ] **T5.5** - localStorage: projeto deletado do DB → fallback para crypto
- [ ] **T5.6** - Cache: criar card em trading-bot → kanban refresh imediato
- [ ] **T5.7** - Cache: mover card entre colunas → kanban atualiza
- [ ] **T5.8** - HomePage: mostra changes do último projeto selecionado
- [ ] **T5.9** - HomePage: primeiro acesso (sem localStorage) → default crypto

---

## Dependências

- T0 estabelece a base de isolamento real por projeto
- T2 (localStorage) pode ser feito antes de T1 (URL sync)
- T3 (cache bug) é independente
- T4 (HomePage) depende de T2 (precisa da função de leitura)

## Prioridade

1. T0 (isolamento runtime) - base arquitetural
2. T3 (bug fix) - Impacta funcionamento básico
3. T1 (URL sync) - Feature principal do card
4. T2 (localStorage) - Melhora UX
5. T4 (HomePage) - nice to have
6. T5 (QA) - Validação

## Notas Técnicas

- Backend agora precisa expor metadados de isolamento por projeto
- Frontend: React + TanStack Query + react-router
- Manter backward compatibility: default = 'crypto'
- Query key pattern: `['kanban', 'changes', selectedProject]`
