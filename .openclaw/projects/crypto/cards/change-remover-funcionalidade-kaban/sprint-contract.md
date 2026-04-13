# Contrato de homologacao

## Projeto
crypto

## Operational root
/root/.openclaw/workspace/crypto

## Escopo desta homologacao
remover funcionalidade kaban

## Evidencias consolidadas
- Diff removendo a rota `/kanban` de `frontend/src/App.tsx`.
- Diff removendo o item `Kanban` de `frontend/src/components/AppNav.tsx`.
- `rg -n "KanbanPage" frontend/src` sem imports remanescentes, apenas a definicao em `frontend/src/pages/KanbanPage.tsx`.
- App Kanban standalone acessivel em `http://127.0.0.1:5174` com `HTTP/1.1 200 OK` e `title>Kanban</title>`.
- Build do frontend concluido com sucesso.

## Decisao esperada
Aprovar para archive ou registrar blocker objetivo.

## Riscos conhecidos
- Ainda existem outras referencias a Kanban no frontend fora deste item claimado e elas precisam ser tratadas nos proximos work items.
