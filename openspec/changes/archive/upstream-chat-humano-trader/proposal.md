## Why

Hoje o **Upstream** do Lab é essencialmente um *preflight/contrato* automático (aprovado/bloqueado), o que não entrega a experiência desejada: uma conversa que ajude o humano a esclarecer objetivos, restrições e risco antes de gastar custo de execução.

Queremos que o Upstream seja um **chat Humano ↔ Trader** (a persona hoje chamada `validator`), no estilo ChatGPT, para:
- Clarificar inputs (símbolo, timeframe, janela, direção, objetivo)
- Negociar constraints (max drawdown, min sharpe, nº mínimo de trades, etc.)
- Explicar trade-offs e riscos
- Produzir um **upstream_contract** explícito, aprovado pelo humano

## What Changes

- Transformar o Upstream em um **fluxo conversacional** com histórico persistido no run.
- Renomear na UI/copy a persona `validator` para **Trader** (sem necessariamente mudar o id interno no backend de primeira).
- A execução (downstream) só começa quando:
  - `upstream_contract.approved == true`
  - e o humano confirmar (CTA)

## Capabilities

### New Capabilities
- `lab-upstream-chat`: chat upstream com histórico + contrato.

### Modified Capabilities
- `lab-run-page`: exibir chat upstream e estado (needs_user_input) claramente.
- `lab-run-api`: retornar histórico upstream + contrato + fase.

## Impact

- Backend: `backend/app/routes/lab.py` + serviços de upstream (persistência do histórico no JSON do run)
- Frontend: `/lab` e `/lab/runs/:run_id` para renderizar upstream como conversa e coletar input do humano.
- Trace: eventos por turno (ex.: `upstream_turn`, `upstream_message`) para permitir auditoria e UI.

## Out of scope

- Multi-tenant/auth.
- Memory longa entre runs (o histórico é por run).
- Ferramentas de automação de browser.
