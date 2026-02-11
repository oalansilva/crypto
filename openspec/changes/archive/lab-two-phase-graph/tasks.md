## 1. Upstream contract + branch

- [x] 1.1 Estender `backend/app/services/lab_graph.py` para incluir um node `upstream` que produz `upstream_contract`.
- [x] 1.2 Implementar branch no grafo: se `upstream_contract.approved==true` avança; senão pausa com `needs_user_input`.
- [x] 1.3 Persistir `upstream_contract` e `phase` no run JSON.
- [x] 1.4 Adicionar eventos de trace `upstream_started`/`upstream_done`.

## 2. Implementação + testes

- [x] 2.1 Encadear etapa de implementação após upstream aprovado (reuso do fluxo atual, mas dentro da fase 2).
- [x] 2.2 Rodar testes determinísticos e registrar `tests_started`/`tests_done`.
- [x] 2.3 Registrar `final_decision` e finalizar status (`done`/`failed`).

## 3. UI /lab

- [x] 3.1 Ajustar `/lab` para suportar ciclo de conversa upstream (exibir question e reenvio).

## 4. Testes e verificação

- [x] 4.1 Adicionar/ajustar testes cobrindo: missing → needs_user_input; aprovado → avança para fase 2.
- [x] 4.2 `openspec validate lab-two-phase-graph`.
- [x] 4.3 Rodar `./backend/.venv/bin/python -m pytest -q`.
