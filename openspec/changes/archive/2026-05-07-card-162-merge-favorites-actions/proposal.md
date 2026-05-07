## Why

Na tela de Favoritos, `View Trades` e `View Results` criam duas entradas muito parecidas para analisar a mesma estrategia. Isso duplica a decisao do usuario e dificulta o fluxo principal de revisar resultado consolidado e historico de trades.

## What Changes

- Mesclar as acoes de trades e resultados em uma unica entrada clara na tela de Favoritos.
- Preservar o modal/fluxo que mostra resultado consolidado da estrategia.
- Incorporar a visualizacao de trades no mesmo fluxo, incluindo regeneracao quando o historico salvo estiver ausente.
- Remover ou ocultar a acao redundante para que cada favorito tenha apenas um CTA analitico principal.

## Capabilities

### New Capabilities

### Modified Capabilities
- `favorites`: a tela de Favoritos deve oferecer um unico fluxo para ver resultados consolidados e trades da estrategia favorita.

## Impact

- Frontend da tela de Favoritos e seus modais/controles.
- Testes E2E de Favoritos relacionados a resultados e trades.
- Sem mudanca planejada no contrato de API; o frontend deve reaproveitar endpoints existentes de resultados/trades/regeneracao.
