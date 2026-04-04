# Proposal: Separar Kanban do Crypto

## Resumo

**Problema:** O kanban atual é semanticamente e operacionalmente acoplado ao projeto "Crypto" — o default é sempre `crypto`, não há como compartilhar/linkar uma view de outro projeto, o HomePage é hardcoded para `crypto` e o runtime de projetos ainda não guarda diretório, URLs e banco próprios por projeto.

**Solução:** Tornar o kanban um hub de projetos independentes, com metadados de isolamento por projeto (`root_directory`, `frontend_url`, `backend_url`, `workflow_database_url`, `tech_stack`), além de URL-based project persistence e deshardcoded do HomePage.

**Tipo:** Arquitetura + UX Enhancement + Bug Fix

---

## Contexto

O sistema JÁ POSSUI suporte multi-projeto lógico:
- `ProjectSelector` no frontend
- `project_slug` parameter na API
- 2 projetos no DB: `crypto` (85 changes), `trading-bot` (0 changes)

Porém, a experiência usuário não refleja essa capacidade:
1. Refresh da página → projeto reseta para `crypto` (sem URL param, sem localStorage)
2. Sem URL param → não é possível compartilhar link para view de projeto específico
3. `HomePage.tsx` hardcoded para `crypto` em 2 lugares
4. A entidade `Project` não guarda o isolamento operacional necessário para projetos realmente independentes

---

## Proposta de Solução

### 0. Metadados de Isolamento por Projeto

Cada projeto deve registrar:
- diretório raiz próprio
- URL de frontend própria
- URL de backend própria
- URL de banco de workflow própria
- stack/tecnologia principal

Isso permite que o kanban seja um hub para projetos heterogêneos, sem assumir que todos vivem no mesmo app/runtime.

### 0.1. PostgreSQL Obrigatório no Runtime

- Remover fallback de SQLite para banco principal do app
- Remover fallback de SQLite para workflow DB
- Operar com:
  - banco principal Postgres
  - registry de projetos em Postgres
  - workflow DB próprio por projeto em Postgres

### 1. URL Sync para Projeto Selecionado

Adicionar `?project=XYZ` na URL do kanban:
- `/kanban?project=crypto` (default se não especificado)
- `/kanban?project=trading-bot`
- React Router gerencia o sync
- Backward compatible: sem param usa `crypto` como default

### 2. localStorage Persistence

Salvar `selectedProject` em localStorage:
- Chave: `kanban_selected_project`
- Lê ao carregar página (sobrescreve default do useState)
- Atualiza ao trocar projeto no selector

### 3. Corrigir Cache Invalidation Bug

O query key `['kanban', 'changes', selectedProject]` não é invalidado corretamente após mutations que usam `['kanban', 'changes']`.

### 4. HomePage Deshardcoded

Substituir `?project_slug=crypto` hardcoded no HomePage pelo projeto atualmente selecionado (via context ou localStorage).

---

## Dependências

- Nenhuma mudança no backend necessária
- Frontend only (react-router, localStorage)

---

## Riscos

- **Baixo:** Mudança de escopo local em KanbanPage e HomePage
- **Mitigação:** Manter backward compatibility (default continua sendo 'crypto')

---

## Próximo Passo

DESIGN → Protótipo de UX para visualização do ProjectSelector mais proeminente e feedback visual de projeto selecionado na URL.
