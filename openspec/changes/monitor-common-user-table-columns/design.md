## Context

O Monitor já diferencia usuários comuns de administradores por autenticação. A solicitação afeta apenas a leitura da tabela principal para o usuário comum.

## Goals / Non-Goals

**Goals:**
- Reduzir ruído visual da tabela principal para usuário comum.
- Manter a coluna final com nome claro (`Status`).
- Evitar mudança de contrato backend.

**Non-Goals:**
- Não remover dados do payload.
- Não alterar regra de scoring, tier ou status.
- Não refatorar o layout completo do Monitor.

## Decisions

- Usar `useAuth()` no componente para identificar admin.
  - Racional: padrão já existente no frontend para diferenciar usuário comum/admin.
- Renderizar `Distância` e `7d` apenas para admin.
  - Racional: preserva ferramentas técnicas para operação/admin e simplifica usuário comum.
- Renomear o cabeçalho final para `Status`.
  - Racional: descreve melhor o badge exibido na célula.

## Risks / Trade-offs

- [Risk] Mudança de quantidade de colunas quebra linha expandida.
  - Mitigation: calcular `colSpan` conforme as colunas visíveis.
- [Risk] Teste E2E depender demais do texto da tabela.
  - Mitigation: testar somente cabeçalhos relevantes para usuário comum.
