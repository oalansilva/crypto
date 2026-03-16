# Proposta: Tela para Novo Card

## Problema

 Atualmente, para criar um novo card o usuário interage na mesma tela principal. A issue solicita que haja uma tela separada (modal/overlay) aberta ao clicar em um botão, criando uma experiência mais focada e limpa para criação de novos cards.

## Solução Proposta

Implementar um **modal/overlay** (tela menor sobreposta) para criação de novos cards.

### Comportamento Esperado

1. **Botão de ação**: Um botão "Novo Card" (ou similar) na interface principal
2. **Ação ao clicar**: Abre um modal/overlay centralizado sobre a tela principal
3. **Conteúdo do modal**: Formulário para preenchimento dos dados do card
4. **Fechamento**: 
   - Botão "Cancelar" ou "X" para fechar sem salvar
   - Botão "Salvar" para criar e fechar
   - Clique fora do modal para fechar (opcional)
5. **Feedback**: Loading states e mensagens de sucesso/erro

### Elementos do Formulário (a serem detalhados pelo DEV)

- Título do card
- Descrição
- Prioridade
- Outras informações relevantes

## Critérios de Aceitação

- [ ] Botão "Novo Card" visível na tela principal
- [ ] Ao clicar, abre modal/overlay centralizado
- [ ] Formulário com campos necessários é exibido
- [ ] Botão Salvar cria o card e fecha o modal
- [ ] Botão Cancelar fecha o modal sem salvar
- [ ] Modal fecha ao clicar fora (opcional)
- [ ] Feedback visual durante criação
- [ ] Tratamento de erros exibido ao usuário

## Priority

Média

## Notas

- Manter consistência com design system do projeto
- Considerar responsividade (mobile)
- Acessibilidade (tab navigation, ARIA labels)
