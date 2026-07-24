## Why

O Monitor/gráfico mostrava **Venda** para BTC multi_ma ainda em posição aberta: `EXIT_NEAR` (saída próxima) era mapeado para status público `EXIT` e `is_holding=false`.

## What Changes

- `_public_monitor_status`: com `is_holding=true`, `EXIT_NEAR` permanece `HOLD`.
- Mensagem pública de hold próximo da saída não usa copy “EXIT:/fora de posição”.
- Testes unitários cobrindo o contrato.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `monitor`: reforçar que `EXIT_NEAR` com posição aberta permanece HOLD/Compra no contrato público binário.

## Impact

- Backend: `opportunity_service._public_monitor_status` / `_public_monitor_message`
- UI Monitor/ChartModal (badge Compra/Venda) via payload público
- Sem mudança de schema de API além do valor correto de `status`/`is_holding`
