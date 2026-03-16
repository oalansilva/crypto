# Tasks: Tela para Novo Card

## Tarefas de Desenvolvimento

### 1. Implementação do Modal

- [ ] **DEV-1**: Criar componente de Modal/Overlay reutilizável
  - Estilização base (posição, backdrop, animação)
  - Props: isOpen, onClose, title, children
  - Tratamento de clique fora do modal

- [ ] **DEV-2**: Criar botão "Novo Card" na tela principal
  - Posicionamento adequado
  - Estilização conforme design system
  - Evento onClick para abrir o modal

- [ ] **DEV-3**: Criar formulário de Novo Card dentro do Modal
  - Campos: título, descrição, prioridade (opcional)
  - Validação de campos obrigatórios
  - Estados: default, loading, erro, sucesso

- [ ] **DEV-4**: Implementar lógica de criação do card
  - Chamada à API/backend
  - Tratamento de resposta
  - Atualização da lista de cards
  - Feedback visual (sucesso/erro)

### 2. Melhorias e Polish

- [ ] **DEV-5**: Adicionar animações de entrada/saída do modal
- [ ] **DEV-6**: Implementar responsividade (mobile/tablet)
- [ ] **DEV-7**: Adicionar acessibilidade (ARIA, tab navigation, focus trap)

### 3. Qualidade

- [ ] **QA-1**: Testar fluxo completo de criação
- [ ] **QA-2**: Testar validações (campos obrigatórios)
- [ ] **QA-3**: Testar tratamento de erros
- [ ] **QA-4**: Testar responsividade
- [ ] **QA-5**: Validar acessibilidade

---

## Ordem de Implementação Sugerida

1. Componente Modal (DEV-1)
2. Botão + Formulário (DEV-2, DEV-3)
3. Lógica de criação (DEV-4)
4. Animações e polish (DEV-5, DEV-6)
5. Acessibilidade (DEV-7)
6. QA (todas as tarefas)
