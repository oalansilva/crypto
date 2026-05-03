## Context

O Monitor já renderiza tiers como estrelas para usuários comuns. O backend restringe a exposição a Tier 1, 2 e 3; o filtro solicitado é uma seleção local na lista carregada.

## Goals / Non-Goals

**Goals:**
- Permitir filtrar oportunidades por 3, 2 ou 1 estrela.
- Preservar os filtros existentes de lista, estratégia, timeframe e busca.
- Manter o comportamento sem recarregar a API ao trocar estrela.

**Non-Goals:**
- Não criar novo endpoint.
- Não mudar regras de tier, scoring ou normalização backend.
- Não alterar permissões de usuário comum/admin.

## Decisions

- Usar um `select` no toolbar atual do Monitor.
  - Racional: mantém consistência com filtros de estratégia/timeframe e evita aumentar a densidade visual com mais botões segmentados.
- Filtrar pela quantidade de caracteres retornada por `getTierStars`.
  - Racional: reutiliza a regra já centralizada de Tier 1/2/3 para estrelas e reduz duplicação.
- Aplicar o filtro após estratégia/timeframe e antes da busca textual.
  - Racional: mantém ordem previsível dos filtros e permite a busca atuar apenas sobre o subconjunto visível.

## Risks / Trade-offs

- [Risk] Estratégias sem tier não aparecem ao escolher estrelas.
  - Mitigation: opção padrão "Todas" preserva comportamento atual.
- [Risk] Teste E2E pode ficar frágil se payload mock mudar.
  - Mitigation: usar payload existente com BTC Tier 1 e ETH Tier 2.
