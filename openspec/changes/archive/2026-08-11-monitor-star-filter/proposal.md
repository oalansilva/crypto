## Why

Usuários comuns agora veem estratégias classificadas por estrelas, mas ainda não conseguem reduzir a lista pela quantidade de estrelas. O Monitor precisa permitir foco rápido em estratégias de 3, 2 ou 1 estrela.

## What Changes

- Adicionar filtro visual de estrelas na tela do Monitor.
- Filtrar oportunidades carregadas por classificação `★★★`, `★★` ou `★`.
- Manter a classificação por tier existente: Tier 1 = 3 estrelas, Tier 2 = 2 estrelas, Tier 3 = 1 estrela.
- Não alterar contrato de API nem regras de tier do backend.

## Capabilities

### New Capabilities
- `monitor-star-filter`: filtro de oportunidades por quantidade de estrelas no Monitor.

### Modified Capabilities

## Impact

- Frontend: `frontend/src/components/monitor/MonitorStatusTab.tsx`.
- E2E: `frontend/tests/e2e/monitor-card-mode-and-portfolio.spec.ts`.
- Sem impacto em banco, API ou dependências.
