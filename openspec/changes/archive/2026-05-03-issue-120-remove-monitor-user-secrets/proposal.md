## Why

O detalhe expandido do Monitor ainda mostra blocos técnicos de `Parâmetros` e `Indicadores` para usuário comum. Esses dados ajudam a copiar a lógica da estratégia e devem ficar visíveis apenas para administrador.

## What Changes

- Ocultar os blocos `Parâmetros` e `Indicadores` no detalhe expandido do Monitor para usuário comum quando a oportunidade estiver protegida.
- Ocultar ações e controles técnicos do detalhe expandido para usuário comum quando a oportunidade estiver protegida.
- Mostrar apenas o timeframe da estratégia no detalhe protegido, sem seletor de timeframe alternativo.
- Manter esses blocos visíveis para administrador.
- Preservar nome público da estratégia, status, preço, risco, notas operacionais e ações do Monitor para usuário comum.

## Capabilities

### New Capabilities
- `monitor-common-user-detail-secrets`: detalhe expandido do Monitor protege dados técnicos para usuário comum.

### Modified Capabilities

## Impact

- Frontend: `frontend/src/components/monitor/OpportunityCard.tsx`.
- Frontend: `frontend/src/components/monitor/MonitorStatusTab.tsx`.
- Sem alteração em API, banco ou regra de cálculo.
