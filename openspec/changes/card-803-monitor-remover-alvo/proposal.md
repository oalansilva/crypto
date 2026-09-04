## Why

No Monitor em HOLD, o campo **alvo** parece preço de operação, mas é só uma estimativa no frontend (`preço atual × (1 ± distância até a saída)`). O produto não opera take-profit. Esse número compete com stop e distâncias — o risco real — e quebra a confiança no beta. O #792 pediu risco explícito e a implementação mostrou alvo derivado; este card corrige: HOLD mostra risco sem fingir TP.

## What Changes

- **BREAKING (spec `opportunity-monitor`):** HOLD deixa de mostrar `alvo` (rótulo e valor) no card do Monitor e no modal do gráfico. A spec deixa de exigir `alvo` no bloco de risco.
- Remover o cálculo e o estado morto do alvo derivado no frontend (`OpportunityCard` / `ChartModal`). Sem linha escondida, tooltip ou número equivalente com outro nome.
- Em HOLD, a ordem visível fica: `distância até saída` → `distância até stop` → `stop` → `entrada` → `preço atual`.
- Manter, sem mudar copy nem regra: `indisponível — dado não confiável` quando o dado for null/stale; a frase `Se o preço cruzar $X…` quando o stop for confiável; em EXIT, `preço atual` + bloco `Risco residual`.
- Card e modal da mesma oportunidade permanecem iguais.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `opportunity-monitor`: o requisito “Monitor card shows explicit risk for HOLD” deixa de mandar mostrar `alvo`; cenários e coerência card↔modal passam a tratar o recorte sem alvo derivado.

## Impact

- Frontend: `frontend/src/components/monitor/OpportunityCard.tsx` e `ChartModal.tsx` (cálculo `alvoPrice`/`chartAlvoPrice` e linhas do kv). Sem campo `alvo` no backend.
- Spec canónica `openspec/specs/opportunity-monitor/spec.md` (senão o Apply reintroduz o campo).
- Testes e2e/unitários que ainda afirmam a linha `alvo` no HOLD.
- Protótipo clone+delta da rota viva `/monitor` (não o proto #792, que vira anti-referência).
- Sem mudança de API, Telegram, Kelly, take-profit, ou ordem na corretora.
