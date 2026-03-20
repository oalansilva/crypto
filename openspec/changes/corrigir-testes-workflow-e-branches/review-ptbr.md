# Revisão PO — `corrigir-testes-workflow-e-branches`

## Resumo
Manutenção crítica: 3 items bloqueando operações diárias.

## O que muda

1. **Testes de integração** — 6 testes falhando no `test_workflow_kanban_manual_backlog.py` serão corrigidos ou removidos.
2. **Branches stale** — 5 branches de feature já mergeadas serão deletadas (local + remote).
3. **test-results/** — `frontend/test-results/` será ignorado via .gitignore ou commitado — não pode continuar bloqueando o upstream guard.

## Critérios de aceite
- `pytest backend/tests/integration` passa (ou falhas documentadas)
- Nenhuma branch stale permanece
- Upstream guard não bloqueado

## Sem novo UI/UX
Esta change é manutenção pura — nenhum novo UI/UX.
