# Tasks: Kanban Multiprojeto

## Task List

### T1: Seed Projeto "Crypto" no Banco
- [ ] **T1.1** - Criar script de seed para projeto "crypto"
  - Arquivo: `crypto/backend/scripts/seed_crypto_project.py`
  - Executar: criar projeto com slug="crypto", name="Crypto Trading"
  - Validar: verificar se projeto foi criado no DB

### T2: API de Projetos
- [ ] **T2.1** - Adicionar endpoint `GET /api/projects` (listar projetos)
  - Arquivo: `crypto/backend/app/routes/workflow.py` (ou criar novo)
  - Retorno: lista de projetos com id, slug, name
  
- [ ] **T2.2** - Adicionar endpoint `POST /api/projects` (criar projeto)
  - Input: `{ slug, name }`
  - Validação: slug único
  
- [ ] **T2.3** - Adicionar endpoint `GET /api/projects/:slug` (detalhes)

### T3: Frontend - Selector de Projeto
- [ ] **T3.1** - Criar componente `ProjectSelector.tsx`
  - Local: `crypto/frontend/src/components/`
  - Funcionalidade: dropdown com lista de projetos
  - Persistência: localStorage (chave: `selectedProjectSlug`)
  
- [ ] **T3.2** - Integrar selector no Layout/Header
  - Mostrar próximo ao título "Kanban"
  - Estilizar para ficar coerente com UI existente

### T4: Kanban - Filtrar por Projeto
- [ ] **T4.1** - Modificar KanbanPage para usar `projectSlug` do contexto
  - Passar `projectSlug` para todas as queries de changes/work-items
  
- [ ] **T4.2** - Atualizar mutations para incluir `project_id`
  - Create/Update/Delete de changes
  - Create/Update de work-items

### T5: Validação QA
- [ ] **T5.1** - Testar criação de novo projeto (via API)
- [ ] **T5.2** - Testar selector: trocar para projeto inexistente → mostrar erro/feedback
- [ ] **T5.3** - Testar selector: trocar para "crypto" → carregar cards corretos
- [ ] **T5.4** - Testar CRUD de cards no projeto selecionado
- [ ] **T5.5** - Testar persistência: refresh página → manter projeto selecionado

---

## Dependencies
- T2 depende de T1 (projeto existente para testar)
- T3 depende de T2 (precisa da API)
- T4 depende de T3 (precisa do selector)

## Prioridade
1. T1 (seed) - Sem isso, sistema não funciona
2. T2 (API) - Base para tudo
3. T3 (selector) - Interface principal
4. T4 (filtro) - Funcionalidade core
5. T5 (QA) - Validação

## Notas
- Backend usa SQLAlchemy (ver `workflow_models.py`)
- Frontend usa React + TanStack Query
- API base: `API_BASE_URL` (ver lib/apiBase.ts)
