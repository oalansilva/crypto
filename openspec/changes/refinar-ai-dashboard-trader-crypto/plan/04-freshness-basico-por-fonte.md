# Card 4 — Freshness básico por fonte

## Objetivo

Adicionar um primeiro nível de transparência temporal por fonte, com leitura rápida e compatível com payload parcial.

## Spec touchpoints

- Kanban: card `#100`
- Capability: `ai-dashboard-source-trust`
- Requirement: `Unified signals must expose freshness metadata per source`
- Scenarios: `Source freshness is explicit`; `Freshness degrades safely when timing metadata is incomplete`

## Problema que este card resolve

Sem indicar se uma fonte está fresca ou envelhecida, o usuário vê sinais consolidados sem contexto temporal mínimo. Isso afeta confiança mesmo quando a direção do sinal parece correta.

## Escopo

- Expor `updated_at`, `age_seconds` e um estado curto como `fresh`, `aging` ou `stale`.
- Mostrar esse estado no detalhe por fonte.
- Exibir um badge ou marcador curto na UI.
- Garantir fallback seguro quando esses campos não existirem.

## Fora de escopo

- Conflito entre fontes.
- Convicção consolidada.
- Timeline ou histórico visual.

## Direção proposta

- Badge curto para `fresh`, `aging` e `stale`.
- Exibição prioritária no detalhe por fonte.
- Compatibilidade explícita com payload legado sem quebra da tela.

## Validação neste card

- Teste backend cobrindo pelo menos um caso `fresh` e um caso `stale`.
- Checagem UI ou E2E confirmando renderização correta dos badges.
- Verificação de fallback seguro quando os campos novos estiverem ausentes.

## Critérios de aceite

- O usuário identifica rapidamente se a fonte está fresca ou envelhecida.
- O payload legado não quebra a UI.
- A tela não exige interpretação técnica longa para entender freshness.

## Dependências

- Payload do dashboard com novos campos de freshness.
- Componentes do dashboard em `frontend/src/components/ai-dashboard/`

## Riscos

- Multiplicar estados visuais cedo demais.
- Quebrar a UI quando uma fonte vier sem timestamp utilizável.

## Mitigação

- Usar taxonomia curta e consistente.
- Tratar freshness como incremento opcional com fallback.

## Entregáveis esperados

- Campos básicos de freshness no payload.
- Badge curto de freshness por fonte.
- Validação do comportamento no mesmo card.
