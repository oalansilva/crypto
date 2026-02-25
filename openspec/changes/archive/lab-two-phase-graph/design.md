## Overview

Implementar um grafo único com duas etapas e branch (LangGraph):

1) **Upstream**
   - papéis: humano (via UI `/lab`) + trader/validator
   - saída: `upstream_contract`
   - se `approved=false`: retorna `needs_user_input` e interrompe execução

2) **Implementation + tests**
   - executa implementação (persona dev_senior/coordinator se aplicável)
   - roda testes determinísticos
   - produz decisão final

## State shape

Adicionar ao estado do Lab:
- `upstream_contract: { approved, missing, question, inputs, objective, acceptance_criteria, risk_notes }`
- `phase: 'upstream' | 'implementation' | 'tests' | 'done'`

Persistência:
- `run.json` deve conter `upstream_contract` e `phase` para retomada.

## Branching

No grafo:
- Node `upstream` sempre roda primeiro.
- Condição:
  - se `upstream_contract.approved`: segue para `implementation`
  - se não aprovado: termina com estado que leva o run para `needs_user_input`

Retomada:
- endpoint `/api/lab/runs/{id}/continue` deve reinvocar o grafo a partir do upstream (reavaliando inputs).

## Events

Adicionar eventos no trace:
- `upstream_started`, `upstream_done`
- `implementation_started`, `implementation_done`
- `tests_started`, `tests_done`
- `final_decision`

## Tests

- Unit/route tests cobrindo:
  - missing inputs → needs_user_input + question
  - upstream aprovado → etapa 2 executa e marca phase/status
