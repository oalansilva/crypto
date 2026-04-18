# Card 3 — Ranking determinístico dos primary

## Objetivo

Ordenar os ativos `primary` com uma regra simples, estável e explicável.

## Spec touchpoints

- Kanban: card `#99`
- Capability: `ai-dashboard-asset-curation`
- Requirement: `Dashboard must rank primary opportunities deterministically`
- Scenarios: `Primary opportunities are ordered by deterministic relevance`; `Deterministic ranking has a stable tiebreaker`

## Problema que este card resolve

Depois que a vitrine principal é separada, ainda falta definir qual ativo aparece primeiro. Sem uma regra estável, a lista pode parecer arbitrária e perder credibilidade.

## Escopo

- Ordenar apenas os ativos `primary`.
- Definir poucos fatores de ordenação.
- Garantir desempate estável.
- Expor um motivo resumido de posicionamento quando fizer sentido.

## Fora de escopo

- Trust/freshness detalhado por fonte.
- Modelagem avançada de score.
- Ordenação personalizada por usuário.

## Direção proposta

- Regra curta e auditável, por exemplo combinando prioridade de mercado e sinal consolidado disponível.
- Desempate previsível para evitar reorder arbitrário.
- O frontend não replica a regra.

## Validação neste card

- Teste backend provando que a mesma entrada gera a mesma ordenação.
- Teste cobrindo desempate estável.
- Checagem UI simples confirmando que o topo da vitrine segue a ordem do payload.

## Critérios de aceite

- A mesma entrada gera a mesma ordem.
- A regra é explicável sem depender de heurística escondida na UI.
- A vitrine principal respeita a ordenação do backend.

## Dependências

- Tiering do card `02`.
- Payload atual do dashboard.

## Riscos

- Tentar resolver o ranking perfeito cedo demais.
- Criar regra instável entre cargas parecidas.

## Mitigação

- Manter poucos fatores.
- Fixar desempate determinístico.

## Entregáveis esperados

- Ordenação determinística dos `primary`.
- Campo opcional de apoio à explicação do ranking.
- Validação do ranking no mesmo card.
