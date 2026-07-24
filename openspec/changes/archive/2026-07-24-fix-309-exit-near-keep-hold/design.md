## Context

`_public_monitor_status` inclui `EXIT_NEAR` no conjunto que força `EXIT`, sobrescrevendo `is_holding=True`. O spec de Monitor já classifica `EXIT_NEAR` como HOLD-compatible.

## Goals / Non-Goals

**Goals:**
- Posição aberta + `EXIT_NEAR` → público `HOLD` / `is_holding=true` / badge Compra (long).
- `EXIT_SIGNAL`, `EXITED`, stop e saídas reais continuam `EXIT`.

**Non-Goals:**
- Mudar regra de entrada/saída da estratégia multi_ma.
- Alterar alertas Telegram além do efeito do status público.

## Decisions

1. Remover `EXIT_NEAR` do conjunto que força `EXIT` quando `is_holding` é verdadeiro.
2. Em `_public_monitor_message`, se status público é `HOLD` e análise interna é `EXIT_NEAR`, usar copy de hold com distância de saída (sem “fora de posição”).
3. Manter `EXIT_SIGNAL` como `EXIT` (saída acionável confirmada na proximidade).

## Risks / Trade-offs

- Cards que estavam em seção Venda só por `EXIT_NEAR` voltam para Compra — comportamento desejado.
- Distância de saída continua no payload para o usuário acompanhar.
