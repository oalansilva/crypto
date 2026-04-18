# Card 2 — Separar primary da cobertura adicional

## Objetivo

Separar claramente a vitrine principal dos ativos adicionais, sem depender de um ranking sofisticado neste momento.

## Spec touchpoints

- Kanban: card `#98`
- Capability: `ai-dashboard-asset-curation`
- Requirement: `Dashboard must separate primary opportunities from additional coverage`
- Scenarios: `Primary and secondary tiers are explicit in the payload`; `Additional coverage remains accessible without mixing with the primary list`

## Problema que este card resolve

Mesmo removendo os casos mais ruidosos, o dashboard continua confuso se todos os ativos válidos disputarem o mesmo espaço visual. Falta uma divisão explícita entre o que é destaque principal e o que é apenas cobertura adicional.

## Escopo

- Expor `primary`, `secondary` e `excluded` no payload.
- Expor `tier_reason` ou equivalente.
- Mostrar `primary` na vitrine principal.
- Mostrar `secondary` em uma seção separada com contagem visível.

## Fora de escopo

- Ranking fino dentro dos `primary`.
- Trust/freshness detalhado por fonte.
- Actionability do sinal.

## Direção proposta

- Começar pela separação estrutural, não pela ordenação perfeita.
- `primary` concentra o que merece primeira dobra.
- `secondary` continua acessível, mas fora da vitrine principal.

## Validação neste card

- Teste de payload confirmando tiers corretos para exemplos de `primary`, `secondary` e `excluded`.
- Checagem UI ou E2E confirmando a separação entre vitrine principal e cobertura adicional.
- Verificação de contagem ou indicador visível de ativos fora da vitrine.

## Critérios de aceite

- A UI distingue claramente `primary` de cobertura adicional.
- O payload informa tier e motivo.
- Um ativo `secondary` não aparece misturado com a vitrine principal.

## Dependências

- Exclusão mínima do card `01`.
- Payload unificado atual do dashboard.

## Riscos

- Definir tiers amplos demais e manter a vitrine poluída.
- Empurrar a decisão de tier para o frontend.

## Mitigação

- Começar com regra simples e auditável.
- Backend decide o tier; UI apenas exibe.

## Entregáveis esperados

- Payload com `tier` e `tier_reason`.
- UI com seção principal e seção de cobertura adicional.
- Validação do comportamento no mesmo card.
