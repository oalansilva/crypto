# Specification: Issue #69 — Listar estratégias favoritas no Monitor

## Requisitos

- O endpoint de oportunidades do Monitor deve retornar apenas estratégias favoritas do usuário autenticado.
- O filtro `tier=all` deve incluir também favoritos com `tier IS NULL`.
- O filtro `tier=none` deve retornar somente favoritos com `tier IS NULL`.
- O filtro `tier` vazio/nulo deve manter contrato atual (sem filtro implícito por tier).

## Persistência e desempenho
- Refresh com `refresh=true` continua forçando recomputação.
- O cache permanece por `(user_id, tier)` para evitar mistura entre modos de filtro.

## Renderização no Monitor
- Não pode haver deduplicação por símbolo que remova estratégias concorrentes com mesmo ativo.
- Cada cartão deve exibir ativo, timeframe e estratégia correspondentes sem sobreposição.

## Critérios de aceite

1. Com entradas de `tier=all` contendo `tier=1,2,3,null`, o Monitor renderiza todas as estratégias.
2. Ao trocar refresh, a lista permanece as mesmas estratégias de favorito.
3. Com duas estratégias no mesmo ativo, ambas aparecem como cards distintos.

## Cenários

### Scenario: exibir favoritos com `tier=all`
- **Given** um usuário com favoritos em `tier=1`, `tier=2`, `tier=3` e `tier=null`;
- **When** consulta `GET /api/opportunities/?tier=all`;
- **Then** a resposta inclui todos os itens favoritos;
- **And** não inclui estratégias de outros usuários.

### Scenario: listar múltiplas estratégias por símbolo
- **Given** dois favoritos com `symbol=BTC/USDT` e estratégias diferentes;
- **When** o Monitor renderiza a lista;
- **Then** ambos os cards aparecem no resultado (sem deduplicação por símbolo).

### Scenario: refresh preserva lista
- **Given** uma lista não vazia de favoritos;
- **When** o usuário aciona Refresh;
- **Then** o Monitor mantém o mesmo escopo de cartões favoritados.
