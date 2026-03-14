# Revisão PT-BR — alterar-dados-dos-cards

## Resumo

Esta change cobre a manutenção básica de cards já existentes no Kanban.

Hoje dá para criar/mover cards, mas ainda falta:
- editar **título**
- editar **descrição**
- **cancelar** card inválido/duplicado/descartado

## O que entra
- fluxo de editar título e descrição no card existente
- ação explícita de cancelamento
- persistência no runtime/workflow DB
- atualização imediata do board/detalhe após salvar
- preservação do histórico, sem apagar o card fisicamente

## O que não entra
- deletar card do banco
- reorder de cards
- edição em lote
- mudanças grandes no modelo de workflow

## Decisão de PO
- **cancelar ≠ deletar**: o card deve continuar auditável
- a UX deve ser simples e direta, preferencialmente a partir do detalhe do card
- cancelamento deve exigir intenção clara do usuário e deixar o item fora do fluxo ativo
- o fluxo deve continuar coerente com o runtime/Kanban como fonte principal de verdade

## Próximo gate
- DESIGN revisar a UX mínima do fluxo de edição/cancelamento e confirmar se basta um drawer/modal enxuto sem protótipo extenso
