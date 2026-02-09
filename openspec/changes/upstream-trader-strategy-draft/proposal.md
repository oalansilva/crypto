## Why

O upstream atual ainda está muito focado em coletar campos (symbol/timeframe/constraints) e não entrega o valor principal: o **Trader** deveria propor uma **ideia de estratégia** e sugerir **indicadores** para o humano validar antes de gastar custo rodando backtests.

Queremos um upstream **LLM-first e fluido**, onde o Trader:
1) entende objetivo/risco/constraints
2) produz um **Strategy Draft** (resumo + proposta)
3) sugere indicadores (preferencialmente da lib **pandas_ta**)
4) pede **aprovação do humano**
5) só então inicia a execução (downstream)

## What Changes

- No upstream, introduzir um artefato persistido por run: `upstream.strategy_draft`.
- O Trader passa a retornar no JSON:
  - `strategy_draft` (resumo, indicadores sugeridos, entry/exit em linguagem natural, plano de risco, o que medir)
  - `ready_for_user_review: true` quando já tiver informação suficiente
- UI mostra o draft e oferece CTA:
  - **Aprovar e iniciar execução**
  - Campo de texto: “ajustes desejados” (volta para o Trader gerar uma versão revisada)

## Capabilities

### New Capabilities
- `lab-upstream-strategy-draft`: draft de estratégia + indicadores sugeridos pelo Trader.

### Modified Capabilities
- `lab-upstream-chat`: adicionar etapa de review/aprovação do draft.
- `lab-downstream-start`: execução só inicia após aprovação explícita.

## Scope / Guardrails

- Modo escolhido: **Sugestão + aprovação** (mais seguro).
- Indicadores: permitir sugestões baseadas em **pandas_ta**; se algum indicador não for suportado pelo engine atual, o sistema deve:
  - ou mapear para o equivalente suportado,
  - ou registrar como “não suportado” e pedir ajuste (sem travar em loop).

## Out of scope

- Gerar código final de estratégia “perfeita” no upstream.
- Multi-tenant/auth.
