# Spec: Separar Kanban do Crypto

## ID
`kanban.multi-project-ux`

## Tipo
Arquitetura + UX Enhancement + Bug Fix

## Motivação

O kanban precisa ser semanticamente e operacionalmente independente do projeto "crypto". Hoje o sistema suporta multi-projeto via API, mas a UX não comunica isso claramente e a camada de projeto ainda não registra o isolamento real de diretório, URLs e banco por projeto.

---

## Functional Requirements

### FR-0: Projeto Deve Carregar Metadados de Isolamento

**Como:** Estender a entidade `Project` e suas APIs para guardar metadados operacionais por projeto.

**Campos mínimos:**
- `root_directory`
- `frontend_url`
- `backend_url`
- `workflow_database_url`
- `tech_stack`

**Comportamento:**
- `GET /api/workflow/projects` deve retornar esses campos
- `POST /api/workflow/projects` deve aceitar esses campos
- O sistema deve permitir projetos com stacks diferentes
- O seed padrão deve suportar pelo menos `crypto` e `kanban` como projetos distintos

**Critério de aceitação:**
- [ ] Projeto `crypto` pode apontar para diretório/URLs/banco próprios
- [ ] Projeto `kanban` pode existir separado do `crypto`
- [ ] Posso cadastrar um terceiro projeto com outra stack

### FR-0.1: Runtime Deve Ser PostgreSQL-Only

**Comportamento:**
- `DATABASE_URL` deve ser obrigatório e apontar para PostgreSQL
- `WORKFLOW_DATABASE_URL` deve ser obrigatório e apontar para PostgreSQL
- Cada projeto cadastrado deve ter `workflow_database_url` próprio em PostgreSQL
- SQLite pode existir apenas em testes explícitos

**Critério de aceitação:**
- [ ] Backend não sobe sem `DATABASE_URL`
- [ ] Workflow registry não sobe sem `WORKFLOW_DATABASE_URL`
- [ ] Projeto novo em runtime multi-projeto exige `workflow_database_url`

### FR-1: URL Sync para Projeto Selecionado

**Como:** Adicionar `?project=XYZ` query parameter na URL do kanban

**Comportamento:**
- URL `/kanban?project=crypto` mostra projeto crypto
- URL `/kanban?project=trading-bot` mostra projeto trading-bot
- URL `/kanban` (sem param) default = `crypto` (backward compatible)
- Trocar projeto no selector → URL atualiza via `react-router`
- Mudar URL manualmente → selector atualiza e dados carregam corretamente

**Tecnologia:** `useSearchParams` do react-router ou `useNavigate` + `useLocation`

**Arquivos:**
- `frontend/src/pages/KanbanPage.tsx`

**Critério de aceitação:**
- [ ] Refresh com `?project=trading-bot` mantém projeto selecionado
- [ ] Copiar URL e abrir em nova aba mantém projeto
- [ ] Browser back/forward funciona corretamente

---

### FR-2: localStorage Persistence

**Como:** Salvar projeto selecionado em localStorage

**Comportamento:**
- Chave: `kanban_selected_project`
- Lê ao montar KanbanPage (antes do useState default)
- Atualiza ao trocar projeto no selector
- Se localStorage tem valor válido, usa ele como default (sobrescreve hardcoded 'crypto')
- Se projeto do localStorage não existe mais, fallback para 'crypto'

**Critério de aceitação:**
- [ ] Fecho aba e abro nova → projeto selecionado é mantido
- [ ] Troco para trading-bot → fecho aba → abro nova → trading-bot mantido
- [ ] Projeto do localStorage foi deletado do DB → fallback para crypto

---

### FR-3: Corrigir Cache Invalidation Bug

**Problema:** Query key `['kanban', 'changes', selectedProject]` não é invalidado corretamente

**Como:** Corrigir `onSuccess` callbacks para incluir `selectedProject` no queryKey

**Arquivos:**
- `frontend/src/pages/KanbanPage.tsx` (createChange, updateSelectedChange, moveChange, archiveChange mutations)

**Critério de aceitação:**
- [ ] Crio card em trading-bot → kanban refresh mostra o novo card imediatamente
- [ ] Movo card de Pending → Done → kanban atualiza sem precisar refresh

---

### FR-4: HomePage Deshardcoded

**Problema:** HomePage hardcoded `?project_slug=crypto` em 2 lugares

**Como:** Usar valor do localStorage (ou default 'crypto') em vez de hardcoded

**Comportamento:**
- `HomePage.tsx` lê `localStorage.getItem('kanban_selected_project') || 'crypto'`
- Usa esse valor no `project_slug` param

**Arquivos:**
- `frontend/src/pages/HomePage.tsx`

**Critério de aceitação:**
- [ ] HomePage mostra changes do último projeto selecionado no kanban
- [ ] Se nunca selecionou projeto, default = crypto

---

## Non-Functional Requirements

- **Performance:** urlSync não pode causar reload de dados desnecessário
- **Compatibilidade:** default = 'crypto' para backward compatibility
- **Mobile:** funcionando igual desktop
- **Isolamento:** o cadastro de projeto não deve assumir que todos os projetos compartilham o mesmo diretório, URL ou banco

---

## Edge Cases

1. **Projeto inexistente na URL:** fallback para 'crypto'
2. **localStorage corrompido:** fallback para 'crypto'
3. **Projeto deletado do DB:** frontend mostra erro se não encontrar
4. **Primeiro acesso (sem localStorage):** default = 'crypto'
5. **Projeto cadastrado sem URLs ainda:** sistema continua listando o projeto sem quebrar o selector

---

## Critérios de Aceitação Gerais

- [ ] Kanban funciona como "layer independente de projeto"
- [ ] Usuário consegue trocar entre crypto e trading-bot seamless
- [ ] URL e localStorage funcionam como source of truth para projeto selecionado
- [ ] API de projetos expõe metadados próprios de diretório/URLs/banco
