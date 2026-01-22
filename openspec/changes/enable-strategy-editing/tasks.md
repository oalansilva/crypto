# Tarefas: Habilitar Edição de Templates de Estratégia

## Fase 1: API Backend (4 tarefas)
- [x] Adicionar endpoint `PUT /api/combos/meta/{template_name}` para atualizar metadados e optimization_schema do template
- [x] Adicionar lógica de validação para garantir min < max, step > 0, e sem mudanças quebradas no schema
- [x] Adicionar endpoint `POST /api/combos/meta/{template_name}/clone` para duplicar um template com novo nome
- [x] Adicionar migração/atualização no banco para suportar flag `is_readonly` na tabela combo_templates

## Fase 2: UI Frontend (6 tarefas)
- [x] Criar página `/combo/edit/:templateName` com formulário para editar parâmetros de otimização
- [x] Adicionar botão "Editar" nos cards de template na página `/combo/select`
- [x] Implementar validação de formulário (client-side) correspondente às regras do backend
- [x] Adicionar ação "Clonar Template" para templates somente-leitura
- [x] Exibir toasts de sucesso/erro após operações de salvamento
- [x] **[Novo]** Adicionar toggle "Modo Avançado" que exibe editor JSON (Monaco Editor ou similar) para edição direta do schema completo

## Fase 3: Integração & Testes (3 tarefas)
- [x] Testar fluxo de edição: modificar ranges → salvar → verificar banco atualizado → usar no backtest
- [x] Testar fluxo de clonagem: clonar pré-construído → editar clone → verificar original inalterado
- [x] Adicionar teste E2E cobrindo workflows de edição e clonagem

## Fase 4: Polimento (2 tarefas)  
- [ ] Adicionar diálogo de confirmação antes de salvar mudanças para avisar sobre impacto em backtests futuros
- [ ] Atualizar walkthrough/documentação com nova funcionalidade de editor

## Dependências
- Fase 2 depende da Fase 1 (API deve existir antes da UI poder chamá-la)
- Fase 3 pode iniciar assim que Fase 1 & 2 estiverem completas
- Fase 4 é trabalho de polimento independente

## Trabalho Paralelizável
- Lógica de validação do backend pode ser desenvolvida junto com migração do banco
- Componentes de formulário do frontend podem ser construídos enquanto API está sendo implementada (usando dados mock)
