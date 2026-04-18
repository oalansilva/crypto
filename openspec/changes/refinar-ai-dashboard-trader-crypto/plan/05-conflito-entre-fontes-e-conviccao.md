# Card 5 — Conflito entre fontes e convicção

## Objetivo

Explicitar quando as fontes convergem ou conflitam e refletir isso em uma faixa simples de convicção.

## Spec touchpoints

- Kanban: card `#101`
- Capability: `ai-dashboard-source-trust`
- Requirement: `Final conviction must reflect source agreement, conflicts and stale inputs`
- Scenarios: `Source alignment is explicit`; `High convergence raises conviction`; `Conflict or stale data lowers conviction with warning`

## Problema que este card resolve

Mesmo com freshness básico, ainda falta mostrar quando as fontes puxam em direções diferentes. Sem isso, o sinal consolidado pode parecer mais forte do que realmente é.

## Escopo

- Expor `agreement_to_final` por fonte.
- Expor `warnings` e `confidence_band` no consolidado.
- Mostrar alinhamento ou conflito na UI sem poluição excessiva.
- Reduzir convicção quando houver conflito relevante.

## Fora de escopo

- Actionability detalhado.
- Score numérico sofisticado.
- Redesenho completo do dashboard.

## Direção proposta

- Taxonomia curta para alinhamento, por exemplo `agree`, `partial` e `conflict`.
- `confidence_band` simples, legível e derivada do estado das fontes.
- Warning visível apenas quando impactar a decisão.

## Validação neste card

- Teste backend com um cenário alinhado e outro em conflito.
- Checagem UI ou E2E confirmando warning visível em caso de conflito.
- Verificação de que a convicção muda entre caso alinhado e caso conflitante.

## Critérios de aceite

- O payload deixa claro quando uma fonte conflita com o sinal final.
- O usuário percebe a diferença entre convergência e conflito.
- A convicção final não mascara conflito relevante.

## Dependências

- Freshness básico do card `04`.
- Fontes atualmente consolidadas no dashboard.

## Riscos

- Excesso de informação visual no card.
- Rótulos técnicos demais para leitura rápida.

## Mitigação

- Manter taxonomia curta.
- Concentrar detalhe extra no expandido.

## Entregáveis esperados

- Campos de alinhamento e convicção no payload.
- UI mostrando conflito ou convergência.
- Validação do comportamento no mesmo card.
