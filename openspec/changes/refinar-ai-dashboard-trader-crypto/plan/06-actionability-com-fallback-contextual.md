# Card 6 — Actionability com fallback contextual

## Objetivo

Introduzir o primeiro nível de `actionability` sem inventar precisão e distinguindo claramente setup acionável de leitura contextual.

## Spec touchpoints

- Kanban: card `#102`
- Capability: `ai-dashboard-signal-actionability`
- Requirement: `Unified signals must expose minimum actionability with explicit fallback`
- Scenarios: `Minimum actionability is populated from available source data`; `Actionability degrades explicitly when data is missing`; `UI shows minimum execution context for actionable signals`; `UI shows informative fallback for non-actionable signals`

## Problema que este card resolve

Hoje todos os sinais parecem ter o mesmo grau de prontidão. Falta dizer quando existe base operacional mínima e quando o sinal serve apenas como contexto.

## Escopo

- Introduzir um bloco `actionability` mínimo no payload.
- Exibir resumo curto quando houver base operacional suficiente.
- Exibir fallback contextual quando não houver base segura.
- Usar `unavailable_reason` quando o bloco não puder ser preenchido.

## Fora de escopo

- Campos detalhados como alvo, invalidação e risco fino.
- Simulação de trade.
- Recomendação financeira.

## Direção proposta

- Primeiro passo curto: `acionável` vs `contextual`.
- Se não houver base segura, mostrar claramente que o sinal é apenas contextual.
- A UI não deve parecer mais precisa do que o payload suporta.

## Validação neste card

- Teste backend com um caso que retorne `actionability` mínimo e outro que retorne fallback.
- Checagem UI ou E2E confirmando distinção visual entre acionável e contextual.
- Verificação de uso de `unavailable_reason` quando faltar base.

## Critérios de aceite

- O usuário diferencia rapidamente sinal acionável de sinal contextual.
- O fallback não aparece como campo vazio ou quebrado.
- O produto não fabrica precisão indevida.

## Dependências

- Payload mínimo de `actionability`.
- Componentes de card e detalhes do dashboard.

## Riscos

- Transformar um fallback em mensagem ambígua.
- Passar sensação de recomendação automática.

## Mitigação

- Manter texto curto e explícito.
- Usar linguagem de contexto, não de instrução.

## Entregáveis esperados

- Bloco mínimo de `actionability`.
- UI distinguindo `acionável` e `contextual`.
- Validação do comportamento no mesmo card.
