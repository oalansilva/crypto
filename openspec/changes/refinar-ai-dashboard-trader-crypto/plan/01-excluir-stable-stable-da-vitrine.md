# Card 1 — Excluir stable/stable da vitrine

## Objetivo

Eliminar o ruído mais óbvio do `AI Dashboard` removendo pares `stablecoin/stablecoin` da vitrine principal.

## Spec touchpoints

- Kanban: card `#97`
- Capability: `ai-dashboard-asset-curation`
- Requirement: `Dashboard must exclude ineligible stable pairs from the primary view`
- Scenarios: `Stablecoin versus stablecoin pairs are excluded from the primary list`; `Exclusion reasons are inspectable for ineligible pairs`

## Problema que este card resolve

Hoje o dashboard ainda pode destacar ativos que não ajudam a tomada de decisão de trading. O caso mais evidente é `stablecoin/stablecoin`, que enfraquece a percepção de qualidade logo na primeira leitura.

## Escopo

- Detectar pares `stablecoin/stablecoin` no agregador.
- Marcá-los como inelegíveis para a vitrine principal.
- Garantir que a UI não exiba esses ativos na lista principal.
- Introduzir um motivo simples de exclusão no payload para auditoria.

## Fora de escopo

- Curadoria completa de todos os demais ativos.
- Separação entre `primary` e `secondary`.
- Ranking entre ativos elegíveis.

## Direção proposta

- Regra mínima e objetiva: par `stablecoin/stablecoin` não entra na vitrine.
- O motivo da exclusão deve aparecer de forma explícita no payload.
- A UI deve simplesmente respeitar essa exclusão, sem heurística paralela.

## Validação neste card

- Teste backend cobrindo ao menos um par `stablecoin/stablecoin` elegível hoje e verificando exclusão.
- Checagem UI ou E2E confirmando que o ativo não aparece na lista principal.
- Verificação de que o payload informa a razão da exclusão.

## Critérios de aceite

- Par `stablecoin/stablecoin` não aparece na vitrine principal.
- O backend informa o motivo da exclusão.
- A UI não reintroduz o ativo por erro de renderização ou fallback.

## Dependências

- Agregador unificado em `backend/app/routes/ai_dashboard.py`
- Lista atual em `frontend/src/pages/AIDashboardPage.tsx`

## Riscos

- Tratar apenas esse caso e deixar a impressão de curadoria completa.
- Criar uma regra implícita no frontend e outra no backend.

## Mitigação

- Assumir este card como primeira limpeza, não a curadoria inteira.
- Centralizar a regra no backend e só consumi-la na UI.

## Entregáveis esperados

- Regra de exclusão de `stablecoin/stablecoin`.
- Motivo de exclusão no payload.
- Validação automatizada ou semiautomatizada do comportamento.
