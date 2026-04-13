# Proposal: Remover Funcionalidade Kanban do Projeto Crypto

## User Story

**Como** usuário do projeto crypto  
**Eu quero** não ver mais a funcionalidade Kanban integrada  
**Para** simplificar a aplicação e usar o Kanban standalone diretamente quando necessário

---

## Value Proposition

- **Simplifica o projeto crypto** — menos código, menos dependências
- **Reduz confusão** — usuários usam Kanban standalone em vez de versão embarcada
- **Manutenção simplificada** — duas bases de código menos acopladas

---

## Scope In

- Remover rota `/kanban` do projeto crypto
- Remover item de navegação que aponta para `/kanban` em AppNav.tsx
- Remover importação e uso de `KanbanPage` no projeto crypto
- Remover qualquer link para `#/party` ou rotas relacionadas ao Kanban

---

## Scope Out

- Não remove o projeto Kanban standalone
- Não remove dados do Kanban — tudo continua funcionando em app separado
- Não afeta rotas/funcionalidades não relacionadas ao Kanban

---

## Technical Notes

**Arquivos afetados no projeto crypto:**
1. `App.tsx` ou arquivo de rotas — remover rota `/kanban` pointing to KanbanPage
2. `AppNav.tsx` — remover SIDEBAR_ITEMS entry: `{ label: 'Kanban', route: '#/kanban', ... }`
3. `mainNavItems` ou `strategyNavItems` — depending on where the Kanban nav item is defined
4. Qualquer import de `KanbanPage` ou componentes relacionados

**Verificar:**
- `frontend/src/App.tsx` — rotas
- `frontend/src/components/AppNav.tsx` — navegação lateral
- `frontend/src/pages/` —是否有KanbanPage

---

## Dependencies

- None — standalone removal

---

## Risks

1. **Usuários perdem acesso** — quem usava Kanban via crypto precisa saber que deve usar app separado
2. **Comunicação** — usuários precisam ser avisados da mudança
3. **Bookmarks** — usuários com bookmark para `/kanban` no crypto vão perder acesso
4. **FuncionalidadeParty Mode** — verificar se Party Mode depende do Kanban integrado

---

## ICE Score

- Impact: 6 (simplifica projeto, mas afeta fluxo de usuários)
- Confidence: 8 (scope claro, implementação direta)
- Ease: 9 (remover código é simples)
- **ICE: 432**
