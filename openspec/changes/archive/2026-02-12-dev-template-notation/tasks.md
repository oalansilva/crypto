# Tasks: Dev Template Notation (auto-correção)

**Change:** dev-template-notation  
**Estimated:** ~2h  
**Priority:** high

---

## ✅ Tarefas

1. Atualizar `DEV_SENIOR_PROMPT`
   - Requerer lógica booleana válida
   - Proibir texto livre
   - Exigir `stop_loss` float
   - Instruir auto-correção

2. Rodar testes
   - `./backend/.venv/bin/python -m pytest -q`

---

## ✅ Critérios de Aceite

- Dev retorna apenas lógica válida
- stop_loss sempre numérico
- auto-correção aplicada quando inválido
