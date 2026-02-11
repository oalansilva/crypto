## UX / Estados

### Onde aparece
- `/lab` (criar run): inicia com uma pergunta do Trader quando faltar info.
- `/lab/runs/:run_id`: seção **Upstream (chat)** acima da execução.

### Estados
- `phase=upstream` e `status=needs_user_input`:
  - mostra histórico do chat
  - mostra a pergunta atual do Trader
  - input do humano + botão **Enviar**
- `phase=upstream` e `upstream_contract.approved=true`:
  - mostra o contrato upstream resumido
  - CTA **Iniciar execução**
- `phase=execution`:
  - upstream fica colapsado (mas acessível)
  - execução normal

### Copy
- Trocar “Validator” por **Trader** em todos os locais da UI.

## Modelo de dados (run JSON)

Adicionar/garantir estes campos:

```json
{
  "phase": "upstream" | "execution" | "done",
  "upstream": {
    "messages": [
      {"role":"user","text":"...","ts_ms":123},
      {"role":"trader","text":"...","ts_ms":124}
    ],
    "pending_question": "..." 
  },
  "upstream_contract": {
    "approved": false,
    "missing": ["..."],
    "question": "...",
    "inputs": { }
  }
}
```

## Backend flow (alto nível)

1) Ao criar run:
- roda `build_upstream_contract(context)`
- se aprovado: guarda contrato e não precisa conversar
- se bloqueado: chama o Trader para gerar `pending_question` (e salva no histórico)

2) POST /continue (ou endpoint dedicado de upstream message):
- recebe `user_message`
- adiciona no histórico
- chama Trader com o histórico + contexto para:
  - atualizar `upstream_contract` (missing/question/inputs)
  - produzir próxima pergunta (se ainda bloqueado)
- quando aprovado: UI mostra CTA para iniciar execução

## Observabilidade

- Adicionar trace events por turno:
  - `upstream_message` (role=user|trader)
  - `upstream_contract_updated`
  - `upstream_approved`
