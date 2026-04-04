# separar-kanban-do-crypto

## Status
- PO: done ✅
- DESIGN: done ✅
- DEV: not started
- QA: not started
- Alan approval: pending
- Homologation: not reviewed

> Gate order: PO must be **done** before Alan approves to implement.

## Decisions (locked)
- Kanban multi-projeto JÁ EXISTE: `ProjectSelector` + `project_slug` na API
- Gap: UX/implementação do seletor de projeto precisa melhorar
- Gap adicional: entidade `Project` ainda não guarda diretório, URLs e banco por projeto
- Escopo: backend + frontend
- Bug identificado: cache invalidation mismatch após mutações

## Links
- OpenSpec folder: `openspec/changes/separar-kanban-do-crypto/`
- PT-BR review (viewer): (pending)
- PR: (pending)
- CI run: (pending)

## Notes
- Card #85
- Description: "Quero separar o kanban do projeto Crypto o kanban se torna um outro projeto onde eu posso escolher qual projeto quero ver Crypto e um deles"
- Card #17 (mesmo requisito) foi CANCELLED em 2026-03-18 - arquitetura já implementada parcialmente

---

## Análise PO Completa

### Estado Atual (O que existe)

**Backend:**
- `GET /workflow/projects` → retorna 2 projetos: `crypto` (85 changes), `trading-bot` (0 changes)
- `GET /workflow/kanban/changes?project_slug=XYZ` → filtra changes por projeto ✅
- `POST /workflow/kanban/changes?project_slug=XYZ` → cria change no projeto correto ✅
- `_kanban_project_slug()` → default é primeiro projeto (crypto) se não especificado ✅
- Seed de `crypto` em `main.py` ✅

**Frontend:**
- `ProjectSelector.tsx` → dropdown de projetos ✅
- `KanbanPage.tsx` → `selectedProject` state usado em TODAS as API calls ✅
- Default `selectedProject = 'crypto'` em linha 276 ✅

### Gap Identificado

**Problema 1: URL não reflete projeto selecionado**
- Sem URL parameter (`?project=XYZ`), não há como compartilhar/linkar uma view de projeto específico
- Refresh da página → projeto reseta para `crypto` (default do useState)
- Sem localStorage persistence

**Problema 2: HomePage hardcoded para crypto**
- `HomePage.tsx` linha 284: `/workflow/kanban/changes?project_slug=crypto` (hardcoded)
- `HomePage.tsx` linha 296: `/workflow/projects/crypto/changes/...` (hardcoded)
- HomePage nunca usa o seletor de projeto

**Problema 3: Cache invalidation mismatch (bug menor)**
- Query key: `['kanban', 'changes', selectedProject]`
- `onSuccess` invalidates: `['kanban', 'changes']` (sem o `selectedProject`)
- Resultado: após criar card, kanban pode não refresh se projeto ≠ 'crypto'

### Classificação do Gap

**Tipo: UX + Bug menor + Gap arquitetural**

O sistema JÁ SUPORTA multi-projeto corretamente na camada de API. O gap é de UX:
1. Usuário não consegue linkar/compartilhar view de projeto específico
2. Experiência de "separate kanban from crypto" não é completa porque tudo reseta para crypto
3. HomePage não participa do contexto de projeto
4. O cadastro de projeto não suporta isolamento operacional real para diretório/URLs/banco

### Requisito Centrale

"Quero separar o kanban do Crypto" = O kanban deve ser um layer INDEPENDENTE de projeto, onde o usuário pode:
1. Escolher qual projeto ver (já funciona via ProjectSelector)
2. Compartilhar/linkar a view de um projeto específico (NÃO funciona - sem URL)
3. Ver que está num projeto diferente do "crypto" default (confuso sem indicador visual)

### Escopo Técnico

- **Backend:** expandir `wf_projects` e APIs para metadados de isolamento
- **Frontend:** URL sync (react-router), localStorage persistence, HomePage deshardcoded
- **Bug fix:** React Query invalidation com queryKey correto

## Handoff Log

### [PO-Agent] 2026-04-03 23:20 UTC
Card #85 puxado do Pending para PO.

**Análise inicial - estado atual:**
- Frontend: `ProjectSelector` já existe em `KanbanPage.tsx` (linha 1010)
- Backend: API aceita `project_slug` nas chamadas `/workflow/kanban/changes`
- DB: existem projetos "crypto" e "trading-bot" via `/api/workflow/projects`
- O card ainda não tem pasta em `openspec/changes/separar-kanban-do-crypto/`

**Hipótese:** o card pode ser sobre:
1. Bug: o ProjectSelector não está funcionando corretamente em algum fluxo
2. UX: melhorar a experiência do seletor de projeto
3. Arquitetura: criar projeto "kanban" independente ou separar contexto

### [PO-Agent] 2026-04-04 00:15 UTC
**Análise completa - gap identificado:**

- API multi-projeto: ✅ FUNCIONANDO
- Gap: URL não persiste projeto selecionado (sem URL param, sem localStorage)
- HomePage hardcoded: `?project_slug=crypto` em 2 lugares
- Bug cache invalidation: query key mismatch
- Gap arquitetura: `wf_projects` ainda não modela diretório/URLs/banco próprios

**Decisão:** Classificado como UX gap + arquitetura

**Artefatos criados:** proposal.md, spec.md, tasks.md

**Handoff:** PO ✅ → DESIGN (pendente)

## Next actions
- [x] PO: Analisar gap entre implementação atual e requisito do card
- [x] PO: Definir se precisa de novo projeto "kanban" ou se existente funciona
- [x] PO: Definir escopo técnico (backend/frontend/ambos)
- [x] PO: Criar OpenSpec artifacts (proposal, spec, tasks)
- [ ] DESIGN: Criar protótipo de UX para URL sync e ProjectSelector mais visível
- [ ] DESIGN: Revisar HomePage hardcoded (criar proposal/PT-BR review)
- [ ] DEV: Implementar URL sync (react-router param)
- [ ] DEV: Implementar localStorage persistence
- [ ] DEV: Corrigir cache invalidation bug
- [ ] DEV: Remover hardcoded crypto da HomePage
- [ ] QA: Validar project switching e URL sharing

### [DESIGN Agent] 2026-04-04 00:XX UTC
Design completo: `openspec/changes/separar-kanban-do-crypto/design.md` criado.

**Decisões de design:**
- URL sync via `useSearchParams` + `localStorage` persistence
- `?project=<slug>` como URL parameter (sem mudança de rota)
- Badge cyan quando projeto ≠ crypto
- Cache invalidation: queryKey completo com `selectedProject`
- HomePage deshardcoded via `localStorage.getItem('kanban.lastProject')`

**Handoff:** DESIGN ✅ → Alan approval
