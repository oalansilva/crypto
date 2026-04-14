# Tasks — Card #91

## Mudança: Ajustes Tela Playground - Remover Referências ao Kanban

---

## DEV Tasks

- [x] 1. Buscar todas as referências ao Kanban no frontend**
  
  Buscar por: "kanban", "Kanban", "Kaban" nos arquivos do projeto crypto.
  
  **Critério de Aceite:** Lista completa de arquivos com referências

- [x] 2. Identificar componentes da tela playground**
  
  Localizar componentes que renderizam "Abrir Kanban" e "Kanban Real".
  
  **Critério de Aceite:** Componentes identificados

- [x] 3. Remover "Abrir Kanban"
  
  Remover botão/link da tela playground.
  
  **Critério de Aceite:** Texto "Abrir Kanban" não existe mais

- [x] 4. Remover "Kanban Real"
  
  Remover texto/config da tela playground.
  
  **Critério de Aceite:** Texto "Kanban Real" não existe mais

- [x] 5. Verificar outras telas
  
  Confirmar que não há resíduos em outras telas do crypto.
  
  **Critério de Aceite:** Nenhuma outra referência ao Kanban encontrada

- [ ] **6. Testar playground**
  
  Garantir que tela playground funciona normalmente após remoção.
  
  **Critério de Aceite:** Playground funciona sem erros

---

## QA Tasks

- [x] 7. Validar remoção de "Abrir Kanban"**
  
  Buscar na UI por "Abrir Kanban" — não deve existir.
  
  **Critério de Aceite:** Texto não aparece na interface

- [x] 8. Validar remoção de "Kanban Real"**
  
  Buscar na UI por "Kanban Real" — não deve existir.
  
  **Critério de Aceite:** Texto não aparece na interface

- [x] 9. Verificar links para /kanban**
  
  Garantir que não há links funcionando para /kanban.
  
  **Critério de Aceite:** Nenhum link para /kanban funciona

- [ ] **10. Testar usabilidade do playground**
  
  Playground continua funcional após limpeza.
  
  **Critério de Aceite:** Todas as funcionalidades do playground funcionam

---

## Notas

- **Depende de card #88** — contexto: limpeza pós-remoção do Kanban
- **Sem protótipo** — é limpeza, não adição de UI
- **Risco baixo** — remoção simples de texto
