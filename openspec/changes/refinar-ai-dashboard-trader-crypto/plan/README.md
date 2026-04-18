# Plano de execução — AI Dashboard Trader Crypto

Esta pasta guarda o plano operacional da change `refinar-ai-dashboard-trader-crypto` em arquivos menores, um por card.

O plano foi sincronizado com os cards do Kanban multiprojeto no projeto `crypto` e agora segue a regra de entregas pequenas, verticais e já validadas no mesmo card.

## Ordem de execução recomendada

1. `01-excluir-stable-stable-da-vitrine.md`
2. `02-separar-primary-da-cobertura-adicional.md`
3. `03-ranking-deterministico-dos-primary.md`
4. `04-freshness-basico-por-fonte.md`
5. `05-conflito-entre-fontes-e-conviccao.md`
6. `06-actionability-com-fallback-contextual.md`
7. `07-actionability-detalhado-e-compatibilidade.md`

## Status atual

- Sincronizado com os cards `#97` a `#103` do Kanban
- Cada card já embute sua própria validação
- O card `07` deixou de ser um QA genérico e virou um fechamento leve de compatibilidade

## Mapa card -> spec

- `01` / `#97` -> `ai-dashboard-asset-curation` -> `Dashboard must exclude ineligible stable pairs from the primary view`
- `02` / `#98` -> `ai-dashboard-asset-curation` -> `Dashboard must separate primary opportunities from additional coverage`
- `03` / `#99` -> `ai-dashboard-asset-curation` -> `Dashboard must rank primary opportunities deterministically`
- `04` / `#100` -> `ai-dashboard-source-trust` -> `Unified signals must expose freshness metadata per source`
- `05` / `#101` -> `ai-dashboard-source-trust` -> `Final conviction must reflect source agreement, conflicts and stale inputs`
- `06` / `#102` -> `ai-dashboard-signal-actionability` -> `Unified signals must expose minimum actionability with explicit fallback`
- `07` / `#103` -> `ai-dashboard-signal-actionability` -> `Detailed actionability must only appear when supported and remain backward compatible`

## Regra de trabalho

- Cada arquivo representa uma entrega pequena e fechada, com backend/UI/teste do próprio escopo quando aplicável.
- Nenhum card deve depender de um QA final genérico para ser considerado pronto.
- A validação mínima do comportamento entregue deve acontecer no mesmo card.
- O card final existe apenas para compatibilidade, smoke integrado e regressão leve.
- A implementação continua guiada pelo OpenSpec principal desta change.
- Cada card deve apontar explicitamente para um requirement principal da spec e para os cenários que ele entrega ou valida.
