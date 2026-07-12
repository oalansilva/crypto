## Why

O saneamento de caches futuros passou a descartar históricos válidos quando o payload guarda apenas candles recentes e a impedir regeneração quando a chave `trades` não existe. A suíte completa detectou a regressão antes da release.

## What Changes

- Validar apenas o limite superior conhecido da cobertura ao sanear trades históricos.
- Preservar a ausência da chave `trades` para manter o fluxo de regeneração.
- Cobrir caches resumidos, catálogo protegido e reconstrução de métricas.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `monitor`: corrigir a leitura segura de caches históricos parciais sem apagar trades válidos.

## Impact

- Backend: `backend/app/routes/favorites.py` e testes de favoritos.
- Runtime: DEV e pacote de release 2026-07-12.
