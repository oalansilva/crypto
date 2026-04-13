# Tasks — Card #88

## Mudança: Remover Funcionalidade Kanban do Projeto Crypto

---

## DEV Tasks

- [x] **1. Remover rota `/kanban` de App.tsx**
  
  Localizar e remover a rota que aponta para KanbanPage em App.tsx ou arquivo de rotas.
  
  **Critério de Aceite:** Rota `/kanban` não existe mais no projeto crypto

- [x] **2. Remover item de navegação Kanban de AppNav.tsx**
  
  Remover SIDEBAR_ITEMS entry: `{ label: 'Kanban', route: '#/kanban', ... }` ou similar.
  
  **Critério de Aceite:** Item de navegação Kanban não aparece mais no menu lateral

- [x] **3. Remover imports de KanbanPage**
  
  Remover qualquer import de `KanbanPage` ou componentes relacionados.
  
  **Critério de Aceite:** Nenhum import de Kanban no código do crypto

- [ ] **4. Verificar Party Mode**
  
  Confirmar que Party Mode ainda funciona no app Kanban standalone após remoção.
  
  **Critério de Aceite:** Party Mode não é afetado pela remoção

---

## QA Tasks

- [ ] **5. Validar remoção de rota**
  
  Acessar `/kanban` no projeto crypto deve resultar em 404 ou redirect.
  
  **Critério de Aceite:** Rota não existe mais

- [ ] **6. Validar navegação**
  
  Menu lateral não mostra mais item Kanban.
  
  **Critério de Aceite:** Navegação atualizada corretamente

- [ ] **7. Verificar outras funcionalidades**
  
  Confirmar que outras funcionalidades do crypto não foram afetadas.
  
  **Critério de Aceite:** App crypto funciona normalmente exceto pela remoção do Kanban

---

## Notas

- **Sem protótipo necessário** — é remoção, não adição de UI
- **Sem mudança de schema** — apenas remoção de código
- **URL do Kanban standalone:** Provavelmente `http://127.0.0.1:5174/` ou similar — confirmar
