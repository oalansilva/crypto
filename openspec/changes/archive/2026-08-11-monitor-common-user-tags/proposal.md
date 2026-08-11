## Why

As tags `Portfolio` e `Strategy` na tabela do Monitor não estão claras para usuário comum. `Portfolio` deve aparecer em português como carteira, e `Strategy` não adiciona informação útil na linha comum.

## What Changes

- Trocar a tag `Portfolio` por `Carteira`.
- Remover a tag `Strategy` da tabela para usuário comum.
- Manter a classificação por estrelas visível.
- Preservar a tag técnica `Strategy` para admin, se necessário para operação.

## Capabilities

### New Capabilities
- `monitor-common-user-tags`: tags da tabela do Monitor mais claras para usuário comum.

### Modified Capabilities

## Impact

- Frontend: `frontend/src/components/monitor/MonitorStatusTab.tsx`.
- E2E: `frontend/tests/e2e/monitor-card-mode-and-portfolio.spec.ts`.
- Sem impacto em API, banco ou permissões backend.
