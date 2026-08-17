## Why

A chave de idempotência do sweep de Discovery usava `snapshot_hash` e o `payload_hash` não canonicalizava templates/símbolos/timeframes/direções. Retry de payload equivalente (ordem diferente) pode 409; “novo rascunho” pode reutilizar a chave do sweep anterior. O WIP já existe em `origin/card-469-idempotency-normalization-wip` (`a193bae0`); o #469 permanece Pronto e não será reaberto.

## What Changes

- Canonicalizar o hash do payload (templates/símbolos/timeframes/direções) no start.
- Mesma chave + payload equivalente (ordem diferente) retorna retry idempotente, não 409.
- A UI gera UUID por rascunho; “Novo rascunho” gera nova chave e o segundo start não reutiliza a chave anterior.
- Reaplicar o WIP numa branch `card-567-*` a partir de `develop`.
- Testes de integração + e2e do fluxo start/novo rascunho.
- Sincronizar spec `discovery-sweep`.
- UI impact: affected (start/retry/novo rascunho).

## Capabilities

### New Capabilities

Nenhuma. Comportamento novo fica no spec existente.

### Modified Capabilities

- `discovery-sweep`: hash canônico do payload e chave de idempotência por rascunho (não `snapshot_hash` cru).

## Impact

- `backend/app/services/discovery_service.py` (e testes de integração).
- `frontend/src/**/DiscoveryPage.tsx` (UUID por rascunho).
- e2e funcional do start/novo rascunho.
- Spec `openspec/specs/discovery-sweep`.
- Não reabre #469; não inclui workers PROD (#566).
