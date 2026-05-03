## Why

O Monitor do usuário comum ainda expõe colunas técnicas que não ajudam na decisão principal. `7d` e `Distância` geram ruído, e o cabeçalho `Saída` não deixa claro que a coluna representa o estado atual do sinal.

## What Changes

- Ocultar as colunas `Distância` e `7d` para usuário comum.
- Ocultar a ordenação por `Distância` para usuário comum.
- Renomear o cabeçalho `Saída` para `Status`.
- Preservar informações técnicas no detalhe expandido e, quando aplicável, na experiência administrativa.

## Capabilities

### New Capabilities
- `monitor-common-user-table-columns`: tabela do Monitor simplificada para usuário comum.

### Modified Capabilities

## Impact

- Frontend: `frontend/src/components/monitor/MonitorStatusTab.tsx`.
- E2E: `frontend/tests/e2e/monitor-card-mode-and-portfolio.spec.ts`.
- Sem impacto em API, banco ou permissões backend.
