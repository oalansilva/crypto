# Proposal: Card do Monitor — risco explícito (card #792)

## Why

Tester do beta não consegue calibrar "quanto pode doer" porque o card mostra Compra/Venda e preço mas omite stop/alvo/distância ou ressuscita Entry/Stop mortos em EXIT sem explicar o risco residual — sem isso o Farol vira sinal, não farol. É P0 do roteiro #75 "contexto/histórico → risco": sem distância relevante, stop/alvo e frase de cenário de erro o tester não calibra tamanho de posição nem decide se abre o gráfico sem achar que o Farol executa ordem.

## What Changes

- Hierarquia no card: estado (Compra/Venda via `resolveOpportunitySignal`) → distância relevante → stop/alvo (ou "indisponível — dado não confiável").
- Quando `is_holding=true` + `stop_price`/`entry_price`/`distance_to_stop_pct` no payload (top-level `opportunity.*` já derivados no backend): distância + stop + alvo visíveis **sem abrir o gráfico**.
- Quando dado ausente/não confiável (null/undefined/stale): campo mostra `indisponível — dado não confiável` — nunca omite em silêncio nem inventa placeholder/número de outra timeframe.
- Frase de cenário de erro ("se o preço cruzar X, a leitura de posição deixa de valer") só quando houver dado comprovado (`stop_price` do payload ou invalidação de `signal_history`).
- EXIT: não mostrar Entry/Stop como operáveis; mostrar "posição encerrada segundo a estratégia — sem risco residual mapeado" quando `signal_history` vazio, ou risco residual quando houver.
- Usar `Compra/Venda` no badge (resolveOpportunitySignal). Formatação em USD e % com 2 casas reusando `toDisplayValue`/`priceString` de `OpportunityCard.tsx`.
- Quando `is_strategy_protected=true`, card não vaza `parameters`/`indicator_values` — risco mostra apenas `stop_price`/`entry_price` top-level (público/derivado seguro).
- Coerência com modal do gráfico para o mesmo payload.

## Capabilities

### New Capabilities

_Nenhuma capability nova. Mudança é de comportamento visível dentro de capability existente._

### Modified Capabilities

- `opportunity-monitor`: estende display de HOLD/EXIT para incluir risco explícito (distância, stop, alvo, indisponível, frase de cenário, risco residual), sem criar terceiro status visível.

## Impact

- Frontend: `frontend/src/components/monitor/OpportunityCard.tsx`, `types.ts`, `signalResolution.ts`, `ChartModal.tsx`/`MonitorStatusTab.tsx` (coerência do badge e da distância), `frontend/src/lib/strategyTransparency.ts` (já seguro para risco).
- Backend: sem mudança de contrato — `opportunity_service.py` já entrega `entry_price`/`stop_price`/`distance_to_stop_pct`/`signal_history`/`is_holding` top-level; `strategy_secret_visibility.py` já redige `parameters`/`indicator_values` para `is_strategy_protected`.
- Spec: `openspec/specs/opportunity-monitor/spec.md`.
- Não entra: dimensionamento/Kelly, colocar stop na Binance, métricas completas de backtest, alertas Telegram (#747), automação TP/SL/trailing, backfill com placeholder/outra timeframe.
