## Data model

Adicionar ao run JSON:

```json
{
  "phase": "upstream" | "execution" | "done",
  "upstream": {
    "messages": [...],
    "pending_question": "...",
    "strategy_draft": {
      "version": 1,
      "one_liner": "...",
      "rationale": "...",
      "indicators": [
        {"source":"pandas_ta","name":"bbands","params":{"length":20,"std":2}},
        {"source":"pandas_ta","name":"rsi","params":{"length":14}}
      ],
      "entry_idea": "...",
      "exit_idea": "...",
      "risk_plan": "...",
      "what_to_measure": ["sharpe_holdout", "max_drawdown_holdout", "min_trades"],
      "open_questions": ["..."]
    },
    "ready_for_user_review": false,
    "user_approved": false,
    "user_feedback": "..."
  }
}
```

## Trader output contract (JSON)

O Trader deve responder JSON com:
- `reply`: texto curto
- `inputs`: symbol/timeframe/objective
- `constraints`: constraints atualizadas (se aplicável)
- `strategy_draft`: objeto conforme acima (quando tiver info suficiente)
- `ready_for_user_review`: boolean

## UX

### Upstream chat
- Continua conversando até `ready_for_user_review=true`.
- Quando pronto, a UI mostra um card **Proposta do Trader**:
  - One-liner + rationale
  - Indicadores sugeridos (nome + params)
  - Entry/exit/risk em linguagem natural
  - “O que vamos medir”

### Aprovação
- Botão: **Aprovar e iniciar execução**
- Campo de texto: **Quero ajustar** → envia feedback ao Trader e ele revisa o draft.

## Downstream

- A execução só inicia se `upstream.user_approved=true`.
- O downstream usa `upstream.strategy_draft.indicators` como base para montar a estratégia candidata.
  - Se algum indicador não for suportado pelo engine: retornar erro amigável no upstream e pedir ajuste (sem iniciar execução).
