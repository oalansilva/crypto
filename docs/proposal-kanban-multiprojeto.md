# Proposal: Separar Sistema Kanban do Projeto Crypto

## Problema

O sistema kanban atual está fortemente integrado ao projeto "crypto". O objetivo é torná-lo **multiprojeto**, permitindo que diferentes projetos (ex: crypto, fintech, pessoal) usem o mesmo sistema de kanban com seleção de projeto.

## Análise do Estado Atual

### Banco de Dados
- ✅ Já existe tabela `wf_projects` com suporte a múltiplos projetos
- ✅ Estrutura: `id`, `slug`, `name`, `created_at`
- ❌ Nenhum projeto criado ainda (banco vazio)

### Frontend
- ❌ KanbanPage não tem seletor de projeto
- ❌ API/backend não expõe endpoints de projeto

### Backend
- ✅ Modelos SQLAlchemy definidos (`Project`, `Change`, `WorkItem`)
- ❌seed inicial do projeto "crypto" não existe

## Solução Proposta

### Fase 1:seed do Projeto "Crypto"
- Criar projeto inicial "crypto" no banco de dados
- Slug: `crypto`
- Nome: `Crypto Trading`

### Fase 2: API de Projetos
- `GET /api/projects` - listar todos projetos
- `GET /api/projects/:slug` - detalhes de um projeto
- `POST /api/projects` - criar novo projeto

### Fase 3: Frontend - Seletor de Projeto
- Adicionar dropdown/selector no header do Kanban
- Persistir seleção no localStorage
- **Por padrão**, carregar projeto "crypto"

### Fase 4: Integração Kanban ↔ Projeto
- Todas as operações do kanban devem filtrar por `project_id`
- Mudar CRUD de changes/work-items para usar o projeto selecionado

## Escopo MVP

1. ✅seed do projeto "crypto"
2. ✅ Selector de projeto no frontend
3. ✅ CRUD básico de projetos
4. ✅ Kanban filtrando por projeto selecionado

## Fora do Escopo (Futuro)
- Permissões por projeto
- Arquivo/mover cards entre projetos
- Dashboard agregado multi-projeto

## Impacto
- Backend: ~2-3 endpoints novos
- Frontend: ~1 dia de trabalho (selector + integração)
- Banco: sem mudança (schema já suporta)

## Timeline Sugerido
- **DEV**: 1 dia
- **QA**: Validação funcional simples
