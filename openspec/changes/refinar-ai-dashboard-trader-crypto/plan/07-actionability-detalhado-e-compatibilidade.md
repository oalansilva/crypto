# Card 7 — Actionability detalhado e compatibilidade

## Objetivo

Completar o `actionability` com os campos detalhados restantes e fechar a iteração com uma regressão integrada leve, não com um QA genérico separado.

## Spec touchpoints

- Kanban: card `#103`
- Capability: `ai-dashboard-signal-actionability`
- Requirement: `Detailed actionability must only appear when supported and remain backward compatible`
- Scenarios: `Detailed actionability fields are populated only with explicit backing`; `UI shows detailed execution context without fabrication`; `Dashboard remains compatible with partial or legacy payloads`

## Problema que este card resolve

Depois do `actionability` mínimo, ainda falta enriquecer o contexto operacional quando houver origem confiável. Também é preciso garantir que payload parcial ou legado continue funcionando após os incrementos anteriores.

## Escopo

- Completar campos como `timeframe`, `entry_zone`, `invalidation_level`, `target_level` e `risk_label` quando houver base explícita.
- Manter `unavailable_reason` nos casos sem base suficiente.
- Validar compatibilidade com payload parcial ou legado.
- Rodar um smoke final da tela cobrindo os estados principais já entregues.

## Fora de escopo

- Campanha ampla de QA manual separada.
- Teste de carga.
- Histórico de performance do sinal.

## Validação neste card

- Testes backend cobrindo preenchimento dos campos detalhados apenas quando houver origem confiável.
- Checagem UI ou E2E com um caso detalhado e um caso ainda contextual.
- Smoke final confirmando que payload parcial ou legado não quebra a tela.

## Critérios de aceite

- Campos detalhados aparecem somente quando suportados pelo payload.
- Sinais sem base suficiente continuam com fallback claro.
- O dashboard continua funcionando com payload parcial ou legado.

## Dependências

- Conclusão funcional dos cards `01` a `06`.
- Ambiente com backend e frontend disponíveis para smoke final.

## Riscos

- Introduzir precisão artificial em campos detalhados.
- Transformar este card em um “qa final de tudo” novamente.

## Mitigação

- Só preencher campo detalhado com origem explícita.
- Manter este card focado em compatibilidade e fechamento leve.

## Entregáveis esperados

- Campos detalhados de `actionability` quando suportados.
- Testes do comportamento detalhado e dos fallbacks.
- Smoke final de compatibilidade do dashboard.
