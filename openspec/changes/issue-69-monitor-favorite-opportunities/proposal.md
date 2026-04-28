# Proposal: Exibir apenas estratégias favoritas no Monitor (Issue #69)

## Why

Atualmente o Monitor já consulta estratégias favoritas, mas havia lacunas funcionais que
podiam ocultar estratégias favoritada quando:

- o `tier` era `none` (sem tier definido);
- o usuário tinha mais de uma estratégia para o mesmo ativo (deduplicação por símbolo).

Isso fazia o Monitor não refletir fielmente o que foi escolhido/favoritado no Backtest.

## What

Esta change garante que o Monitor exiba **apenas estratégias favoritas** (sem perder casos
sem tier), preservando variações por ativo/timeframe/estratégia e mantendo o comportamento
de refresh.

### Escopo do backend
- Ajustar filtro de tier para que `tier=all` e vazio não removam favoritos com `tier is null`.
- Manter escopo por usuário nas consultas (sem regressão de isolamento).
- Preservar cache por usuário e filtro de tier existente.

### Escopo do frontend
- Remover deduplicação agressiva por símbolo em `MonitorStatusTab`.
- Ajustar renderização do card para mostrar nome/estratégia com maior clareza.
- Garantir que a lista atualizável continue representando o conjunto real de favoritos.

## Out of Scope

- Mudanças de modelo de dados de favorito (nome/campos de strategy).
- Novas regras de seleção por carteira além do filtro atual do Monitor.

## Impact

- O Monitor passa a refletir fielmente todas as estratégias favoritas, inclusive sem tier.
- Múltiplas estratégias no mesmo ativo continuam visíveis.
- Refresh continua preservando a lista por usuário e filtro atual.
