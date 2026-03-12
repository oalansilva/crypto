## Resumo PT-BR

Esta change propõe transformar o `/kanban` em uma superfície de entrada de backlog e movimentação real de cards.

### O que entra
- nova coluna **Pending** antes de **PO**
- botão/fluxo para criar um novo card direto no Kanban
- **drag-and-drop no desktop** para mover cards entre colunas
- manutenção do fluxo mobile de mover card, usando o mesmo backend
- atualização automática do status/runtime quando o card muda de coluna

### Fluxo desejado
- Alan cria ideias direto em **Pending**
- PO puxa de **Pending** para **PO** quando for começar o planejamento
- depois o fluxo segue normal: DESIGN → Alan approval → DEV → QA → Alan homologation → Archived

### Pontos importantes
- o runtime/Kanban continua sendo a fonte operacional de verdade
- OpenSpec continua sendo criado/atualizado quando o trabalho entrar de fato no fluxo de planejamento
- a UI deve refletir a mudança de coluna automaticamente, sem reload manual

### Dúvida em aberto
- decidir se um card criado em `Pending` já gera um esqueleto OpenSpec imediatamente ou só quando PO puxar para planejamento
